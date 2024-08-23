import base64
from .param import AddParam
from random import randint
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap
from tools import write_json, read_json
from tools.gen_img import model_id, api
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QComboBox, QTableWidget, QCheckBox, QFileDialog, \
    QMessageBox

import asyncio
from qasync import asyncSlot


class StatGen(QMainWindow):
    def __init__(self, loop=None):
        super().__init__()
        uic.loadUi('ui/main.ui', self)

        self.add_param_form = None

        self.params = {
            "image": None,
            "здоровье": {"type": 'int', "min": 1, "max": 100, 'cur': 50, 'checkbox': None},
            "черта": {"type": 'str', "contents": ['умный', 'жидкий', 'черт', 'молодец'], "cur": 1, "combobox": None,
                      'checkbox': None},
            "броня": {"type": 'str', "contents": ['легкая', 'тяжелая'], "cur": 0, "combobox": None, 'checkbox': None}
        }
        self.setup_table()

        self.save.clicked.connect(self.save_char)
        self.load.clicked.connect(self.load_char)
        self.make.clicked.connect(self.make_char)

        self.tableWidget.cellChanged.connect(self.update_param)
        self.tableWidget.cellDoubleClicked.connect(self.edit_param)

        self.add.clicked.connect(self.add_param)
        self.rem.clicked.connect(self.rem_param)

        self.loop = loop or asyncio.get_event_loop()

    @staticmethod
    def create_warning(title: str, text: str):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Warning)
        msg.setText(text)

        return msg

    def update_param(self):
        try:
            if isinstance(self.sender(), QTableWidget):
                try:
                    val = int(self.tableWidget.item(self.tableWidget.currentRow(), 2).text())
                    if self.params[str(self.tableWidget.item(self.tableWidget.currentRow(), 1).text())]['min'] <= val <= \
                            self.params[str(self.tableWidget.item(self.tableWidget.currentRow(), 1).text())]['max']:
                        self.params[str(self.tableWidget.item(self.tableWidget.currentRow(), 1).text())]['cur'] = val
                    else:
                        raise ValueError
                except ValueError:
                    self.tableWidget.setItem(self.tableWidget.currentRow(), 2, QTableWidgetItem(
                        str(self.params[str(self.tableWidget.item(self.tableWidget.currentRow(), 1).text())]['cur'])))

                    msg = self.create_warning("Попался!", "Вы вводите недопустимое значение характеристики!")
                    msg.exec_()

            if isinstance(self.sender(), QComboBox):
                old_data = list(self.params.items())[1:]
                for i in range(len(old_data)):
                    if old_data[i][1]['type'] == 'str':
                        if old_data[i][1]['combobox'] == self.sender():
                            self.params[old_data[i][0]]['cur'] = self.sender().currentIndex()
                            break
        except AttributeError or KeyError:
            pass

    def setup_table(self):
        self.tableWidget.setRowCount(len(self.params) - 1)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["🔄", "Название", "Значение"])

        self.tableWidget.setColumnWidth(0, 20)
        self.tableWidget.setColumnWidth(1, 131)
        self.tableWidget.setColumnWidth(2, 175)

        for i, param in enumerate(self.params.items()):
            if param[0] == 'image':
                continue

            save_cur = param[1]['cur']  # Это костыль от бага с выделенной ячейкой

            item = QTableWidgetItem(param[0])
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.tableWidget.setItem(i - 1, 1, item)

            if param[1]['checkbox'] is None:
                checkbox = QCheckBox("", self)
                checkbox.setChecked(True)
                self.params[param[0]]['checkbox'] = checkbox
                self.tableWidget.setCellWidget(i - 1, 0, checkbox)

            if param[1]['type'] == 'int':
                self.tableWidget.setItem(i - 1, 2, QTableWidgetItem(str(save_cur)))

            if param[1]['type'] == 'str':
                if param[1]['combobox'] is None:
                    combo_box = QComboBox()
                    combo_box.addItems(param[1]['contents'])
                    combo_box.setCurrentIndex(param[1]['cur'])
                    combo_box.currentIndexChanged.connect(self.update_param)
                    self.params[param[0]]['combobox'] = combo_box
                    self.tableWidget.setCellWidget(i - 1, 2, combo_box)
                else:
                    param[1]['combobox'].setCurrentIndex(param[1]['cur'])

    def save_char(self):
        path = QFileDialog.getExistingDirectory(self, "Open Directory", "/home",
                                                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks |
                                                QFileDialog.DontUseNativeDialog)

        data = dict(self.params)

        for key in data.keys():
            if key == 'image':
                continue

            data[key]['checkbox'] = None
            if data[key]['type'] == 'str':
                data[key]['combobox'] = None

        if self.name_text.toPlainText() and path:
            try:
                write_json(path + f'/{self.name_text.toPlainText()}.json', data)
                self.setup_table()
            except PermissionError:
                msg = self.create_warning("Район попутал? Или чё!?", "У вас нет прав сохранятся в этой директории!")
                msg.exec_()
        else:
            msg = self.create_warning("Безымянные, конечно, классные, НО...",
                                      "Вы пытаетесь сохранить персонажа без имени!")
            msg.exec_()

    def load_char(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, "Open file", "/home", "Characters (*.json)")

            self.name_text.setText(path.split('/')[-1].replace('.json', ''))
            self.params = read_json(path)
            self.setup_table()

            if self.params['image']:
                with open('buff.png', 'wb') as file:
                    file.write(base64.b64decode(''.join(self.params['image'][0])))

                self.image.setPixmap(QPixmap("buff.png"))
                self.plainTextEdit.setPlainText(self.params['image'][1])
        except Exception as e:
            msg = self.create_warning("Это не наше!",
                                      f"Похоже файл не от нас, возникла ошибка: {e.__class__}")
            msg.exec_()

    @asyncSlot()
    async def make_char(self):
        if self.checkBox_image.isChecked():
            try:
                print('Started...')
                self.setEnabled(False)
                self.image.setText('Generating...')
                uuid = api.generate(
                    self.plainTextEdit.toPlainText(),
                    model_id)

                images = await api.check_generation(self.loop, uuid)

                with open('buff.png', 'wb') as file:
                    file.write(base64.b64decode(''.join(images)))
                self.params['image'] = (images, self.plainTextEdit.toPlainText())

                self.image.setPixmap(QPixmap("buff.png"))
                self.setEnabled(True)
                print("Ended...")
            except KeyError:
                self.setEnabled(True)

                msg = self.create_warning("Астрологи объявляют неделю багов!",
                                          "Изображение отсутствует по причине автомодерации или состояния серверов.")
                msg.exec_()

        for row in self.params.items():
            if row[0] == 'image':
                continue

            if row[1]['checkbox'].isChecked():
                if row[1]['type'] == 'int':
                    self.params[row[0]]['cur'] = randint(row[1]['min'], row[1]['max'])
                if row[1]['type'] == 'str':
                    self.params[row[0]]['cur'] = randint(0, len(row[1]['contents']) - 1)

        self.setup_table()

    def add_param(self):
        self.add_param_form = AddParam(self)
        self.add_param_form.show()

    def rem_param(self):
        if self.tableWidget.item(self.tableWidget.currentRow(), 1) is None:
            msg = self.create_warning("Как можно удалить то, чего нет?", " Вы не выбрали характеристику для удаления!")
            msg.exec_()
            return
        else:
            if str(self.tableWidget.item(self.tableWidget.currentRow(), 1).text()):
                del self.params[str(self.tableWidget.item(self.tableWidget.currentRow(), 1).text())]
                self.tableWidget.removeRow(self.tableWidget.currentRow())

    def edit_param(self):
        self.add_param_form = AddParam(self)

        if self.params[str(self.tableWidget.item(self.tableWidget.currentRow(), 1).text())]['type'] == 'int':
            self.add_param_form.spinBox_min.setValue(
                self.params[str(self.tableWidget.item(self.tableWidget.currentRow(), 1).text())]['min'])
            self.add_param_form.spinBox_max.setValue(
                self.params[str(self.tableWidget.item(self.tableWidget.currentRow(), 1).text())]['max'])

        if self.params[str(self.tableWidget.item(self.tableWidget.currentRow(), 1).text())]['type'] == 'str':
            self.add_param_form.radioButton_1.setChecked(True)
            self.add_param_form.textEdit.setText(
                '\n'.join(self.params[str(self.tableWidget.item(self.tableWidget.currentRow(), 1).text())]['contents']))

        self.add_param_form.lineEdit.setText(str(self.tableWidget.item(self.tableWidget.currentRow(), 1).text()))
        self.add_param_form.radioButton.setEnabled(False)
        self.add_param_form.radioButton_1.setEnabled(False)
        self.add_param_form.label.setText("Изменить характеристику")
        self.add_param_form.show()
