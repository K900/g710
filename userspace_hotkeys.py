from __future__ import print_function
import usb.core
import g710

import Xlib.display
import Xlib.ext.xtest
import Xlib.X

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
keymap = [
        {
            0x01: 0x1008FF41,
            0x02: 0x1008FF42,
            0x04: 0x1008FF43,
            0x08: 0x1008FF44,
            0x10: 0x1008FF45,
            0x20: 0x1008FF46,
        },
        {
            0x10: 0x1008FF47,
            0x20: 0x1008FF48,
            0x40: 0x1008FF49,
            0x80: 0x1008FF4A
        }
]

with g710.G710Context() as context:
    endpoint = context.endpoint

    old_data = [0, 0, 0]

    while True:
        try:
            data = endpoint.read(endpoint.wMaxPacketSize)
            packet_id = data[0]
            data = data[1:]
            if packet_id == 3:
                for data_byte, old_byte, keys in zip(data, old_data, keymap):
                    for mask in keys:
                        is_down = data_byte & mask
                        was_down = old_byte & mask
                        if not was_down and is_down:
                            fake_press(keys[mask])
                        if was_down and not is_down:
                            fake_release(keys[mask])

                old_data = data
        except usb.core.USBError as ex:
            if ex.errno == 110:
                pass
            else:
                raise ex
