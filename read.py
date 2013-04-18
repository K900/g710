import usb.core
import g710

keymap = {
    2: {
        1: {
            0x01: "Next track",
            0x02: "Previous track",
            0x04: "Stop",
            0x08: "Play",
            0x10: "Vol. up",
            0x20: "Vol. down",
            0x40: "Mute"
        }
    },
    3: {
        1: {
            0x01: "G1",
            0x02: "G2",
            0x04: "G3",
            0x08: "G4",
            0x10: "G5",
            0x20: "G6"
        },
        2: {
            0x10: "M1",
            0x20: "M2",
            0x40: "M3",
            0x80: "MR"
        },
        3: {
            0x01: "WASD backlight",
            0x02: "Keyboard backlight",
            0x04: "Game mode"
        }
    }
}

backlight = [
    "100%",
    "75%",
    "50%",
    "25%",
    "OFF"
]

with g710.G710Context() as context:
    endpoint = context.endpoint

    old_data = {
        2: [2, 0],
        3: [3, 0, 0, 0]
    }

    while True:
        try:
            data = endpoint.read(endpoint.wMaxPacketSize, timeout=1000)
        except usb.core.USBError as ex:
            if ex.errno == 110:
                print("Timed out, exiting!")
                break

        if data[0] == 4:
            print("Status change!")
            print("Game mode:", "ON" if data[1] else "OFF")
            print("WASD backlight level:", backlight[data[2]])
            print("Backlight level:", backlight[data[3]])
        else:
            for bit in keymap[data[0]]:
                keys = keymap[data[0]][bit]
                for mask in keys:
                    if data[bit] & mask:
                        if not (old_data[data[0]][bit] & mask):
                            print(keys[mask], "DOWN")
                    elif old_data[data[0]][bit] & mask:
                        print(keys[mask], "UP")

            old_data[data[0]] = data