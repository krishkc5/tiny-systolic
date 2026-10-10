# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0
# Adapted for TinySystolic MAC bring-up, 2026.
import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_mac(dut):
    # 10 MHz target; inspect outputs well after the clock for gate-level testing.
    dut.clk.value = 0
    dut.rst_n.value = 0
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0

    async def tick():
        dut.clk.value = 0
        await Timer(50, unit="ns")
        dut.clk.value = 1
        await Timer(50, unit="ns")
        dut.clk.value = 0

    async def check(expected):
        expected &= 0xffff
        control = int(dut.uio_in.value) & ~4
        dut.uio_in.value = control
        await Timer(50, unit="ns")
        assert int(dut.uo_out.value) == expected & 255
        dut.uio_in.value = control | 4
        await Timer(50, unit="ns")
        assert int(dut.uo_out.value) == expected >> 8
        assert int(dut.uio_out.value) == 0
        assert int(dut.uio_oe.value) == 0

    await tick()
    await check(0)
    dut.rst_n.value = 1
    for a in range(-8, 8):
        for b in range(-8, 8):
            dut.uio_in.value = 1
            await tick()
            dut.ui_in.value = ((b & 15) << 4) | (a & 15)
            dut.uio_in.value = 2
            await tick()
            await check(a * b)
    dut.uio_in.value = 1
    await tick()
    for i in range(16):
        dut.ui_in.value = 0x88
        dut.uio_in.value = 2
        await tick()
        await check((i + 1) * 64)
    dut.uio_in.value = 0
    await tick()
    await check(1024)
    dut.ena.value = 0
    dut.uio_in.value = 2
    await tick()
    await check(1024)
    dut.ena.value = 1
    dut.uio_in.value = 3
    await tick()
    await check(0)
    dut.uio_in.value = 2
    await tick()
    await check(64)
    dut.rst_n.value = 0
    await tick()
    await check(0)
