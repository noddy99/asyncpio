#!/usr/bin/env python

import asyncio
import curses
import atexit

import asyncpio

GPIOS=32

MODES=["INPUT", "OUTPUT", "ALT5", "ALT4", "ALT0", "ALT1", "ALT2", "ALT3"]

async def cleanup(pi):
   curses.nocbreak()
   curses.echo()
   curses.endwin()
   await pi.stop()

async def main():
   pi = asyncpio.pi()
   await pi.connect()

   stdscr = curses.initscr()
   curses.noecho()
   curses.cbreak()

   atexit.register(cleanup, pi)

   cb = []

   for g in range(GPIOS):
      cb.append(await pi.callback(g, asyncpio.EITHER_EDGE))

   # disable gpio 28 as the PCM clock is swamping the system

   await cb[28].cancel()

   stdscr.nodelay(1)

   stdscr.addstr(0, 23, "Status of gpios 0-31", curses.A_REVERSE)

   while True:

      for g in range(GPIOS):
         tally = cb[g].tally()
         mode = await pi.get_mode(g)

         col = (g // 11) * 25
         row = (g % 11) + 2

         stdscr.addstr(row, col, "{:2}".format(g), curses.A_BOLD)

         stdscr.addstr(
            "={} {:>6}: {:<10}".format(pi.read(g), MODES[mode], tally))

      stdscr.refresh()

      await asyncio.sleep(0.1)

      c = stdscr.getch()

      if c != curses.ERR:
         break

asyncio.run(main())
