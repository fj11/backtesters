from PySide2.QtCore import Slot, Signal, QObject

class Signals(QObject):
    message = Signal(str)
    finished = Signal()
    process = Signal(int)
    process_range = Signal(int, int)

    def __init__(self, output, processbar):
        QObject.__init__(self)
        self.message.connect(output.append)
        self.process.connect(processbar.setValue)
        self.process_range.connect(processbar.setRange)

