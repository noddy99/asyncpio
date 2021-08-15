#!/usr/bin/env python

# 2014-08-26 PCF8591.py

import asyncio
import curses

import asyncpio

# sudo pigpiod
# ./PCF8591.py

# Connect Pi 3V3 - VCC, Ground - Ground, SDA - SDA, SCL - SCL.

YL_40=0x48

async def main():
    pi = asyncpio.pi()
    await pi.connect() # Connect to local Pi.

    handle = await pi.i2c_open(1, YL_40, 0)

    stdscr = curses.initscr()

    curses.noecho()
    curses.cbreak()

    aout = 0

    stdscr.addstr(10, 0, "Brightness")
    stdscr.addstr(12, 0, "Temperature")
    stdscr.addstr(14, 0, "AOUT->AIN2")
    stdscr.addstr(16, 0, "Resistor")

    stdscr.nodelay(1)

    try:
        while True:

            for a in range(0,4):
                aout = aout + 1
                await pi.i2c_write_byte_data(handle, 0x40 | ((a+1) & 0x03), aout&0xFF)
                v = await pi.i2c_read_byte(handle)
                hashes = v / 4
                spaces = 64 - hashes
                stdscr.addstr(10+a*2, 12, str(v) + ' ')
                stdscr.addstr(10+a*2, 16, '#' * hashes + ' ' * spaces )

            stdscr.refresh()
            await asyncio.sleep(0.04)

            c = stdscr.getch()

            if c != curses.ERR:
                break

    except:
        pass

    curses.nocbreak()
    curses.echo()
    curses.endwin()

    await pi.i2c_close(handle)
    await pi.stop()

asyncio.run(main())

