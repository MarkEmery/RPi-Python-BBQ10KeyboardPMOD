#
# bbq10keyboard_injector.py for the Raspberry Pi (and others) by Mark Strickland Emery @_MARKSE on Twitter.
# A Python keystroke injector for @arturo182's BBQ10KBD PMOD based on Arturo's sample CircuitPython script.
#
# Changes: We don't use the "with uinput.Device(events) as device:" method as this costs too much in device open/write/close cycles.
#          Instead, we assume this code is running as a daemon and open the device just once. Run from systemd, the script should
#          be made to restart if it fails.
#          Check out /usr/lib/python3/dist-packages/uinput/ev.py for possible KEY events.
#          Hash 'dict' stores all of the keyboard events we can send.
#          Hash 'shifted' lets the code know what SHIFT-<key> to send to get things normally found above other keys on a PC keyboard.

import board
from bbq10keyboard import BBQ10Keyboard, STATE_PRESS, STATE_RELEASE, STATE_LONG_PRESS
import time
import uinput
import string

events = (
    uinput.KEY_UP, uinput.KEY_DOWN, uinput.KEY_LEFT, uinput.KEY_RIGHT, uinput.KEY_DELETE, uinput.KEY_BACKSPACE, uinput.KEY_MINUS, uinput.KEY_LEFTSHIFT,
    uinput.KEY_KPPLUS, uinput.KEY_SEMICOLON, uinput.KEY_LEFTBRACE, uinput.KEY_RIGHTBRACE, uinput.KEY_APOSTROPHE, uinput.KEY_GRAVE, uinput.KEY_DOLLAR,
    uinput.KEY_SPACE, uinput.KEY_TAB, uinput.KEY_ENTER, uinput.KEY_SPACE, uinput.KEY_DOT, uinput.KEY_COMMA, uinput.KEY_SLASH, uinput.KEY_BACKSLASH,
    uinput.KEY_NUMERIC_POUND,
    uinput.KEY_0, uinput.KEY_1, uinput.KEY_2, uinput.KEY_3, uinput.KEY_4, uinput.KEY_5, uinput.KEY_6, uinput.KEY_7, uinput.KEY_8, uinput.KEY_9,
    uinput.KEY_A, uinput.KEY_B, uinput.KEY_C, uinput.KEY_D, uinput.KEY_E, uinput.KEY_F, uinput.KEY_G, uinput.KEY_H, uinput.KEY_I, uinput.KEY_J,
    uinput.KEY_K, uinput.KEY_L, uinput.KEY_M, uinput.KEY_N, uinput.KEY_O, uinput.KEY_P, uinput.KEY_Q, uinput.KEY_R, uinput.KEY_S, uinput.KEY_T,
    uinput.KEY_U, uinput.KEY_V, uinput.KEY_W, uinput.KEY_X, uinput.KEY_Y, uinput.KEY_Z,
    )

dict = { '0': uinput.KEY_0, '1': uinput.KEY_1, '2': uinput.KEY_2, '3': uinput.KEY_3, '4': uinput.KEY_4, '5': uinput.KEY_5, '6': uinput.KEY_6, '7': uinput.KEY_7, '8': uinput.KEY_8, '9': uinput.KEY_9, 'a': uinput.KEY_A, 'b': uinput.KEY_B, 'c': uinput.KEY_C, 'd': uinput.KEY_D, 'e': uinput.KEY_E, 'f': uinput.KEY_F, 'g': uinput.KEY_G, 'h': uinput.KEY_H, 'i': uinput.KEY_I, 'j': uinput.KEY_J, 'k': uinput.KEY_K, 'l': uinput.KEY_L, 'm': uinput.KEY_M, 'n': uinput.KEY_N, 'o': uinput.KEY_O, 'p': uinput.KEY_P, 'q': uinput.KEY_Q, 'r': uinput.KEY_R, 's': uinput.KEY_S, 't': uinput.KEY_T, 'u': uinput.KEY_U, 'v': uinput.KEY_V, 'w': uinput.KEY_W, 'x': uinput.KEY_X, 'y': uinput.KEY_Y, 'z': uinput.KEY_Z, "\t": uinput.KEY_TAB, "\n": uinput.KEY_ENTER, " ":  uinput.KEY_SPACE, ".":  uinput.KEY_DOT, ",":  uinput.KEY_COMMA, "/":  uinput.KEY_SLASH, "\\": uinput.KEY_BACKSLASH, "\d": uinput.KEY_DELETE, "\b": uinput.KEY_BACKSPACE, "-": uinput.KEY_MINUS, "+": uinput.KEY_KPPLUS, ";": uinput.KEY_SEMICOLON, "'": uinput.KEY_APOSTROPHE, "`": uinput.KEY_GRAVE, } 

shifted = { '?':'/', ':':';', '"':'2', '_':'-', '!': '1', '@': "'", '$':'4', '#': '3', '(': '9', ')': '0', 'A':'a', 'B':'b', 'C':'c', 'D':'d', 'E':'e', 'F':'f', 'G':'g', 'H':'h', 'I':'i', 'J':'j', 'K':'k', 'L':'l', 'M':'m', 'N':'n', 'O':'o', 'P':'p', 'Q':'q', 'R':'r', 'S':'s', 'T':'t', 'U':'u', 'V':'v', 'W':'w', 'X':'x', 'Y':'y', 'Z':'z', }

i2c = board.I2C()
kbd = BBQ10Keyboard(i2c)

kbd.backlight = 0.25
time.sleep(0.3)
kbd.backlight = 0.5
time.sleep(0.3)
kbd.backlight = 0.25

device = uinput.Device(events)

while True:
    key_count = kbd.key_count
    if key_count == 0:
        time.sleep(0.1)
    else:
        key = kbd.key
        state = 'pressed'
        if key[0] == STATE_LONG_PRESS:
            state = 'held down'
        elif key[0] == STATE_RELEASE:
            state = 'released'

        # print("key: '%s' (dec %d, hex %02x) %s" % ( key[1], ord(key[1]), ord(key[1]), state ) )

        if state == "pressed":
            if key[1] in dict or key[1] in shifted:
                if key[1] in shifted:
                    # print("Sending: SHIFT '%s'" % shifted[key[1]])
                    device.emit_combo([ uinput.KEY_LEFTSHIFT, dict[shifted[key[1]]] ])
                else:
                    # print("Sending: '%s'" % key[1])
                    device.emit_click(dict[key[1]])

