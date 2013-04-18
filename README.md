This repository contains some proof of concept code for talking to the [Logitech G710](http://www.logitech.com/en-us/product/g710plus-mechanical-gaming-keyboard?crid=825) mechanical keyboard.

Working
=======
* G1-G6 key events
* M1-MR key events
* Media key events
* M1-MR per key backlight - events, read, write
* WASD/other keys backlight - events, read, write
* 'Game mode' - events, read

Known issues
============
* Game mode is not writable (I'm missing something...)

Won't fix
=========
* Macro recording, Logitech drivers do it in userspace

Protocol
========
* Key events
    * All key events are sent from interface 1, endpoint 130
    * G1-G6 keys send numbers 1 to 6 by default, stop by writing to control `0x0309`
    * Media key send interrupts in the format of `0x02 [bitmask]`
    * Other keys send interrupts in the format of `0x03 [G keys bitmask] [M keys bitmask] [backlight / game mode bitmask]`
    * See `keymap` in `g710.py` for details

* Control values
    * All control values return their ID as the first value
    * `0x0305` - read: `0x05 [game mode] 0x19 0x49 0x51 0xff 0xff 0xff`. Writing doesn't change the game mode.
        * TODO meaning of other values unknown
    * `0x0306` - read/write `0x06 [M keys bitmask]` - sets backlight for M keys
        * Bitmask values: `0x10` - M1, `0x20` - M2, `0x40` - M3, `0x80` - MR
    * `0x0307` - read/write `0x07 [WASD value pair] [other value pair]` - sets backlight
        * Value pairs for default backlight levels:
            * `0x00 0x20`
            * `0x8f 0x11`
            * `0xdf 0x07`
            * `0xdf 0x01`
            * `0x00 0x00`
        * Writing backlight this way resets buttons to some random(ish) setting
            * TODO investigate
    * `0x0308` - read/write `0x08 [WASD backlight level] [other backlight level] 0x00` - backlight levels
        * Backlight levels are 0-4, 0 being the brightest
        * Last value likely unused
    * `0x0309` - read/write `0x09 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00` - disables ghost input on write
        * Values likely unused
        * TODO what are valid values?

