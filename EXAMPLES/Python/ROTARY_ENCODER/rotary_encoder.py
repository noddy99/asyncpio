#!/usr/bin/env python

import asyncio

import asyncpio

class decoder:

   """Class to decode mechanical rotary encoder pulses."""

   def __init__(self, pi, gpioA, gpioB, callback):

      """
      Instantiate the class with the pi and gpios connected to
      rotary encoder contacts A and B.  The common contact
      should be connected to ground.  The callback is
      called when the rotary encoder is turned.  It takes
      one parameter which is +1 for clockwise and -1 for
      counterclockwise.

      EXAMPLE

      import time
      import asyncpio

      import rotary_encoder

      pos = 0

      def callback(way):

         global pos

         pos += way

         print("pos={}".format(pos))

      pi = asyncpio.pi()
      await pi.connect()

      decoder = rotary_encoder.decoder(pi, 7, 8, callback)
      await decoder.start()

      await asyncio.sleep(300)

      await decoder.cancel()

      await pi.stop()

      """

      self.pi = pi
      self.gpioA = gpioA
      self.gpioB = gpioB
      self.callback = callback

      self.levA = 0
      self.levB = 0

      self.lastGpio = None

   async def start(self):
      await self.pi.set_mode(self.gpioA, asyncpio.INPUT)
      await self.pi.set_mode(self.gpioB, asyncpio.INPUT)

      await self.pi.set_pull_up_down(self.gpioA, asyncpio.PUD_UP)
      await self.pi.set_pull_up_down(self.gpioB, asyncpio.PUD_UP)

      self.cbA = await self.pi.callback(self.gpioA, asyncpio.EITHER_EDGE, self._pulse)
      self.cbB = await self.pi.callback(self.gpioB, asyncpio.EITHER_EDGE, self._pulse)

   def _pulse(self, gpio, level, tick):

      """
      Decode the rotary encoder pulse.

                   +---------+         +---------+      0
                   |         |         |         |
         A         |         |         |         |
                   |         |         |         |
         +---------+         +---------+         +----- 1

             +---------+         +---------+            0
             |         |         |         |
         B   |         |         |         |
             |         |         |         |
         ----+         +---------+         +---------+  1
      """

      if gpio == self.gpioA:
         self.levA = level
      else:
         self.levB = level;

      if gpio != self.lastGpio: # debounce
         self.lastGpio = gpio

         if   gpio == self.gpioA and level == 1:
            if self.levB == 1:
               self.callback(1)
         elif gpio == self.gpioB and level == 1:
            if self.levA == 1:
               self.callback(-1)

   async def cancel(self):

      """
      Cancel the rotary encoder decoder.
      """

      await self.cbA.cancel()
      await self.cbB.cancel()

async def main():
   pos = 0

   def callback(way):

      nonlocal pos

      pos += way

      print("pos={}".format(pos))

   pi = asyncpio.pi()
   await pi.connect()

   decoder = decoder(pi, 7, 8, callback)
   await decoder.start()

   await asyncio.sleep(300)

   await decoder.cancel()

   await pi.stop()

if __name__ == "__main__":
   asyncio.run(main())
