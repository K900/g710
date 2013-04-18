from __future__ import print_function
import g710


class MyObserver(g710.G710Observer):
    def key_down(self, key):
        print(key, "DOWN")

    def key_up(self, key):
        print(key, "UP")

    def status_change(self, game_mode, wasd_light, key_light):
        print("Game mode ", "ON" if game_mode else "OFF")
        print("WASD backlight: ", wasd_light)
        print("Key backlight: ", key_light)


reader = g710.G710Reader()
reader.add_observer(MyObserver())
reader.loop()
