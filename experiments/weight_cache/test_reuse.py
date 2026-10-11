"""Pin-level experimental cache tests; run against RTL or the candidate netlist."""
import json, random
from pathlib import Path
import cocotb
from test import Chip, START, DATA, READ, ABORT, DONE, BUSY, READY, ERROR
REUSE=5

async def reuse(c,a,b,stall=False):
    before=c.cycles
    await c.edge(REUSE,15)
    assert c.status == READY|BUSY
    for k in range(16):
        if stall:
            await c.edge(DATA,0xff,ena=0)
            await c.edge()
        await c.edge(DATA,((a[1][k]&15)<<4)|(a[0][k]&15))
    await c.edge();await c.edge()
    assert c.status == DONE
    got=await c.read()
    expected=[sum(a[r][k]*b[k][j] for k in range(16)) for r in range(2) for j in range(2)]
    assert got==expected,(got,expected)
    if not stall:assert c.cycles-before==27

@cocotb.test()
async def cache_protocol(dut):
    c=Chip(dut);await c.reset();rng=random.Random(8128)
    def rand_a():return [[rng.randrange(-8,8) for _ in range(16)] for _ in range(2)]
    b=[[rng.randrange(-8,8),rng.randrange(-8,8)] for _ in range(16)]
    for epoch in range(8):
        await c.run(rand_a(),b)
        for n in range(5):await reuse(c,rand_a(),b,stall=n%2==1)
        # Invalid configuration preserves results and cache alignment.
        old=c.byte
        await c.edge(REUSE,14);assert c.status==DONE|ERROR and c.byte==old
        await reuse(c,rand_a(),b)
        await c.edge(REUSE,15,ena=0);assert c.status==DONE
    # Reset/abort at every partial rotation invalidates the cache.
    for k in range(17):
        for reset in [False,True]:
            await c.run(rand_a(),b)
            await c.edge(REUSE,15)
            for _ in range(k):await c.edge(DATA,0x78)
            if reset:await c.reset()
            else:await c.edge(ABORT)
            await c.edge(REUSE,15);assert c.status==ERROR
            await c.edge(ABORT)
    # A short normal load must invalidate a previously complete cache.
    await c.run(rand_a(),b)
    await c.run([[1],[2]],[[3,4]])
    await c.edge(REUSE,15);assert c.status==DONE|ERROR
    await c.edge(ABORT)
    # Invalid commands during reuse don't consume weights or A bytes.
    await c.run(rand_a(),b)
    await c.edge(REUSE,15)
    for k in range(16):
        await c.edge(READ);await c.edge(START,15);await c.edge(REUSE,15)
        await c.edge(DATA,0x21)
    await c.edge();await c.edge()
    assert c.status==DONE|ERROR
    assert await c.read()==[sum(v[j] for v in b)*r for r in [1,2] for j in range(2)]

@cocotb.test()
async def cached_digits(dut):
    root=Path(__file__).resolve().parents[2]
    f=json.loads((root/'ml/fixtures/digits_int4.json').read_text())
    c=Chip(dut);await c.reset();begin=c.cycles
    tiles=0;warm=0
    async def layer(inputs,w):
        nonlocal tiles,warm
        n=len(w[0]);out=[[0]*n for _ in inputs]
        for col in range(0,n,2):
            for off in range(0,len(w),16):
                b=[row[col:col+2] for row in w[off:off+16]]
                for batch in range(0,len(inputs),2):
                    a=[row[off:off+16] for row in inputs[batch:batch+2]]
                    before=c.cycles
                    await c.edge(START if batch==0 else REUSE,15)
                    for k in range(16):
                        await c.edge(DATA,((a[1][k]&15)<<4)|(a[0][k]&15))
                        if batch==0:await c.edge(DATA,((b[k][1]&15)<<4)|(b[k][0]&15))
                    await c.edge();await c.edge()
                    assert c.status==DONE
                    tile=await c.read()
                    assert tile==[sum(a[r][k]*b[k][j] for k in range(16)) for r in range(2) for j in range(2)]
                    assert c.cycles-before==(43 if batch==0 else 27)
                    for r in range(2):
                        for j in range(2):out[batch+r][col+j]+=tile[2*r+j]
                    tiles+=1;warm+=batch==0
        return out
    first=await layer(f['input_int4'],f['weights1'])
    hidden=[[max(0,min(7,round(max(0,s*f['scale1'][j]+f['bias1'][j])/f['hidden_scale']))) for j,s in enumerate(row)] for row in first]
    assert hidden==f['reference_hidden']
    second=await layer(hidden,f['weights2'])
    predictions=[]
    for row in second:
        logits=[s*f['scale2'][j]+f['bias2'][j] for j,s in enumerate(row)]
        predictions.append(max(range(10),key=logits.__getitem__))
    assert predictions==f['reference_predictions']
    assert tiles==6660 and warm==37 and c.cycles-begin==180412
    result=dict(images=360,correct=sum(p==t for p,t in zip(predictions,f['labels'])),tiles=tiles,
        mismatches=0,weight_load_transactions=warm,reuse_transactions=tiles-warm,
        protocol_cycles=c.cycles-begin,baseline_cycles=286380,
        scope='Full-dataset weight-stationary schedule; excludes host storage/work/transport; not single-image latency')
    dest=root/'build/cache-ml.json';dest.write_text(json.dumps(result,indent=2)+'\n')
    dut._log.info('CACHE ML: %s',result)
