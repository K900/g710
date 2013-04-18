This repository contains some proof of concept code for talking to the [Logitech G710](http://www.logitech.com/en-us/product/g710plus-mechanical-gaming-keyboard?crid=825) mechanical keyboard.

Working
=======
* G1-G6 keys (somewhat, see below)
* M1-MR keys
* Game mode (events only)
* Backlight (events only)
* Media keys
* M1-MR key backlight

Known issues
============
* G1-G6 keys send 'ghost' input -- numbers 1 to 6 (same on Windows VM without drivers?!)

Won't fix
=========
* Macro recording, Logitech drivers do it in userspace
* Read/write backlight levels, game mode on demand, unless someone finds the magic control transfer data

Protocol
========
See `read.py`, proper documentation will come later.