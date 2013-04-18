from __future__ import print_function
import usb.core
import g710

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
            print("Status change!")
            print("Game mode:", "ON" if data[0] else "OFF")
            print("WASD backlight level:", backlight[data[1]])
            print("Backlight level:", backlight[data[2]])
        else:
            for data_byte, old_byte, keys in zip(data, old_data[packet_id], keymap[packet_id]):
                for mask in keys:
                    is_down = data_byte & mask
                    was_down = old_byte & mask
                    if not was_down and is_down:
                        print(keys[mask], "DOWN")
                    if was_down and not is_down:
                        print(keys[mask], "UP")

            old_data[packet_id] = data