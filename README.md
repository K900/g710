This repository contains some proof of concept code for talking to the [Logitech G710](http://www.logitech.com/en-us/product/g710plus-mechanical-gaming-keyboard?crid=825) mechanical keyboard.

Working
=======
* G1-G6 keys
* M1-MR keys
* Media keys
* M1-MR key backlight (write only)
* Game mode (events only)
* Backlight (events only)

Won't fix
=========
* Macro recording, Logitech drivers do it in userspace
* Read/write backlight levels, read M keys backlight, game mode on demand, unless someone finds the magic control transfer data

Protocol
========
See the source, proper documentation will come later.