from PySide2.QtUiTools import QUiLoader

from PySide2.QtWidgets import QListWidget, QComboBox, QWidget, QDialogButtonBox

class FunctionDialog():

    def __init__(self, data_frame, parent=None):
        self.data_frame = data_frame

        loader = QUiLoader()
        function = loader.load('function_dialog.ui', parentWidget=parent)

        self.list1 = function.findChild(QListWidget, "listWidget1")
        self.list2 = function.findChild(QListWidget, "listWidget2")
        button_box = function.findChild(QDialogButtonBox, "buttonBox")
        function_box = function.findChild(QComboBox, "function_box")
        function_box.currentIndexChanged.connect(self.onFunctionBox)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        list_items = list(data_frame.columns)
        for item in list_items:
            self.list1.addItem(item)

        function.show()

    def onFunctionBox(self, index):
        print(index)
        if index > 4:
            self.list2.enabled(False)

    def accept(self):

        print("accpet")

    def reject(self):
        print("reject")