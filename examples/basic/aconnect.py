#!/usr/bin/env python
#
# midiin_callback.py
#
"""Show how to receive MIDI input by setting a callback function."""

from __future__ import print_function

import logging
import sys
import time
import rtmidi


# from rtmidi.midiutil import open_midiinput
# from rtmidi.midiutil import open_midioutput

log = logging.getLogger('midiin_callback')
logging.basicConfig(level=logging.DEBUG)

midiin = rtmidi.MidiIn()
midiout = rtmidi.MidiOut()

names = midiin.get_ports()

print("midi in")  

for port, name in enumerate(names):
    print("[%i] %s" % (port, name))


print("midi out")  
names = midiout.get_ports()
for port, name in enumerate(names):
    print("[%i] %s" % (port, name))
             

class MidiInputHandler(object):
    def __init__(self, port, midiout):
        self.port = port
        self._wallclock = time.time()
        self.midiout = midiout

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        self.midiout.send_message(message)


# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.
port = sys.argv[1] if len(sys.argv) > 1 else None


def open_midi_in(port):
    #global midiin
    try:
        # midiin, port_name = open_midiinput(port)
        if not midiin.is_port_open():
            midiin.open_port(port)
            port_name = midiin.get_port_name(port)
            print("midi in opening " + port_name + " " + str(port))
            print("Attaching MIDI input callback handler.")
            midiin.set_callback(MidiInputHandler(port_name, midiout))
    except (EOFError, KeyboardInterrupt):
        sys.exit()
  

def open_midi_out(port):
    try:
        # midiin, port_name = open_midiinput(port)
        # midiout, port_name = open_midioutput(port)
        if not midiout.is_port_open():
            midiout.open_port(port)
            port_name = midiout.get_port_name(port)
            print("midi out opening " + port_name + " " + str(port))

    except (EOFError, KeyboardInterrupt):
        sys.exit()


midiout_found = False
port_in_index = None

midiin_found = False
port_out_index = None

print("Entering main loop. Press Control-C to exit.")
try:
    # Just wait for keyboard interrupt,
    # everything else is handled via the input callback.
    while True:
        time.sleep(1)
        if port_in_index is not None:
            open_midi_in(port_in_index)

        if port_out_index is not None:
            open_midi_out(port_out_index)
            #pass
            
        names = midiout.get_ports()
        midiout_found = False
        for port, name in enumerate(names):
            if "FLUID" in name and "Client" not in name:
                print("[%i] %s" % (port, name))
                midiout_found = True
                port_out_index = port
                break

        names = midiin.get_ports()
        midiin_found = False
        for port, name in enumerate(names):
            if "Impact" in name and "Client" not in name:
                print("[%i] %s" % (port, name))
                midiin_found = True
                port_in_index = port
                break

        if not midiin_found:     
            print("closing ports")    
            midiin.close_port()
            midiout.close_port()
            port_in_index = None
            port_out_index = None
          
  
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
   
  
