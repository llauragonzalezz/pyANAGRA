"""
Filename:
Author: Laura González Pizarro
Description:
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextDocument, QTextCursor, QColor
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QPlainTextEdit, QDesktopWidget, QVBoxLayout, QLabel, QPushButton, \
    QWidget, QLineEdit, QTextEdit, QProgressBar

import conjuntos as conj
import conjuntos_tablas as conj_tab
import simulacion as sim

import LALR
import LL1
import LR
import bottom_up as bu
import grammar


def center_window(window):
    screen = QDesktopWidget().availableGeometry()
    window_size = window.frameGeometry()
    x = (screen.width() - window_size.width()) // 2
    y = (screen.height() - window_size.height()) // 2
    window.move(x, y)


class InformationLog(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Log")
        self.setGeometry(0, 0, 400, 200)
        # Center window to the middle of the screen
        center_window(self)

        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setReadOnly(True)

        self.setCentralWidget(self.text_edit)


    def add_information(self, text):
        self.text_edit.appendPlainText(text)

class InputGrammarWindow(QMainWindow):
    def __init__(self, traductions, type, grammar, table1, table2=None, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.type = type
        if self.type == "LL1":
            self.table_LL1 = table1
        elif self.type == "SLR1":
            self.action_table_SLR = table1
            self.go_to_table_SLR = table2

        elif self.type == "LALR":
            self.action_table_LALR = table1
            self.go_to_table_LALR = table2

        elif self.type == "LR":
            self.action_table_LR = table1
            self.go_to_table_LR = table2
        
        self.grammar = grammar
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Input")
        self.setGeometry(0, 0, 400, 200)
        # Center window to the middle of the screen
        center_window(self)

        layout = QVBoxLayout()

        label = QLabel("Input:")
        layout.addWidget(label)

        self.text_edit = QPlainTextEdit()
        layout.addWidget(self.text_edit)

        boton_aceptar = QPushButton(self.traductions["aceptar"], self)
        boton_aceptar.clicked.connect(self.accept)
        layout.addWidget(boton_aceptar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def accept(self):
        text = self.text_edit.toPlainText()
        self.close()
        if self.type == "LL1":
            table, error = LL1.simulate(self.table_LL1, self.grammar, text + " $")
            new_window = sim.VentanaSimulacion(self.traductions, table, error, self.grammar, self)
        elif self.type == "SLR1":
            table, error = bu.simulate(self.action_table_SLR, self.go_to_table_SLR, text + " $")
            new_window = sim.VentanaSimulacionSLR(self.traductions, table, error, self.grammar, self)
        elif self.type == "LALR":
            table, error = bu.simulate(self.action_table_LALR, self.go_to_table_LALR, text + " $")
            new_window = sim.VentanaSimulacionSLR(self.traductions, table, error, self.grammar, self)

        elif self.type == "LR":
            table, error = bu.simulate(self.action_table_LR, self.go_to_table_LR, text + " $")
            new_window = sim.VentanaSimulacionSLR(self.traductions, table, error, self.grammar, self)
            new_window.show()
        new_window.show()


class FindWindow(QMainWindow):
    def __init__(self, traductions, main_window, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.main_window = main_window
        self.setGeometry(0, 0, 200, 100)
        center_window(self)

        self.setWindowTitle(self.traductions["menuBuscar"])
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.label = QLabel(self.traductions["menuBuscar"]+":")
        self.text_input = QLineEdit()
        layout.addWidget(self.label)
        layout.addWidget(self.text_input)

        self.ok_button = QPushButton(self.traductions["aceptar"])
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)
        self.setCentralWidget(central_widget)

    def accept(self):
        search_word = self.text_input.text()
        text = self.main_window.text_grammar.toPlainText()
        if search_word in text:
            options = QTextDocument.FindWholeWords | QTextDocument.FindCaseSensitively
            cursor = QTextCursor(self.main_window.text_grammar.document())
            selections = []

            while not cursor.isNull():
                cursor = self.main_window.text_grammar.document().find(search_word, cursor, options)
                if not cursor.isNull():
                    sel = QTextEdit.ExtraSelection()
                    sel.format.setBackground(QColor("green"))  # Cambiar el color de fondo a verde
                    sel.cursor = cursor
                    selections.append(sel)

            self.main_window.text_grammar.setExtraSelections(selections)

        else: # fixme poner mensaje desde traductions
            QMessageBox.information(self, 'Mensaje', f'La palabra "{search_word}" no se encontró en el texto.')

class RemplaceWindow(QMainWindow):
    def __init__(self, traductions, main_window, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.main_window = main_window
        self.setGeometry(0, 0, 200, 100)
        center_window(self)

        self.setWindowTitle(self.traductions["tituloReemplazar"])
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.label1 = QLabel(self.traductions["etiqTexto"])
        self.text_input1 = QLineEdit()
        layout.addWidget(self.label1)
        layout.addWidget(self.text_input1)

        self.label2 = QLabel(self.traductions["etiqTextoReemplazar"])
        self.text_input2 = QLineEdit()
        layout.addWidget(self.label2)
        layout.addWidget(self.text_input2)

        self.ok_button = QPushButton(self.traductions["aceptar"])
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setCentralWidget(central_widget)

    def accept(self):
        old = self.text_input1.text()
        new = self.text_input2.text()
        text = self.main_window.text_grammar.toPlainText()

        if old in text:
            options = QTextDocument.FindWholeWords | QTextDocument.FindCaseSensitively
            cursor = QTextCursor(self.main_window.text_grammar.document())
            selections = []

            while not cursor.isNull():
                cursor = self.main_window.text_grammar.document().find(old, cursor, options)
                if not cursor.isNull():
                    cursor.insertText(new)

            self.main_window.text_grammar.setExtraSelections(selections)
            self.close()

        elif old: # fixme igual que en buscar
            QMessageBox.information(self, 'Error', f'La palabra "{old}" no se encontró en el texto.')


class ProgressBarWindow(QMainWindow):
    def __init__(self, text, stop_func, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.text = text
        self.stop_func = stop_func
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Procesando...')
        self.setGeometry(300, 300, 300, 150)
        center_window(self)

        self.message_label = QLabel(self.text, self)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setGeometry(30, 20, 240, 40)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(30, 70, 240, 25)

        self.progress_bar.setRange(0, 0)  # No percentage

        self.stop_button = QPushButton('Cancelar', self)
        self.stop_button.setGeometry(90, 100, 120, 25)
        self.stop_button.clicked.connect(self.stop_func)

    def stopProgress(self):
        self.close()