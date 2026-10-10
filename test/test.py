# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0
# Complete chip tests; uses only package pins, also valid for gate-level simulation.
import random
import cocotb
from cocotb.triggers import Timer

NOP, START, DATA, READ, ABORT = range(5)
READY, BUSY, DONE, ERROR = 0x10, 0x20, 0x40, 0x80

class Chip:
    def __init__(self, dut):
        self.d = dut
        self.cycles = 0

    async def edge(self, cmd=NOP, byte=0, ena=1):
        self.d.clk.value = 0
        self.d.uio_in.value = cmd
        self.d.ui_in.value = byte
        self.d.ena.value = ena
        await Timer(50, unit="ns")
        self.d.clk.value = 1
        await Timer(50, unit="ns")
        self.d.clk.value = 0
        self.cycles += 1
        assert int(self.d.uio_oe.value) == 0xf0
        assert int(self.d.uio_out.value) & 15 == 0

    @property
    def status(self): return int(self.d.uio_out.value)
    @property
    def byte(self): return int(self.d.uo_out.value)

    async def reset(self):
        self.d.rst_n.value = 0
        await self.edge(ena=0)
        self.d.rst_n.value = 1
        assert self.status == 0 and self.byte == 0

    async def read(self):
        result = []
        for _ in range(4):
            lo = self.byte
            await self.edge(READ)
            hi = self.byte
            await self.edge(READ)
            value = lo | (hi << 8)
            result.append(value - 65536 if value & 32768 else value)
        return result

    async def run(self, a, b, rng=None):
        k=len(b)
        expected=[sum(a[i][t]*b[t][j] for t in range(k)) for i in range(2) for j in range(2)]
        begin=self.cycles
        await self.edge(START,k-1)
        assert self.status == READY | BUSY and self.byte == 0
        for t in range(k):
            for byte in [((a[1][t]&15)<<4)|(a[0][t]&15), ((b[t][1]&15)<<4)|(b[t][0]&15)]:
                if rng:
                    for _ in range(rng.randrange(4)):
                        await self.edge()
                        assert self.status == READY | BUSY
                    if rng.randrange(2):
                        await self.edge(DATA,0xff,ena=0)
                        assert self.status == BUSY
                await self.edge(DATA,byte)
        assert self.status == BUSY and self.byte == 0
        await self.edge()
        assert self.status == BUSY
        await self.edge()
        assert self.status == DONE
        got=await self.read()
        assert got == expected, (a,b,got,expected)
        if not rng: assert self.cycles-begin == 2*k+11
        # Read pointer wraps, and result remains stable through idle clocks.
        first=self.byte
        for _ in range(3): await self.edge()
        assert self.status == DONE and self.byte == first
        return got

@cocotb.test()
async def complete_chip_arithmetic(dut):
    chip=Chip(dut);await chip.reset()
    # Every multiplier pair on all four PEs, through the real serial interface.
    for a in range(-8,8):
        for b in range(-8,8):
            await chip.run([[a],[a]],[[b,b]])
    rng=random.Random(20261010)
    for k in range(1,17):
        await chip.run([[-8]*k]*2,[[-8,-8]]*k)
        await chip.run([[7]*k]*2,[[7,-8]]*k)
        await chip.run([[0]*k]*2,[[7,-8]]*k)
        for _ in range(12):
            a=[[rng.randrange(-8,8) for _ in range(k)] for _ in range(2)]
            b=[[rng.randrange(-8,8) for _ in range(2)] for _ in range(k)]
            await chip.run(a,b,rng)
    await chip.run([[1,0],[0,1]],[[-8,7],[3,-2]])

@cocotb.test()
async def protocol_and_recovery(dut):
    c=Chip(dut);await c.reset()
    for cmd in [DATA,READ,5,6,7]:
        await c.edge(cmd)
        assert c.status == ERROR
        await c.edge(ABORT)
        assert c.status == 0
    await c.edge(START,0x10)
    assert c.status == ERROR
    await c.edge(START,0)
    assert c.status == READY|BUSY
    # Rejected commands cannot consume a byte or restart an active operation.
    await c.edge(DATA,0x78)
    for cmd in [START,READ,5]: await c.edge(cmd)
    assert c.status == READY|BUSY|ERROR
    await c.edge(DATA,0x3e)
    assert c.status == BUSY|ERROR
    # Disable while draining: no pipeline advancement, even for ABORT/START.
    for cmd in [ABORT,START,DATA,READ]:
        await c.edge(cmd,ena=0)
        assert c.status == BUSY|ERROR
    await c.edge(DATA) # illegal, but advances first drain step
    assert c.status == BUSY|ERROR
    await c.edge(READ) # illegal on final drain edge
    assert c.status == DONE|ERROR
    assert await c.read() == [16,-24,-14,21]
    old=c.byte
    await c.edge(START,0xf0) # invalid K must preserve results/pointer
    assert c.status == DONE|ERROR and c.byte==old
    await c.edge(READ,ena=0)
    assert c.byte==old
    assert await c.read() == [16,-24,-14,21]
    await c.run([[1],[2]],[[3,4]]) # accepted start clears old error
    # Abort and reset in idle, both load phases, both drain phases, and done.
    sequences=[[],[(START,0)],[(START,0),(DATA,0x21)],
               [(START,0),(DATA,0x21),(DATA,0x43)],
               [(START,0),(DATA,0x21),(DATA,0x43),(NOP,0)],
               [(START,0),(DATA,0x21),(DATA,0x43),(NOP,0),(NOP,0)]]
    for seq in sequences:
        for reset in [False,True]:
            await c.edge(ABORT)
            for cmd,byte in seq: await c.edge(cmd,byte)
            if reset: await c.reset()
            else: await c.edge(ABORT)
            assert c.status==0 and c.byte==0
            for _ in range(4): await c.edge()
            assert c.status==0 and c.byte==0
            await c.run([[-8],[7]],[[-2,3]])
