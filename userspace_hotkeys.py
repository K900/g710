from __future__ import print_function

import Xlib.display
import Xlib.ext.xtest
import Xlib.X

import g710

display = Xlib.display.Display()


def fake_input_keycode(event, keycode):
    Xlib.ext.xtest.fake_input(display, event, keycode)
    display.sync()


def fake_input(event, keysym):
    fake_input_keycode(event, display.keysym_to_keycode(keysym))


def fake_press(keysym):
    fake_input(Xlib.X.KeyPress, keysym)


def fake_release(keysym):
    fake_input(Xlib.X.KeyRelease, keysym)

# Key masks:
keymap = {
    'G1': 0x1008FF41,
    'G2': 0x1008FF42,
    'G3': 0x1008FF43,
    'G4': 0x1008FF44,
    'G5': 0x1008FF45,
    'G6': 0x1008FF46,
    'M1': 0x1008FF47,
    'M2': 0x1008FF48,
    'M3': 0x1008FF49,
    'M4': 0x1008FF4A,
    'Next track': 0x1008FF17,
    'Previous track': 0x1008FF16,
    'Stop': 0x1008FF15,
    'Play': 0x1008FF14,
    'Vol. up': 0x1008FF13,
    'Vol. down': 0x1008FF11,
    'Mute': 0x1008FF12
}


class HotkeyObserver(g710.G710Observer):
    def key_down(self, key):
        fake_press(keymap[key])

    def key_up(self, key):
        fake_release(keymap[key])

    def status_change(self, game_mode, wasd_light, key_light):
        pass


reader = g710.G710Reader()
reader.add_observer(HotkeyObserver())
reader.loop()
