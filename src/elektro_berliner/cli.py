import time
import fluidsynth
import keyboard
from keyboard._keyboard_event import KEY_DOWN, KEY_UP
from threading import Thread, Semaphore
import pickle

fs = None
KEYS_MAP = {}
with open('mapping.data', 'rb') as fin:
    KEYS_MAP = pickle.load(fin)
print(KEYS_MAP)

KEY_PRESS = {}
TIMERS = {}
MIN_WAIT = .3
SUSTAIN = True
DEFAULT_WAIT = 10
MAX_WAIT = 15


class TimerThread:    
    def __init__(self, synth, wait_time, min_wait, note):
        self.synth = synth
        self.note = note
        self.playing = False
        self.wait_time = wait_time
        self.min_wait = min_wait
        self.sem = Semaphore()
    
    def play_note(self):
        curr_time = time.time()
        self.playing = True
        self.synth.noteon(0, self.note, 100)
        self.sem.release()
        while curr_time < self.off_time:
            time.sleep(.1)
            curr_time = time.time()
        self.sem.acquire()
        self.synth.noteoff(0, self.note)
        self.playing = False
        self.sem.release()
    
    def stop_note(self):
        self.sem.acquire()
        self.off_time = time.time() + (self.min_wait)
        self.sem.release()

    def start_play(self):
        self.sem.acquire()
        self.off_time = time.time() + (self.wait_time)
        if not self.playing:            
            t = Thread(target=self.play_note)
            t.start()
        else:
            self.synth.noteon(0, self.note, 100)
            self.sem.release()            

def get_note(key):
    code = key.scan_code
    if key.is_keypad:
        code += 300
    note = 50
    try:
        note = KEYS_MAP[code]
    except:    
        print(f'Key {key} undefined')
    return note

def activate_note(note):
    try:
        last_activation = KEY_PRESS[note]
    except:
        last_activation = None
    
    curr_time = time.time()
    if last_activation == None or curr_time - last_activation > MAX_WAIT:
        try:
            timer_thread = TIMERS[note]
        except:
            timer_thread = TimerThread(fs, DEFAULT_WAIT, MIN_WAIT, note)
            TIMERS[note] = timer_thread
        timer_thread.start_play()
    KEY_PRESS[note] = curr_time


def deactivate_note(note):
    try:
        timer_thread = TIMERS[note]
        timer_thread.stop_note()
    except Exception as e:
        print(f'ERROR!!! [{repr(e)}]')


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
    KEY_PRESS[note] = None
    if not SUSTAIN:
        deactivate_note(note)

def on_action(event):
    if event.event_type == KEY_DOWN:
        on_press(event)

    elif event.event_type == KEY_UP:
        on_release(event)

def main():
    global fs
    fs = fluidsynth.Synth()
    fs.setting('synth.gain', 1.0)
    fs.start()

    sfid = fs.sfload("FluidR3_GM.sf2")
    fs.program_select(0, sfid, 0, 0)

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


    keyboard.hook(lambda e: on_action(e), suppress=True)

    while True:
        time.sleep(1)

    fs.delete()

if __name__ == '__main__':
    main()
