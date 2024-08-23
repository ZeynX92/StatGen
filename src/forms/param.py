from PyQt5 import uic
from random import randint
from PyQt5.QtWidgets import QWidget, QMessageBox


class AddParam(QWidget):
    def __init__(self, parent_):
        super().__init__()
        uic.loadUi('ui/add_param.ui', self)

        self.parent_ = parent_

        self.radioButton.mode = 'int'
        self.radioButton.toggled.connect(self.mode_change)

        self.radioButton_1.mode = 'str'
        self.radioButton_1.toggled.connect(self.mode_change)

        self.cancel_btn.clicked.connect(self.cancel)
        self.ok.clicked.connect(self.add_param)

        self.spinBox_min.setEnabled(True)
        self.spinBox_max.setEnabled(True)
        self.textEdit.setEnabled(False)

        self.cur_mode = 'int'

    @staticmethod
    def create_warning(title: str, text: str):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Warning)
        msg.setText(text)

        return msg

    def mode_change(self):
        if self.sender().isChecked():
            if self.sender().mode == 'int':
                self.spinBox_min.setEnabled(True)
                self.spinBox_max.setEnabled(True)
                self.textEdit.setEnabled(False)

                self.cur_mode = 'int'
            if self.sender().mode == 'str':
                self.spinBox_min.setEnabled(False)
                self.spinBox_max.setEnabled(False)
                self.textEdit.setEnabled(True)

                self.cur_mode = 'str'

    def add_param(self):
        if not str(self.lineEdit.text()):
            msg = self.create_warning("Тебя подписывать не научили?",
                                      "Вы пытаетесь создать пустую характеристику")
            msg.exec_()
            return

        if self.cur_mode == 'int':
            if str(self.lineEdit.text()) and self.spinBox_max.value() > self.spinBox_min.value():
                self.parent_.params[str(self.lineEdit.text())] = {"type": 'int', "min": self.spinBox_min.value(),
                                                                  "max": self.spinBox_max.value(),
                                                                  'cur': randint(self.spinBox_min.value(),
                                                                                 self.spinBox_max.value()),
                                                                  'checkbox': None}
                self.parent_.setup_table()
                self.cancel()
            else:
                msg = self.create_warning("Не, ну ты реально конч*****?!", "Максимальное значение меньше минимального!")
                msg.exec_()

        if self.cur_mode == 'str':
            if str(self.lineEdit.text()) and [i for i in self.textEdit.toPlainText().split('\n') if i]:
                self.parent_.params[str(self.lineEdit.text())] = {"type": 'str', "contents": [i for i in
                                                                                              self.textEdit.toPlainText().split(
                                                                                                  '\n') if i],
                                                                  "cur": randint(0,
                                                                                 len([i for i in
                                                                                      self.textEdit.toPlainText().split(
                                                                                          '\n') if i]) - 1),
                                                                  "combobox": None, 'checkbox': None}

                self.parent_.setup_table()
                self.cancel()
            else:
                msg = self.create_warning("Иллюзия выбора...",
                                          "Вы создали характеристику с пустым списком")
                msg.exec_()

    def cancel(self):
        self.hide()
