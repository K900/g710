#!/usr/bin/env python2
import sys
import threading

from PyQt4 import QtCore, QtGui

import Xlib.display
import Xlib.ext.xtest
import Xlib.X

import g710


class HotkeyObserver(g710.G710Observer):
    keymap = {
        'G1': 0x1008FF41,
        'G2': 0x1008FF42,
        'G3': 0x1008FF43,
        'G4': 0x1008FF44,
        'G5': 0x1008FF45,
        'G6': 0x1008FF46,
        'M1': 0x1008FF47,
        'M2': 0x1008FF48,
        'M3': 0x1008FF49,
        'M4': 0x1008FF4A,
        'Next track': 0x1008FF17,
        'Previous track': 0x1008FF16,
        'Stop': 0x1008FF15,
        'Play': 0x1008FF14,
        'Vol. up': 0x1008FF13,
        'Vol. down': 0x1008FF11,
        'Mute': 0x1008FF12
    }

    def __init__(self, display=None):
        self.display = display if display else Xlib.display.Display()

    def fake_input(self, event, keysym):
        Xlib.ext.xtest.fake_input(self.display, event, self.display.keysym_to_keycode(keysym))
        self.display.sync()

    def fake_press(self, keysym):
        self.fake_input(Xlib.X.KeyPress, keysym)

    def fake_release(self, keysym):
        self.fake_input(Xlib.X.KeyRelease, keysym)

    def key_down(self, key):
        self.fake_press(self.keymap[key])

    def key_up(self, key):
        self.fake_release(self.keymap[key])

    def status_change(self, game_mode, wasd_light, key_light):
        pass


class G710Control(QtGui.QWidget):
    _closing = False

    # noinspection PyUnresolvedReferences,PyCallByClass,PyTypeChecker,PyArgumentList
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.g710 = g710.G710()
        self.reader = g710.G710Reader(self.g710)
        self.reader.add_observer(HotkeyObserver())
        self.hotkey_thread = threading.Thread(target=self.reader.loop)
        self.hotkey_thread.setDaemon(True)
        self.hotkey_thread.start()

        self.m1 = QtGui.QCheckBox('M1')
        self.m1.stateChanged.connect(self.backlight_changed)

        self.m2 = QtGui.QCheckBox('M2')
        self.m2.stateChanged.connect(self.backlight_changed)

        self.m3 = QtGui.QCheckBox('M3')
        self.m3.stateChanged.connect(self.backlight_changed)

        self.mr = QtGui.QCheckBox('MR')
        self.mr.stateChanged.connect(self.backlight_changed)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.m1)
        hbox.addWidget(self.m2)
        hbox.addWidget(self.m3)
        hbox.addWidget(self.mr)

        vbox = QtGui.QVBoxLayout(self)
        vbox.addLayout(hbox)

        vbox.addWidget(QtGui.QLabel('WASD backlight'))

        self.wasd = QtGui.QSlider()
        self.wasd.setMinimum(0)
        self.wasd.setMaximum(4)
        self.wasd.setValue(self.g710.backlight['WASD'])
        self.wasd.setOrientation(QtCore.Qt.Horizontal)
        self.wasd.valueChanged.connect(self.backlight_changed)
        vbox.addWidget(self.wasd)

        vbox.addWidget(QtGui.QLabel('Keys backlight'))

        self.light = QtGui.QSlider()
        self.light.setMinimum(0)
        self.light.setMaximum(4)
        self.light.setValue(self.g710.backlight['keys'])
        self.light.setOrientation(QtCore.Qt.Horizontal)
        self.light.valueChanged.connect(self.backlight_changed)
        vbox.addWidget(self.light)

        self.icon = QtGui.QSystemTrayIcon()
        self.icon.setIcon(QtGui.QIcon.fromTheme("input-keyboard"))
        self.icon.setToolTip("G710Tool")

        menu = QtGui.QMenu()
        exit_action = menu.addAction("Exit")
        exit_action.setIcon(QtGui.QIcon.fromTheme("application-exit"))
        exit_action.activated.connect(self.close_right)
        self.icon.setContextMenu(menu)
        self.icon.activated.connect(self.tray_clicked)
        self.icon.show()

        self.setWindowTitle('G710Tool v0.1')

    def close_right(self):
        self._closing = True
        self.close()

    def closeEvent(self, event):
        if self._closing:
            event.accept()
        else:
            self.hide()
            event.ignore()

    def tray_clicked(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()

    def backlight_changed(self):
        self.g710.backlight['M1'] = self.m1.isChecked()
        self.g710.backlight['M2'] = self.m2.isChecked()
        self.g710.backlight['M3'] = self.m3.isChecked()
        self.g710.backlight['MR'] = self.mr.isChecked()
        self.g710.backlight['WASD'] = self.wasd.value()
        self.g710.backlight['keys'] = self.light.value()


app = QtGui.QApplication(sys.argv)
window = G710Control()
window.show()
sys.exit(app.exec_())
