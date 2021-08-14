#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import time
import asyncio

import asyncpio


class DHT11(object):
    """
    The DHT11 class is a stripped version of the DHT22 sensor code by joan2937.
    You can find the initial implementation here:
    - https://github.com/srounet/pigpio/tree/master/EXAMPLES/Python/DHT22_AM2302_SENSOR

    example code:
    >>> pi = asyncpio.pi()
    >>> sensor = DHT11(pi, 4) # 4 is the data GPIO pin connected to your sensor
    >>> for response in sensor:
    ....    print("Temperature: {}".format(response['temperature']))
    ....    print("Humidity: {}".format(response['humidity']))
    """

    def __init__(self, pi, gpio):
        """
        pi (pigpio): an instance of pigpio
        gpio (int): gpio pin number
        """
        self.pi = pi
        self.gpio = gpio
        self.high_tick = 0
        self.bit = 40
        self.temperature = 0
        self.humidity = 0
        self.either_edge_cb = None

    @classmethod
    async def create(cls, pi, gpio):
        self = cls(pi, gpio)
        await self.setup()
        return self

    async def setup(self):
        """
        Clears the internal gpio pull-up/down resistor.
        Kills any watchdogs.
        """
        await self.pi.set_pull_up_down(self.gpio, asyncpio.PUD_OFF)
        await self.pi.set_watchdog(self.gpio, 0)
        await self.register_callbacks()

    async def register_callbacks(self):
        """
        Monitors RISING_EDGE changes using callback.
        """
        self.either_edge_cb = await self.pi.callback(
            self.gpio,
            asyncpio.EITHER_EDGE,
            self.either_edge_callback
        )

    async def either_edge_callback(self, gpio, level, tick):
        """
        Either Edge callbacks, called each time the gpio edge changes.
        Accumulate the 40 data bits from the dht11 sensor.
        """
        level_handlers = {
            asyncpio.FALLING_EDGE: self._edge_FALL,
            asyncpio.RISING_EDGE: self._edge_RISE,
            asyncpio.EITHER_EDGE: self._edge_EITHER
        }
        handler = level_handlers[level]
        diff = asyncpio.tickDiff(self.high_tick, tick)
        await handler(tick, diff)

    async def _edge_RISE(self, tick, diff):
        """
        Handle Rise signal.
        """
        val = 0
        if diff >= 50:
            val = 1
        if diff >= 200: # Bad bit?
            self.checksum = 256 # Force bad checksum

        if self.bit >= 40: # Message complete
            self.bit = 40
        elif self.bit >= 32: # In checksum byte
            self.checksum = (self.checksum << 1) + val
            if self.bit == 39:
                # 40th bit received
                await self.pi.set_watchdog(self.gpio, 0)
                total = self.humidity + self.temperature
                # is checksum ok ?
                if not (total & 255) == self.checksum:
                    raise
        elif 16 <= self.bit < 24: # in temperature byte
            self.temperature = (self.temperature << 1) + val
        elif 0 <= self.bit < 8: # in humidity byte
            self.humidity = (self.humidity << 1) + val
        else: # skip header bits
            pass
        self.bit += 1

    async def _edge_FALL(self, tick, diff):
        """
        Handle Fall signal.
        """
        self.high_tick = tick
        if diff <= 250000:
            return
        self.bit = -2
        self.checksum = 0
        self.temperature = 0
        self.humidity = 0

    async def _edge_EITHER(self, tick, diff):
        """
        Handle Either signal.
        """
        await self.pi.set_watchdog(self.gpio, 0)

    async def read(self):
        """
        Start reading over DHT11 sensor.
        """
        await self.pi.write(self.gpio, asyncpio.LOW)
        await asyncio.sleep(0.017) # 17 ms
        await self.pi.set_mode(self.gpio, asyncpio.INPUT)
        await self.pi.set_watchdog(self.gpio, 200)
        await asyncio.sleep(0.2)

    async def close(self):
        """
        Stop reading sensor, remove callbacks.
        """
        await self.pi.set_watchdog(self.gpio, 0)
        if self.either_edge_cb:
            await self.either_edge_cb.cancel()
            self.either_edge_cb = None

    def __aiter__(self):
        """
        Support the iterator protocol.
        """
        return self

    async def __anext__(self):
        """
        Call the read method and return temperature and humidity informations.
        """
        await self.read()
        response =  {
            'humidity': self.humidity,
            'temperature': self.temperature
        }
        return response


async def main():
    pi = asyncpio.pi()
    await pi.connect()
    sensor = await DHT11.create(pi, 4)
    async for d in sensor:
        print("temperature: {}".format(d['temperature']))
        print("humidity: {}".format(d['humidity']))
        asyncio.sleep(1)
    await sensor.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
