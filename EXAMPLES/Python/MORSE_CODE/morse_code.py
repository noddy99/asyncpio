#!/usr/bin/env python

import asyncio

import asyncpio

morse={
'a':'.-'   , 'b':'-...' , 'c':'-.-.' , 'd':'-..'  , 'e':'.'    ,
'f':'..-.' , 'g':'--.'  , 'h':'....' , 'i':'..'   , 'j':'.---' ,
'k':'-.-'  , 'l':'.-..' , 'm':'--'   , 'n':'-.'   , 'o':'---'  ,
'p':'.--.' , 'q':'--.-' , 'r':'.-.'  , 's':'...'  , 't':'-'    ,
'u':'..-'  , 'v':'...-' , 'w':'.--'  , 'x':'-..-' , 'y':'-.--' ,
'z':'--..' , '1':'.----', '2':'..---', '3':'...--', '4':'....-',
'5':'.....', '6':'-....', '7':'--...', '8':'---..', '9':'----.',
'0':'-----'}

GPIO=22

MICROS=100000

NONE=0

DASH=3
DOT=1

GAP=1
LETTER_GAP=3-GAP
WORD_GAP=7-LETTER_GAP

async def transmit_string(pi, gpio, str):

   await pi.wave_clear() # start a new waveform

   wf=[]

   for C in str:
      c=C.lower()
      print(c)
      if c in morse:
         k = morse[c]
         for x in k:

            if x == '.':
               wf.append(asyncpio.pulse(1<<gpio, NONE, DOT * MICROS))
            else:
               wf.append(asyncpio.pulse(1<<gpio, NONE, DASH * MICROS))

            wf.append(asyncpio.pulse(NONE, 1<<gpio, GAP * MICROS))

         wf.append(asyncpio.pulse(NONE, 1<<gpio, LETTER_GAP * MICROS))

      elif c == ' ':
         wf.append(asyncpio.pulse(NONE, 1<<gpio, WORD_GAP * MICROS))

   await pi.wave_add_generic(wf)

   await pi.wave_tx_start()


async def main():
   pi = asyncpio.pi()
   await pi.connect()

   await pi.set_mode(GPIO, asyncpio.OUTPUT)

   await transmit_string(pi, GPIO, "Now is the winter of our discontent")

   while await pi.wave_tx_busy():
      pass

   await transmit_string(pi, GPIO, "made glorious summer by this sun of York")

   while await pi.wave_tx_busy():
      pass

   await pi.stop()

asyncio.run(main())
