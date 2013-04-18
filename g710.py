import usb.core
import usb.util


def write_ctrl(device, wValue, data):
    return device.ctrl_transfer(
        bmRequestType=0x21,
        bRequest=0x09,
        wValue=wValue,
        wIndex=1,
        data_or_wLength=data
    )


def read_ctrl(device, wValue, wLength):
    return device.ctrl_transfer(
        bmRequestType=0xa1,
        bRequest=0x01,
        wValue=wValue,
        wIndex=1,
        data_or_wLength=wLength
    )


class Backlight():
    _values = {
        'm1': False,
        'm2': False,
        'm3': False,
        'mr': False,
        'wasd': 0,
        'keys': 0,
    }

    def __getitem__(self, item):
        self._read()
        return self._values[item.lower()]

    def __setitem__(self, key, value):
        key = key.lower()
        if key in self._values.keys():
            if key in ['wasd', 'keys']:
                if 0 <= int(value) <= 4:
                    self._values[key] = int(value)
                else:
                    raise ValueError
            else:
                self._values[key] = bool(value)

            self._write()
        else:
            raise KeyError

    def _read_ctrl(self, wValue, wLength):
        return read_ctrl(self.device, wValue, wLength)

    def _read(self):
        data = self._read_ctrl(0x0306, 2)

        if data[1] & 0x10:
            self._values['m1'] = True

        if data[1] & 0x20:
            self._values['m2'] = True

        if data[1] & 0x40:
            self._values['m3'] = True

        if data[1] & 0x80:
            self._values['mr'] = True

        data = self._read_ctrl(0x0308, 4)

        self._values['wasd'] = 4 - data[1]
        self._values['keys'] = 4 - data[2]

    def _write_ctrl(self, wValue, data):
        return write_ctrl(self.device, wValue, data)

    def _write(self):
        bitmask = 0

        if self._values['m1']:
            bitmask += 0x10
        if self._values['m2']:
            bitmask += 0x20
        if self._values['m3']:
            bitmask += 0x40
        if self._values['mr']:
            bitmask += 0x80

        self._write_ctrl(0x0306, [0x06, bitmask])
        self._write_ctrl(0x0308, [0x08, 4 - self._values['wasd'], 4 - self._values['keys'], 0])

    def __init__(self, device):
        self.device = device
        self._read()


class G710():
    @property
    def game_mode(self):
        # TODO this is not writable and returns a bunch of weird numbers, WTF?
        data = read_ctrl(self.device, 0x0305, 2)
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
            write_ctrl(self.device, 0x0309, [0x00] * 13)

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
            0x01: 'Next track',
            0x02: 'Previous track',
            0x04: 'Stop',
            0x08: 'Play',
            0x10: 'Vol. up',
            0x20: 'Vol. down',
            0x40: 'Mute'
        }
    ],
    3: [
        {
            0x01: 'G1',
            0x02: 'G2',
            0x04: 'G3',
            0x08: 'G4',
            0x10: 'G5',
            0x20: 'G6'
        },
        {
            0x10: 'M1',
            0x20: 'M2',
            0x40: 'M3',
            0x80: 'MR'
        },
        {
            0x01: 'WASD backlight',
            0x02: 'Keyboard backlight',
            0x04: 'Game mode'
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
        with G710Context() as context:
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
                        pass

                if packet_id == 4:
                    for observer in self._observers:
                        # TODO what do bytes 3-7 mean?
                        observer.status_change(bool(data[0]), 4 - data[1], 4 - data[2])
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
