#!/usr/bin/env python

#*** WARNING ************************************************
#*                                                          *
#* All the tests make extensive use of gpio 25 (pin 22).    *
#* Ensure that either nothing or just a LED is connected to *
#* gpio 25 before running any of the tests.                 *
#*                                                          *
#* Some tests are statistical in nature and so may on       *
#* occasion fail.  Repeated failures on the same test or    *
#* many failures in a group of tests indicate a problem.    *
#************************************************************

import asyncio
import sys
import struct

import asyncpio

GPIO=25

def STRCMP(r, s):

   if sys.hexversion > 0x03000000:

      if type(r) == type(""):
         r = bytearray(r, 'latin-1')

      if type(s) == type(""):
         s = bytearray(s, 'latin-1')

   if r != s:
      print(r, s)
      return 0

   else:
      return 1

def CHECK(t, st, got, expect, pc, desc):
   if got >= (((1E2-pc)*expect)/1E2) and got <= (((1E2+pc)*expect)/1E2):
      print("TEST {:2d}.{:<2d} PASS ({}: {:d})".format(t, st, desc, expect))
   else:
      print("TEST {:2d}.{:<2d} FAILED got {:d} ({}: {:d})".
         format(t, st, got, desc, expect))

async def t0():

   print("\nTesting asyncpio Python module {}".format(asyncpio.VERSION))

   print("Python {}".format(sys.version.replace("\n", " ")))

   print("asyncpio version {}.".format(await pi.get_pigpio_version()))

   print("Hardware revision {}.".format(await pi.get_hardware_revision()))

async def t1():

   print("Mode/PUD/read/write tests.")

   await pi.set_mode(GPIO, asyncpio.INPUT)
   v = await pi.get_mode(GPIO)
   CHECK(1, 1, v, 0, 0, "set mode, get mode")

   await pi.set_pull_up_down(GPIO, asyncpio.PUD_UP)
   v = await pi.read(GPIO)
   CHECK(1, 2, v, 1, 0, "set pull up down, read")

   await pi.set_pull_up_down(GPIO, asyncpio.PUD_DOWN)
   v = await pi.read(GPIO)
   CHECK(1, 3, v, 0, 0, "set pull up down, read")

   await pi.write(GPIO, asyncpio.LOW)
   v = await pi.get_mode(GPIO)
   CHECK(1, 4, v, 1, 0, "write, get mode")

   v = await pi.read(GPIO)
   CHECK(1, 5, v, 0, 0, "read")

   await pi.write(GPIO, asyncpio.HIGH)
   v = await pi.read(GPIO)
   CHECK(1, 6, v, 1, 0, "write, read")

t2_count=0

def t2cbf(gpio, level, tick):
   global t2_count
   t2_count += 1

async def t2():

   global t2_count

   print("PWM dutycycle/range/frequency tests.")

   await pi.set_PWM_range(GPIO, 255)
   await pi.set_PWM_frequency(GPIO,0)
   f = await pi.get_PWM_frequency(GPIO)
   CHECK(2, 1, f, 10, 0, "set PWM range, set/get PWM frequency")

   t2cb = await pi.callback(GPIO, asyncpio.EITHER_EDGE, t2cbf)

   await pi.set_PWM_dutycycle(GPIO, 0)
   dc = await pi.get_PWM_dutycycle(GPIO)
   CHECK(2, 2, dc, 0, 0, "get PWM dutycycle")

   await asyncio.sleep(0.5) # allow old notifications to flush
   oc = t2_count
   await asyncio.sleep(2)
   f = t2_count - oc
   CHECK(2, 3, f, 0, 0, "set PWM dutycycle, callback")

   await pi.set_PWM_dutycycle(GPIO, 128)
   dc = await pi.get_PWM_dutycycle(GPIO)
   CHECK(2, 4, dc, 128, 0, "get PWM dutycycle")

   await asyncio.sleep(1)
   oc = t2_count
   await asyncio.sleep(2)
   f = t2_count - oc
   CHECK(2, 5, f, 40, 10, "set PWM dutycycle, callback")

   await pi.set_PWM_frequency(GPIO,100)
   f = await pi.get_PWM_frequency(GPIO)
   CHECK(2, 6, f, 100, 0, "set/get PWM frequency")

   await asyncio.sleep(1)
   oc = t2_count
   await asyncio.sleep(2)
   f = t2_count - oc
   CHECK(2, 7, f, 400, 5, "callback")

   await pi.set_PWM_frequency(GPIO,1000)
   f = await pi.get_PWM_frequency(GPIO)
   CHECK(2, 8, f, 1000, 0, "set/get PWM frequency")

   await asyncio.sleep(1)
   oc = t2_count
   await asyncio.sleep(2)
   f = t2_count - oc
   CHECK(2, 9, f, 4000, 5, "callback")

   r = await pi.get_PWM_range(GPIO)
   CHECK(2, 10, r, 255, 0, "get PWM range")

   rr = await pi.get_PWM_real_range(GPIO)
   CHECK(2, 11, rr, 200, 0, "get PWM real range")

   await pi.set_PWM_range(GPIO, 2000)
   r = await pi.get_PWM_range(GPIO)
   CHECK(2, 12, r, 2000, 0, "set/get PWM range")

   rr = await pi.get_PWM_real_range(GPIO)
   CHECK(2, 13, rr, 200, 0, "get PWM real range")

   await pi.set_PWM_dutycycle(GPIO, 0)

   await t2cb.cancel()

t3_reset=True
t3_count=0
t3_tick=0
t3_on=0.0
t3_off=0.0

def t3cbf(gpio, level, tick):
   global t3_reset, t3_count, t3_tick, t3_on, t3_off

   if t3_reset:
      t3_count = 0
      t3_on = 0.0
      t3_off = 0.0
      t3_reset = False
   else:
      td = asyncpio.tickDiff(t3_tick, tick)

      if level == 0:
         t3_on += td
      else:
         t3_off += td

   t3_count += 1
   t3_tick = tick

async def t3():

   global t3_reset, t3_count, t3_on, t3_off

   pw=[500.0, 1500.0, 2500.0]
   dc=[0.2, 0.4, 0.6, 0.8]

   print("PWM/Servo pulse accuracy tests.")

   t3cb = await pi.callback(GPIO, asyncpio.EITHER_EDGE, t3cbf)

   t = 0
   for x in pw:
      t += 1
      await pi.set_servo_pulsewidth(GPIO, x)
      v = await pi.get_servo_pulsewidth(GPIO)
      CHECK(3, t, v, int(x), 0, "get servo pulsewidth")

      t += 1
      await asyncio.sleep(1)
      t3_reset = True
      await asyncio.sleep(4)
      c = t3_count
      on = t3_on
      off = t3_off
      CHECK(3, t, int((1E3*(on+off))/on), int(2E7/x), 1, "set servo pulsewidth")


   await pi.set_servo_pulsewidth(GPIO, 0)
   await pi.set_PWM_frequency(GPIO, 1000)
   f = await pi.get_PWM_frequency(GPIO)
   CHECK(3, 7, f, 1000, 0, "set/get PWM frequency")

   rr = await pi.set_PWM_range(GPIO, 100)
   CHECK(3, 8, rr, 200, 0, "set PWM range")

   t = 8
   for x in dc:
      t += 1
      await pi.set_PWM_dutycycle(GPIO, x*100)
      v = await pi.get_PWM_dutycycle(GPIO)
      CHECK(3, t, v, int(x*100), 0, "get PWM dutycycle")

      t += 1
      await asyncio.sleep(1)
      t3_reset = True
      await asyncio.sleep(2)
      c = t3_count
      on = t3_on
      off = t3_off
      CHECK(3, t, int((1E3*on)/(on+off)), int(1E3*x), 1, "set PWM dutycycle")

   await pi.set_PWM_dutycycle(GPIO, 0)

   t3cb.cancel()

async def t4():

   print("Pipe notification tests.")

   await pi.set_PWM_frequency(GPIO, 0)
   await pi.set_PWM_dutycycle(GPIO, 0)
   await pi.set_PWM_range(GPIO, 100)

   h = await pi.notify_open()
   e = await pi.notify_begin(h, (1<<GPIO))
   CHECK(4, 1, e, 0, 0, "notify open/begin")

   await asyncio.sleep(1)

   try:
      f = open("/dev/pigpio"+ str(h), "rb")
   except IOError:
      f = None

   await pi.set_PWM_dutycycle(GPIO, 50)
   await asyncio.sleep(4)
   await pi.set_PWM_dutycycle(GPIO, 0)

   e = await pi.notify_pause(h)
   CHECK(4, 2, e, 0, 0, "notify pause")

   e = await pi.notify_close(h)
   CHECK(4, 3, e, 0, 0, "notify close")

   if f is not None:

      n = 0
      s = 0

      seq_ok = 1
      toggle_ok = 1

      while True:

         chunk = f.read(12)

         if len(chunk) == 12:

            S, fl, t, v = struct.unpack('HHII', chunk)
            if s != S:
               seq_ok = 0

            L = v & (1<<GPIO)

            if n:
               if l != L:
                  toggle_ok = 0

            if L:
               l = 0
            else:
               l = (1<<GPIO)

            s += 1
            n += 1

         else:
            break

      f.close()

      CHECK(4, 4, seq_ok, 1, 0, "sequence numbers ok")
      CHECK(4, 5, toggle_ok, 1, 0, "gpio toggled ok")
      CHECK(4, 6, n, 80, 10, "number of notifications")

   else:

      CHECK(4, 4, 0, 0, 0, "NOT APPLICABLE")
      CHECK(4, 5, 0, 0, 0, "NOT APPLICABLE")
      CHECK(4, 6, 0, 0, 0, "NOT APPLICABLE")

t5_count = 0

def t5cbf(gpio, level, tick):
   global t5_count
   t5_count += 1

async def t5():
   global t5_count

   BAUD=4800

   TEXT="""
Now is the winter of our discontent
Made glorious summer by this sun of York;
And all the clouds that lour'd upon our house
In the deep bosom of the ocean buried.
Now are our brows bound with victorious wreaths;
Our bruised arms hung up for monuments;
Our stern alarums changed to merry meetings,
Our dreadful marches to delightful measures.
Grim-visaged war hath smooth'd his wrinkled front;
And now, instead of mounting barded steeds
To fright the souls of fearful adversaries,
He capers nimbly in a lady's chamber
To the lascivious pleasing of a lute.
"""

   print("Waveforms & bit bang serial read/write tests.")

   t5cb = await pi.callback(GPIO, asyncpio.FALLING_EDGE, t5cbf)

   await pi.set_mode(GPIO, asyncpio.OUTPUT)

   e = await pi.wave_clear()
   CHECK(5, 1, e, 0, 0, "callback, set mode, wave clear")

   wf = []

   wf.append(asyncpio.pulse(1<<GPIO, 0,  10000))
   wf.append(asyncpio.pulse(0, 1<<GPIO,  30000))
   wf.append(asyncpio.pulse(1<<GPIO, 0,  60000))
   wf.append(asyncpio.pulse(0, 1<<GPIO, 100000))

   e = await pi.wave_add_generic(wf)
   CHECK(5, 2, e, 4, 0, "pulse, wave add generic")

   wid = await pi.wave_create()
   e = await pi.wave_send_repeat(wid)
   if e < 14:
      CHECK(5, 3, e, 9, 0, "wave send repeat")
   else:
      CHECK(5, 3, e, 19, 0, "wave send repeat")

   oc = t5_count
   await asyncio.sleep(5)
   c = t5_count - oc
   CHECK(5, 4, c, 50, 1, "callback")

   e = await pi.wave_tx_stop()
   CHECK(5, 5, e, 0, 0, "wave tx stop")

   e = await pi.bb_serial_read_open(GPIO, BAUD)
   CHECK(5, 6, e, 0, 0, "serial read open")

   await pi.wave_clear()
   e = await pi.wave_add_serial(GPIO, BAUD, TEXT, 5000000)
   CHECK(5, 7, e, 3405, 0, "wave clear, wave add serial")

   wid = await pi.wave_create()
   e = await pi.wave_send_once(wid)
   if e < 6964:
      CHECK(5, 8, e, 6811, 0, "wave send once")
   else:
      CHECK(5, 8, e, 7116, 0, "wave send once")

   oc = t5_count
   await asyncio.sleep(3)
   c = t5_count - oc
   CHECK(5, 9, c, 0, 0, "callback")

   oc = t5_count
   while await pi.wave_tx_busy():
      await asyncio.sleep(0.2)
   await asyncio.sleep(0.2)
   c = t5_count - oc
   CHECK(5, 10, c, 1702, 0, "wave tx busy, callback")

   c, text = await pi.bb_serial_read(GPIO)
   CHECK(5, 11, STRCMP(text, TEXT), True, 0, "wave tx busy, serial read");

   e = await pi.bb_serial_read_close(GPIO)
   CHECK(5, 12, e, 0, 0, "serial read close")

   c = await pi.wave_get_micros()
   CHECK(5, 13, c, 6158148, 0, "wave get micros")

   CHECK(5, 14, 0, 0, 0, "NOT APPLICABLE")

   c = await pi.wave_get_max_micros()
   CHECK(5, 15, c, 1800000000, 0, "wave get max micros")

   c = await pi.wave_get_pulses()
   CHECK(5, 16, c, 3405, 0, "wave get pulses")

   CHECK(5, 17, 0, 0, 0, "NOT APPLICABLE")

   c = await pi.wave_get_max_pulses()
   CHECK(5, 18, c, 12000, 0, "wave get max pulses")

   c = await pi.wave_get_cbs()
   if c < 6963:
      CHECK(5, 19, c, 6810, 0, "wave get cbs")
   else:
      CHECK(5, 19, c, 7115, 0, "wave get cbs")

   CHECK(5, 20, 0, 0, 0, "NOT APPLICABLE")

   c = await pi.wave_get_max_cbs()
   CHECK(5, 21, c, 25016, 0, "wave get max cbs")

   e = await pi.wave_clear()
   CHECK(5, 22, e, 0, 0, "wave clear")

   e = await pi.wave_add_generic(wf)
   CHECK(5, 23, e, 4, 0, "pulse, wave add generic")

   w1 = await pi.wave_create()
   CHECK(5, 24, w1, 0, 0, "wave create")

   e = await pi.wave_send_repeat(w1)
   if e < 14:
      CHECK(5, 25, e, 9, 0, "wave send repeat")
   else:
      CHECK(5, 25, e, 19, 0, "wave send repeat")

   oc = t5_count
   await asyncio.sleep(5)
   c = t5_count - oc
   CHECK(5, 26, c, 50, 1, "callback")

   e = await pi.wave_tx_stop()
   CHECK(5, 27, e, 0, 0, "wave tx stop")

   e = await pi.wave_add_serial(GPIO, BAUD, TEXT, 5000000)
   CHECK(5, 28, e, 3405, 0, "wave add serial")

   w2 = await pi.wave_create()
   CHECK(5, 29, w2, 1, 0, "wave create")

   e = await pi.wave_send_once(w2)
   if e < 6964:
      CHECK(5, 30, e, 6811, 0, "wave send once")
   else:
      CHECK(5, 30, e, 7116, 0, "wave send once")

   oc = t5_count
   await asyncio.sleep(3)
   c = t5_count - oc
   CHECK(5, 31, c, 0, 0, "callback")

   oc = t5_count
   while await pi.wave_tx_busy():
      await asyncio.sleep(0.2)
   await asyncio.sleep(0.2)
   c = t5_count - oc
   CHECK(5, 32, c, 1702, 0, "wave tx busy, callback")

   e = await pi.wave_delete(0)
   CHECK(5, 33, e, 0, 0, "wave delete")

   # wave_create_and_pad tests
   t5cb = await pi.callback(GPIO, asyncpio.FALLING_EDGE, t5cbf)
   await pi.wave_clear()

   await pi.wave_add_generic([asyncpio.pulse(1<<GPIO, 0,  10000),
                        asyncpio.pulse(0, 1<<GPIO,  30000)])
   wid = await pi.wave_create_and_pad(50)
   CHECK(5, 34, wid, 0, 0, "wave create and pad, wid==")

   await pi.wave_add_generic([asyncpio.pulse(1<<GPIO, 0,  10000),
                        asyncpio.pulse(0, 1<<GPIO,  30000),
                        asyncpio.pulse(1<<GPIO, 0,  60000),
                        asyncpio.pulse(0, 1<<GPIO, 100000)])
   wid = await pi.wave_create_and_pad(50)
   CHECK(5, 35, wid, 1, 0, "wave create and pad, wid==")

   c = await pi.wave_delete(0);
   CHECK(5, 36, c, 0, 0, "delete wid==0 success");

   await pi.wave_add_generic([asyncpio.pulse(1<<GPIO, 0,  10000),
                        asyncpio.pulse(0, 1<<GPIO,  30000),
                        asyncpio.pulse(1<<GPIO, 0,  60000),
                        asyncpio.pulse(0, 1<<GPIO, 100000),
                        asyncpio.pulse(1<<GPIO, 0,  60000),
                        asyncpio.pulse(0, 1<<GPIO, 100000)])
   asyncpio.exceptions = False
   c = await pi.wave_create()
   CHECK(5, 37, c, -67, 0, "No more CBs using wave create")
   asyncpio.exceptions = True

   wid = await pi.wave_create_and_pad(50)
   CHECK(5, 38, wid, 0, 0, "wave create pad, count==3, wid==")

   t5_count = 0;
   e = await pi.wave_chain([1,0])
   CHECK(5, 39, e,  0, 0, "wave chain [1,0]")
   while await pi.wave_tx_busy():
      await asyncio.sleep(0.2)
   CHECK(5, 40, t5_count, 10, 1, "callback count==")


   t5cb.cancel()

t6_count=0
t6_on=0
t6_on_tick=None

def t6cbf(gpio, level, tick):
   global t6_count, t6_on, t6_on_tick
   if level == 1:
      t6_on_tick = tick
      t6_count += 1
   else:
      if t6_on_tick is not None:
         t6_on += asyncpio.tickDiff(t6_on_tick, tick)

async def t6():
   global t6_count, t6_on

   print("Trigger tests.")

   await pi.write(GPIO, asyncpio.LOW)

   tp = 0

   t6cb = await pi.callback(GPIO, asyncpio.EITHER_EDGE, t6cbf)

   for t in range(5):
      await asyncio.sleep(0.1)
      p = 10 + (t*10)
      tp += p;
      await pi.gpio_trigger(GPIO, p, 1)

   await asyncio.sleep(0.5)

   CHECK(6, 1, t6_count, 5, 0, "gpio trigger count")

   CHECK(6, 2, t6_on, tp, 25, "gpio trigger pulse length")

   t6cb.cancel()

t7_count=0

def t7cbf(gpio, level, tick):
   global t7_count
   if level == asyncpio.TIMEOUT:
      t7_count += 1

async def t7():
   global t7_count

   print("Watchdog tests.")

   # type of edge shouldn't matter for watchdogs
   t7cb = await pi.callback(GPIO, asyncpio.FALLING_EDGE, t7cbf)

   await pi.set_watchdog(GPIO, 50) # 50 ms, 20 per second
   await asyncio.sleep(0.5)
   oc = t7_count
   await asyncio.sleep(2)
   c = t7_count - oc
   CHECK(7, 1, c, 39, 5, "set watchdog on count")

   await pi.set_watchdog(GPIO, 0) # 0 switches watchdog off
   await asyncio.sleep(0.5)
   oc = t7_count
   await asyncio.sleep(2)
   c = t7_count - oc
   CHECK(7, 2, c, 0, 1, "set watchdog off count")

   t7cb.cancel()

async def t8():
   print("Bank read/write tests.")

   await pi.write(GPIO, 0)
   v = await pi.read_bank_1() & (1<<GPIO)
   CHECK(8, 1, v, 0, 0, "read bank 1")

   await pi.write(GPIO, 1)
   v = await pi.read_bank_1() & (1<<GPIO)
   CHECK(8, 2, v, (1<<GPIO), 0, "read bank 1")

   await pi.clear_bank_1(1<<GPIO)
   v = await pi.read(GPIO)
   CHECK(8, 3, v, 0, 0, "clear bank 1")

   await pi.set_bank_1(1<<GPIO)
   v = await pi.read(GPIO)
   CHECK(8, 4, v, 1, 0, "set bank 1")

   v = await pi.read_bank_2()

   if v:
      v = 0
   else:
      v = 1

   CHECK(8, 5, v, 0, 0, "read bank 2")

   v = await pi.clear_bank_2(0)
   CHECK(8, 6, v, 0, 0, "clear bank 2")

   asyncpio.exceptions = False
   v = await pi.clear_bank_2(0xffffff)
   asyncpio.exceptions = True
   CHECK(8, 7, v, asyncpio.PI_SOME_PERMITTED, 0, "clear bank 2")

   v = await pi.set_bank_2(0)
   CHECK(8, 8, v, 0, 0, "set bank 2")

   asyncpio.exceptions = False
   v = await pi.set_bank_2(0xffffff)
   asyncpio.exceptions = True
   CHECK(8, 9, v, asyncpio.PI_SOME_PERMITTED, 0, "set bank 2")

async def t9waitNotHalted(s):
   for check in range(10):
      await asyncio.sleep(0.1)
      e, p = await pi.script_status(s)
      if e != asyncpio.PI_SCRIPT_HALTED:
         return

async def t9():
   print("Script store/run/status/stop/delete tests.")

   await pi.write(GPIO, 0) # need known state

   # 100 loops per second
   # p0 number of loops
   # p1 GPIO
   script="""
   ld p9 p0
   tag 0
   w p1 1
   mils 5
   w p1 0
   mils 5
   dcr p9
   jp 0"""

   t9cb = await pi.callback(GPIO)

   old_exceptions = asyncpio.exceptions

   asyncpio.exceptions = False

   s = await pi.store_script(script)

   # Ensure the script has finished initing.
   while True:
      e, p = await pi.script_status(s)
      if e != asyncpio.PI_SCRIPT_INITING:
         break
      await asyncio.sleep(0.1)

   oc = t9cb.tally()
   await pi.run_script(s, [99, GPIO])

   t9waitNotHalted(s)

   while True:
      e, p = await pi.script_status(s)
      if e != asyncpio.PI_SCRIPT_RUNNING:
         break
      await asyncio.sleep(0.1)
   await asyncio.sleep(0.2)
   c = t9cb.tally() - oc
   CHECK(9, 1, c, 100, 0, "store/run script")

   oc = t9cb.tally()
   await pi.run_script(s, [200, GPIO])

   t9waitNotHalted(s)

   while True:
      e, p = await pi.script_status(s)
      if e != asyncpio.PI_SCRIPT_RUNNING:
         break
      await asyncio.sleep(0.1)
   await asyncio.sleep(0.2)
   c = t9cb.tally() - oc
   CHECK(9, 2, c, 201, 0, "run script/script status")

   oc = t9cb.tally()
   await pi.run_script(s, [2000, GPIO])

   t9waitNotHalted(s)

   while True:
      e, p = await pi.script_status(s)
      if e != asyncpio.PI_SCRIPT_RUNNING:
         break
      if p[9] < 1900:
         await pi.stop_script(s)
      await asyncio.sleep(0.1)
   await asyncio.sleep(0.2)
   c = t9cb.tally() - oc
   CHECK(9, 3, c, 110, 20, "run/stop script/script status")

   e = await pi.delete_script(s)
   CHECK(9, 4, e, 0, 0, "delete script")

   t9cb.cancel()

   asyncpio.exceptions = old_exceptions

async def ta():
   print("Serial link tests.")

   # this test needs RXD and TXD to be connected

   h = await pi.serial_open("/dev/ttyAMA0", 57600)
   CHECK(10, 1, h>=0, 1, 0, "serial open")

   (b, s) = await pi.serial_read(h, 1000) # flush buffer

   b = await pi.serial_data_available(h)
   CHECK(10, 2, b, 0, 0, "serial data available")

   TEXT = """
To be, or not to be, that is the question-
Whether 'tis Nobler in the mind to suffer
The Slings and Arrows of outrageous Fortune,
Or to take Arms against a Sea of troubles,
"""
   e = await pi.serial_write(h, TEXT)
   CHECK(10, 3, e, 0, 0, "serial write")

   e = await pi.serial_write_byte(h, 0xAA)
   e = await pi.serial_write_byte(h, 0x55)
   e = await pi.serial_write_byte(h, 0x00)
   e = await pi.serial_write_byte(h, 0xFF)

   CHECK(10, 4, e, 0, 0, "serial write byte")

   await asyncio.sleep(0.1) # allow time for transmission

   b = await pi.serial_data_available(h)
   CHECK(10, 5, b, len(TEXT)+4, 0, "serial data available")

   (b, text) = await pi.serial_read(h, len(TEXT))
   CHECK(10, 6, b, len(TEXT), 0, "serial read")
   CHECK(10, 7, STRCMP(text, TEXT), True, 0, "serial read")

   b = await pi.serial_read_byte(h)
   CHECK(10, 8, b, 0xAA, 0, "serial read byte")

   b = await pi.serial_read_byte(h)
   CHECK(10, 9, b, 0x55, 0, "serial read byte")

   b = await pi.serial_read_byte(h)
   CHECK(10, 10, b, 0x00, 0, "serial read byte")

   b = await pi.serial_read_byte(h)
   CHECK(10, 11, b, 0xFF, 0, "serial read byte")

   b = await pi.serial_data_available(h)
   CHECK(10, 12, b, 0, 0, "serial data available")

   e = await pi.serial_close(h)
   CHECK(10, 13, e, 0, 0, "serial close")

async def tb():
   print("SMBus / I2C tests.")

   # this test requires an ADXL345 on I2C bus 1 addr 0x53

   h = await pi.i2c_open(1, 0x53)
   CHECK(11, 1, h>=0, 1, 0, "i2c open")

   e = await pi.i2c_write_device(h, "\x00") # move to known register
   CHECK(11, 2, e, 0, 0, "i2c write device")

   (b, d)  = await pi.i2c_read_device(h, 1)
   CHECK(11, 3, b, 1, 0, "i2c read device")
   CHECK(11, 4, ord(d), 0xE5, 0, "i2c read device")

   b = await pi.i2c_read_byte(h)
   CHECK(11, 5, b, 0xE5, 0, "i2c read byte")

   b = await pi.i2c_read_byte_data(h, 0)
   CHECK(11, 6, b, 0xE5, 0, "i2c read byte data")

   b = await pi.i2c_read_byte_data(h, 48)
   CHECK(11, 7, b, 2, 0, "i2c read byte data")

   exp = b"[aB\x08cD\xAAgHj\xFD]"

   e = await pi.i2c_write_device(h, b'\x1D'+ exp)
   CHECK(11, 8, e, 0, 0, "i2c write device")

   e = await pi.i2c_write_device(h, '\x1D')
   (b, d)  = await pi.i2c_read_device(h, 12)
   CHECK(11, 9, b, 12, 0, "i2c read device")
   CHECK(11, 10, STRCMP(d, exp), True, 0, "i2c read device")

   e = await pi.i2c_write_byte_data(h, 0x1d, 0xAA)
   CHECK(11, 11, e, 0, 0, "i2c write byte data")

   b = await pi.i2c_read_byte_data(h, 0x1d)
   CHECK(11, 12, b, 0xAA, 0, "i2c read byte data")

   e = await pi.i2c_write_byte_data(h, 0x1d, 0x55)
   CHECK(11, 13, e, 0, 0, "i2c write byte data")

   b = await pi.i2c_read_byte_data(h, 0x1d)
   CHECK(11, 14, b, 0x55, 0, "i2c read byte data")

   exp  =  "[1234567890#]"

   e = await pi.i2c_write_block_data(h, 0x1C, exp)
   CHECK(11, 15, e, 0, 0, "i2c write block data")

   e = await pi.i2c_write_device(h, '\x1D')
   (b, d)  = await pi.i2c_read_device(h, 13)
   CHECK(11, 16, b, 13, 0, "i2c read device")
   CHECK(11, 17, STRCMP(d, exp), True, 0, "i2c read device")

   (b, d)  = await pi.i2c_read_i2c_block_data(h, 0x1D, 13)
   CHECK(11, 18, b, 13, 0, "i2c read i2c block data")
   CHECK(11, 19, STRCMP(d, exp), True, 0, "i2c read i2c block data")

   expl = [0x01, 0x05, 0x06, 0x07, 0x09, 0x1B, 0x99, 0xAA, 0xBB, 0xCC]
   exp = "\x01\x05\x06\x07\x09\x1B\x99\xAA\xBB\xCC"

   e = await pi.i2c_write_i2c_block_data(h, 0x1D, expl)
   CHECK(11, 20, e, 0, 0, "i2c write i2c block data")

   (b, d)  = await pi.i2c_read_i2c_block_data(h, 0x1D, 10)
   CHECK(11, 21, b, 10, 0, "i2c read i2c block data")
   CHECK(11, 22, STRCMP(d, exp), True, 0, "i2c read i2c block data")

   e = await pi.i2c_close(h)
   CHECK(11, 23, e, 0, 0, "i2c close")

async def tca(b, d):
   if b == 3:
      c1 = d[1] & 0x0F
      c2 = d[2]
      await asyncio.sleep(1.0)
      print((c1*256)+c2)

async def tc():
   print("SPI tests.")

   # this test requires a MCP3202 on SPI channel 1

   h = await pi.spi_open(1, 50000)
   CHECK(12, 1, h>=0, 1, 0, "spi open")

   (b, d) = await pi.spi_xfer(h, [1,128,0])
   CHECK(12, 2, b, 3, 0, "spi xfer")
   await tca(b, d)

   (b, d) = await pi.spi_xfer(h, "\x01\x80\x00")
   CHECK(12, 2, b, 3, 0, "spi xfer")
   await tca(b, d)

   (b, d) = await pi.spi_xfer(h, b"\x01\x80\x00")
   CHECK(12, 2, b, 3, 0, "spi xfer")
   await tca(b, d)

   (b, d) = await pi.spi_xfer(h, '\x01\x80\x00')
   CHECK(12, 2, b, 3, 0, "spi xfer")
   await tca(b, d)

   (b, d) = await pi.spi_xfer(h, b'\x01\x80\x00')
   CHECK(12, 2, b, 3, 0, "spi xfer")
   await tca(b, d)

   e = await pi.spi_close(h)
   CHECK(12, 99, e, 0, 0, "spi close")

async def td():

   print("Wavechains & filter tests.")

   tdcb = await pi.callback(GPIO)

   await pi.set_mode(GPIO, asyncpio.OUTPUT)

   await pi.write(GPIO, asyncpio.LOW)

   e = await pi.wave_clear()
   CHECK(13, 1, e, 0, 0, "callback, set mode, wave clear")

   wf = []

   wf.append(asyncpio.pulse(1<<GPIO, 0,  50))
   wf.append(asyncpio.pulse(0, 1<<GPIO,  70))
   wf.append(asyncpio.pulse(1<<GPIO, 0, 130))
   wf.append(asyncpio.pulse(0, 1<<GPIO, 150))
   wf.append(asyncpio.pulse(1<<GPIO, 0,  90))
   wf.append(asyncpio.pulse(0, 1<<GPIO, 110))

   e = await pi.wave_add_generic(wf)
   CHECK(13, 2, e, 6, 0, "pulse, wave add generic")

   wid = await pi.wave_create()

   chain = [
      255, 0, wid, 255, 1, 128, 0, 255, 2, 0, 8,
      255, 0, wid, 255, 1,   0, 1, 255, 2, 0, 4,
      255, 0, wid, 255, 1,   0, 2]

   e = await pi.set_glitch_filter(GPIO, 0)
   CHECK(13, 3, e, 0, 0, "clear glitch filter")

   e = await pi.set_noise_filter(GPIO, 0, 0)
   CHECK(13, 4, e, 0, 0, "clear noise filter")

   tdcb.reset_tally()
   e = await pi.wave_chain(chain)
   CHECK(13, 5, e, 0, 0, "wave chain")
   while await pi.wave_tx_busy():
      await asyncio.sleep(0.1)
   await asyncio.sleep(0.3)
   tally = tdcb.tally()
   CHECK(13, 6, tally, 2688, 2, "wave chain, tally")

   await pi.set_glitch_filter(GPIO, 80)
   tdcb.reset_tally()
   await pi.wave_chain(chain)
   while await pi.wave_tx_busy():
      await asyncio.sleep(0.1)
   await asyncio.sleep(0.3)
   tally = tdcb.tally()
   CHECK(13, 7, tally, 1792, 2, "glitch filter, wave chain, tally")

   await pi.set_glitch_filter(GPIO, 120)
   tdcb.reset_tally()
   await pi.wave_chain(chain)
   while await pi.wave_tx_busy():
      await asyncio.sleep(0.1)
   await asyncio.sleep(0.2)
   tally = tdcb.tally()
   CHECK(13, 8, tally, 896, 2, "glitch filter, wave chain, tally")

   await pi.set_glitch_filter(GPIO, 140)
   tdcb.reset_tally()
   await pi.wave_chain(chain)
   while await pi.wave_tx_busy():
      await asyncio.sleep(0.1)
   await asyncio.sleep(0.2)
   tally = tdcb.tally()
   CHECK(13, 9, tally, 0, 0, "glitch filter, wave chain, tally")

   await pi.set_glitch_filter(GPIO, 0)

   await pi.wave_chain(chain)
   await pi.set_noise_filter(GPIO, 1000, 150000)
   tdcb.reset_tally()
   while await pi.wave_tx_busy():
      await asyncio.sleep(0.1)
   await asyncio.sleep(0.2)
   tally = tdcb.tally()
   CHECK(13, 10, tally, 1500, 2, "noise filter, wave chain, tally")

   await pi.wave_chain(chain)
   await pi.set_noise_filter(GPIO, 2000, 150000)
   tdcb.reset_tally()
   while await pi.wave_tx_busy():
      await asyncio.sleep(0.1)
   await asyncio.sleep(0.2)
   tally = tdcb.tally()
   CHECK(13, 11, tally, 750, 2, "noise filter, wave chain, tally")

   await pi.wave_chain(chain)
   await pi.set_noise_filter(GPIO, 3000, 5000)
   tdcb.reset_tally()
   while await pi.wave_tx_busy():
      await asyncio.sleep(0.1)
   await asyncio.sleep(0.2)
   tally = tdcb.tally()
   CHECK(13, 12, tally, 0, 2, "noise filter, wave chain, tally")

   await pi.set_noise_filter(GPIO, 0, 0)

   e = await pi.wave_delete(wid)
   CHECK(13, 13, e, 0, 0, "wave delete")

   tdcb.cancel()

if len(sys.argv) > 1:
   tests = ""
   for C in sys.argv[1]:
      c = C.lower()
      if c not in tests:
         tests += c

else:
   tests = "0123456789d"

pi = asyncpio.pi()
asyncio.run(pi.connect())

print("Connected to pigpio daemon.")

if '0' in tests: t0()
if '1' in tests: t1()
if '2' in tests: t2()
if '3' in tests: t3()
if '4' in tests: t4()
if '5' in tests: t5()
if '6' in tests: t6()
if '7' in tests: t7()
if '8' in tests: t8()
if '9' in tests: t9()
if 'a' in tests: ta()
if 'b' in tests: tb()
if 'c' in tests: tc()
if 'd' in tests: td()

asyncio.run(pi.stop())

