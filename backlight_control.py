import sys
from PyQt4 import QtCore, QtGui
import g710

class G710Control(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.g710 = g710.G710()

        self.m1 = QtGui.QCheckBox('M1')
        self.m1.stateChanged.connect(self.update)

        self.m2 = QtGui.QCheckBox('M2')
        self.m2.stateChanged.connect(self.update)

        self.m3 = QtGui.QCheckBox('M3')
        self.m3.stateChanged.connect(self.update)

        self.mr = QtGui.QCheckBox('MR')
        self.mr.stateChanged.connect(self.update)

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
        self.wasd.valueChanged.connect(self.update)
        vbox.addWidget(self.wasd)

        vbox.addWidget(QtGui.QLabel('Keys backlight'))

        self.light = QtGui.QSlider()
        self.light.setMinimum(0)
        self.light.setMaximum(4)
        self.light.setValue(self.g710.backlight['keys'])
        self.light.setOrientation(QtCore.Qt.Horizontal)
        self.light.valueChanged.connect(self.update)
        vbox.addWidget(self.light)

        self.setWindowTitle('Logitech G710 backlight control')

    def update(self, *_):
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