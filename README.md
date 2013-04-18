This repository contains some proof of concept code for talking to the [Logitech G710](http://www.logitech.com/en-us/product/g710plus-mechanical-gaming-keyboard?crid=825) mechanical keyboard.

Working
=======
* G1-G6 keys (somewhat, see below)
* M1-MR keys
* Game mode (events only)
* Backlight (events only)
* Media keys

Known issues
============
* G1-G6 keys send 'ghost' input -- numbers 1 to 6
* Read/write backlight levels, game mode on demand
  
Won't fix
=========
* Macro recording, Logitech drivers do it in userspace

Protocol
========
See `read.py`, proper documentation will come later.