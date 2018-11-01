# asyncpio

asyncpio is an asynchronous Python client for [pigpio](https://github.com/joan2937/pigpio),
which allows control of the Raspberry Pi's General Purpose Input Outputs (GPIO).

This is a port of pigpio's thread-based Python client to asyncio.

## Requirements

[pigpio](https://github.com/joan2937/pigpio) is a dependency: you must have the [pigpio](https://github.com/joan2937/pigpio) daemon, `pigpiod`.

## Documentation

See http://abyz.me.uk/rpi/pigpio/

## GPIO

ALL GPIO are identified by their Broadcom number.  See https://pinout.xyz.

There are 54 GPIO in total, arranged in two banks.

Bank 1 contains GPIO 0-31.  Bank 2 contains GPIO 32-54.

A user should only manipulate GPIO in bank 1.

There are at least three types of board:
* Type 1
    * 26 pin header (P1)
    * Hardware revision numbers of 2 and 3
    * User GPIO 0-1, 4, 7-11, 14-15, 17-18, 21-25
* Type 2
    * 26 pin header (P1) and an additional 8 pin header (P5)
    * Hardware revision numbers of 4, 5, 6, and 15
    * User GPIO 2-4, 7-11, 14-15, 17-18, 22-25, 27-31
* Type 3
    * 40 pin expansion header (J8)
    * Hardware revision numbers of 16 or greater
    * User GPIO 2-27 (0 and 1 are reserved)

It is safe to read all the GPIO. If you try to write a system GPIO or change
its mode you can crash the Pi or corrupt the data on the SD card.
