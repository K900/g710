from __future__ import print_function
import sys
if sys.version_info.major == 2:
    input = raw_input

import g710

def make_bitmask(m1, m2, m3, mr):
    result = 0

    if m1:
        result += 0x10
    if m2:
        result += 0x20
    if m3:
        result += 0x40
    if mr:
        result += 0x80

    return result


with g710.G710Context() as context:
    values = []

    for i in ['1', '2', '3', 'R']:
        while True:
            value = input('M{} backlight [Y/n]: '.format(i)).strip()
            if value.lower() in ['on', 'yes', 'y', '1', '']:
                values.append(True)
                break
            if value.lower() in ['off', 'no', 'n', '0']:
                values.append(False)
                break

    context.device.ctrl_transfer(
        bmRequestType=0x21,
        bRequest=0x09,
        wValue=0x0306,
        wIndex=1,
        data_or_wLength=[0x06, make_bitmask(*values)]
    )