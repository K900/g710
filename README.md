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
See the source, proper documentation will come later.