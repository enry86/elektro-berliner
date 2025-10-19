import time
import fluidsynth
import keyboard
from keyboard._keyboard_event import KEY_DOWN, KEY_UP
from mapping import KEYS_MAP
from threading import Thread

KEY_PRESS = {}
MIN_WAIT = .2

fs = fluidsynth.Synth()
fs.setting('synth.gain', 1.0)
fs.start()

sfid = fs.sfload("FluidR3_GM.sf2")
fs.program_select(0, sfid, 0, 2)

print("Start chord")
fs.noteon(0, 60, 80)
fs.noteon(0, 67, 80)
fs.noteon(0, 76, 80)

time.sleep(2)

fs.noteoff(0, 60)
fs.noteoff(0, 67)
fs.noteoff(0, 76)
print("End chord")

time.sleep(1.0)

def get_note(key):
    note = 50
    try:
        note = KEYS_MAP[key.scan_code]
    except:    
        print(f'Key {key} undefined')
    return note

def activate_note(note):
    try:
        last_activation = KEY_PRESS[note]
    except:
        last_activation = None
    
    curr_time = time.time()
    if last_activation == None or curr_time - last_activation > 10000:
        fs.noteon(0, note, 100)
        KEY_PRESS[note] = curr_time

def deactivate_note(note, wait_time=0):
    if wait_time > 0:
        time.sleep(wait_time)
    fs.noteoff(0, note)
    print(f'note {note} deactivated')  

def on_press(key):
    print('{0} pressed'.format(
        key))
    note = get_note(key)
    activate_note(note)
    

def on_release(key):
    print('{0} release'.format(
        key))
    note = get_note(key)
    try:
        last_activation = KEY_PRESS[note]
    except:
        print(f'note {note} not found')
        return
    if last_activation == None:
        print(f'note {note} never activated')
        return
    wait_time = (time.time() - last_activation) / 1000
    KEY_PRESS[note] = None
    print(f'waiting {wait_time} s before stopping note')
    if wait_time < MIN_WAIT:
        decay_thread = Thread(target=deactivate_note, args=(note, MIN_WAIT-wait_time, ))
        decay_thread.start()
    else:
        deactivate_note(note)

def on_action(event):
    if event.event_type == KEY_DOWN:
        on_press(event)

    elif event.event_type == KEY_UP:
        on_release(event)


keyboard.hook(lambda e: on_action(e))

while True:
    time.sleep(1)

fs.delete()
