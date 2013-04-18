from __future__ import print_function
import sys

if sys.version_info.major == 2:
    input = raw_input

import g710

with g710.G710() as context:
    for i in ['1', '2', '3', 'R']:
        while True:
            value = input('M{} backlight [Y/n]: '.format(i)).strip()

            if value.lower() in ['on', 'yes', 'y', '1', '']:
                context.backlight['M' + i] = True
                break

            if value.lower() in ['off', 'no', 'n', '0']:
                context.backlight['M' + i] = False
                break