"""Run the held-out model through actual chip pins, including every tile readback."""
import json
import os
from pathlib import Path
import cocotb
from test import Chip,START,DATA,READ,NOP,READY,BUSY,DONE

ROOT=Path(__file__).resolve().parents[1]

@cocotb.test()
async def digits_inference(dut):
    f=json.loads((ROOT/'ml/fixtures/digits_int4.json').read_text())
    c=Chip(dut);await c.reset()
    transactions=0
    async def multiply(a,w):
        nonlocal transactions
        n=len(w[0]);k=len(w)
        out=[[0]*n for _ in range(2)]
        for col in range(0,n,2):
            for off in range(0,k,16):
                length=min(16,k-off)
                before=c.cycles
                await c.edge(START,length-1)
                for t in range(off,off+length):
                    await c.edge(DATA,((a[1][t]&15)<<4)|(a[0][t]&15))
                    await c.edge(DATA,((w[t][col+1]&15)<<4)|(w[t][col]&15))
                await c.edge();await c.edge()
                assert c.status==DONE
                tile=await c.read()
                expected=[sum(a[r][t]*w[t][j] for t in range(off,off+length))
                          for r in range(2) for j in [col,col+1]]
                assert tile==expected
                assert c.cycles-before==2*length+11
                for r in range(2):
                    for j in range(2):out[r][col+j]+=tile[r*2+j]
                transactions+=1
        return out

    predictions=[]
    begin=c.cycles
    for batch in range(0,len(f['labels']),2):
        inputs=f['input_int4'][batch:batch+2]
        first=await multiply(inputs,f['weights1'])
        hidden=[[max(0,min(7,round(max(0,s*f['scale1'][j]+f['bias1'][j])/f['hidden_scale'])))
                 for j,s in enumerate(row)] for row in first]
        assert hidden==f['reference_hidden'][batch:batch+2]
        second=await multiply(hidden,f['weights2'])
        for row in second:
            logits=[s*f['scale2'][j]+f['bias2'][j] for j,s in enumerate(row)]
            predictions.append(max(range(10),key=logits.__getitem__))
    assert predictions==f['reference_predictions']
    correct=sum(a==b for a,b in zip(predictions,f['labels']))
    report={"test_images":len(predictions),"correct":correct,"accuracy":correct/len(predictions),
            "rtl_predictions_match_integer_model":True,"tile_transactions":transactions,
            "mismatched_tiles":0,"protocol_cycles":c.cycles-begin,
            "cycles_per_two_image_batch":(c.cycles-begin)/(len(predictions)//2),
            "host":"bias, rescaling, ReLU, requantization, tile partial-sum combination, argmax",
            "measurement":"RTL simulation; ideal synchronous host; excludes host processing and transport latency"}
    stage = 'gatelevel' if os.environ.get('GATES') == 'yes' else 'rtl'
    report['measurement'] = stage + ' simulation; ideal synchronous host; excludes host processing and transport latency'
    dest=ROOT/('reports/ml-'+stage+'.json');dest.write_text(json.dumps(report,indent=2)+'\n')
    output=ROOT/'test/output';output.mkdir(exist_ok=True)
    (output/('ml-'+stage+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    dut._log.info("ML result: %s",report)
