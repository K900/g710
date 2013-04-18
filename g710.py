import usb.core
import usb.util


class Backlight():

    # TODO investigate: there are two backlight wValues
    # 0x0308 is what I'm using now, and it works fine
    # 0x0307 is the other one, and it seems to allow more control at the cost of 'breaking' buttons
    # data_or_wlength for 0x307 is [0x07, (WASD pair), (other pair)]
    # Values are paired, the second one is brightness, the first one is ???
    # Default value pairs:
    # [0, 32]
    # [143, 17]
    # [223, 7]
    # [223, 1]
    # [0, 0]

    _values = {
        "M1": False,
        "M2": False,
        "M3": False,
        "MR": False,
        "WASD": 0,
        "keys": 0,
    }

    def __getitem__(self, item):
        self._read()
        return self._values[item]

    def __setitem__(self, key, value):
        if key in self._values.keys():
            if key in ["WASD", "keys"]:
                if 0 <= int(value) <= 4:
                    self._values[key] = int(value)
                else:
                    raise ValueError
            else:
                self._values[key] = bool(value)

            self._write()
        else:
            raise KeyError

    def _read(self):
        data = self.device.ctrl_transfer(
            bmRequestType=0xa1,
            bRequest=0x01,
            wValue=0x0306,
            wIndex=1,
            data_or_wLength=2
        )

        if data[1] & 0x10:
            self._values["M1"] = True

        if data[1] & 0x20:
            self._values["M2"] = True

        if data[1] & 0x40:
            self._values["M3"] = True

        if data[1] & 0x80:
            self._values["MR"] = True

        data = self.device.ctrl_transfer(
            bmRequestType=0xa1,
            bRequest=0x01,
            wValue=0x0308,
            wIndex=1,
            data_or_wLength=4
        )

        self._values["WASD"] = data[1]
        self._values["keys"] = data[2]

    def _write(self):
        bitmask = 0

        if self._values["M1"]:
            bitmask += 0x10
        if self._values["M2"]:
            bitmask += 0x20
        if self._values["M3"]:
            bitmask += 0x40
        if self._values["MR"]:
            bitmask += 0x80

        self.device.ctrl_transfer(
            bmRequestType=0x21,
            bRequest=0x09,
            wValue=0x0306,
            wIndex=1,
            data_or_wLength=[0x06, bitmask]
        )

        self.device.ctrl_transfer(
            bmRequestType=0x21,
            bRequest=0x09,
            wValue=0x308,
            wIndex=1,
            data_or_wLength=[0x08, self._values["WASD"], self._values["keys"], 0]
        )

    def __init__(self, device):
        self.device = device
        self._read()


class G710():
    @property
    def game_mode(self):
        # TODO this is not writable and returns a bunch of weird numbers, WTF?
        data = self.device.ctrl_transfer(
            bmRequestType=0xa1,
            bRequest=0x01,
            wValue=0x0305,
            wIndex=1,
            data_or_wLength=100
        )
        return bool(data[1])


    def __init__(self):
        self.device = usb.core.find(idVendor=0x046d, idProduct=0xc24d)

        if self.device:
            for interface in self.device.get_active_configuration():
                if interface.bInterfaceNumber == 1:
                    self.interface = interface
                    if self.device.is_kernel_driver_active(interface):
                        self.device.detach_kernel_driver(interface)

                    for endpoint in interface:
                        if endpoint.bEndpointAddress == 130:
                            self.endpoint = endpoint

            # Stop ghost input
            self.device.ctrl_transfer(
                bmRequestType=0x21,
                bRequest=0x09,
                wValue=0x0309,
                wIndex=1,
                data_or_wLength=[0x00] * 13
            )

            self.backlight = Backlight(self.device)

    def __del__(self):
        usb.util.dispose_resources(self.device)
        self.device.attach_kernel_driver(self.interface)

class G710Context():
    def __enter__(self):
        self.g710 = G710()
        return self.g710

    def __exit__(self, *_):
        del self.g710

class G710Observer():
    def key_up(self, key):
        pass

    def key_down(self, key):
        pass

    def status_change(self, game_mode, wasd_light, key_light):
        pass

# Key masks:
# keymap[packet_id][byte_number] contains all possible mask 'parts' for byte <byte_number> in packet <packet_id>
keymap = {
    2: [
        {
            0x01: "Next track",
            0x02: "Previous track",
            0x04: "Stop",
            0x08: "Play",
            0x10: "Vol. up",
            0x20: "Vol. down",
            0x40: "Mute"
        }
    ],
    3: [
        {
            0x01: "G1",
            0x02: "G2",
            0x04: "G3",
            0x08: "G4",
            0x10: "G5",
            0x20: "G6"
        },
        {
            0x10: "M1",
            0x20: "M2",
            0x40: "M3",
            0x80: "MR"
        },
        {
            0x01: "WASD backlight",
            0x02: "Keyboard backlight",
            0x04: "Game mode"
        }
    ]
}


class G710Reader():
    _observers = set()
    _status_handlers = set()

    def add_observer(self, observer):
        if issubclass(observer.__class__, G710Observer):
            self._observers.add(observer)
        else:
            raise TypeError

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def loop(self):
        with G710() as context:
            endpoint = context.endpoint

            old_data = {
                2: [0],
                3: [0, 0, 0]
            }

            while True:
                try:
                    data = endpoint.read(endpoint.wMaxPacketSize, timeout=1000)
                    packet_id = data[0]
                    data = data[1:]
                except usb.core.USBError as ex:
                    if ex.errno == 110:
                        print("Timed out, exiting!")
                        break

                if packet_id == 4:
                    for observer in self._observers:
                        # TODO what do bytes 3-7 mean?
                        observer.status_change(bool(data[0]), data[1], data[2])
                else:
                    for data_byte, old_byte, keys in zip(data, old_data[packet_id], keymap[packet_id]):
                        for mask in keys:
                            is_down = data_byte & mask
                            was_down = old_byte & mask
                            if not was_down and is_down:
                                for observer in self._observers:
                                    observer.key_down(keys[mask])
                            if was_down and not is_down:
                                for observer in self._observers:
                                    observer.key_up(keys[mask])

                    old_data[packet_id] = data
