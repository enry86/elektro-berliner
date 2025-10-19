import keyboard
from keyboard._keyboard_event import KEY_DOWN
import time
import pickle

running = True
note = 21
keyboard_mapping = {}
savename = 'mapping.data'

def store_mapping(keyboard_mappging):
    with open(savename, 'wb') as fout:
        pickle.dump(keyboard_mapping, fout)


def on_action(evt):
    global note, keyboard_mapping
    if evt.event_type != KEY_DOWN:
        return
    code = evt.scan_code
    if code in keyboard_mapping:
        print(f'Key [{code}] already pressed, saving')
        store_mapping(keyboard_mapping)
        running = False
    else:
        keyboard_mapping[code] = note
        print(f'Key [{code}] mapped to note [{note}] ')
        note += 1

keyboard.hook(lambda e: on_action(e))

while running:
    time.sleep(1)
