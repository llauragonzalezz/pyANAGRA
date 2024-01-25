"""
Filename:
Developed by Laura González Pizarro
Directed by Joaquín Ezpeleta Mateo
Universidad de Zaragoza
Description:
"""

import re

from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit, QPushButton, QLineEdit, QLabel, QVBoxLayout, QWidget, QMessageBox

import utils


class FirstSet(QMainWindow):
    def __init__(self, traductions, dicc, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.dicc = dicc
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.traductions["tituloConjuntoPRI"])
        self.setGeometry(0, 0, 400, 300)
        # Center window to the middle of the screen
        utils.center_window(self)

        self.text_edit = QPlainTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.text_edit.setReadOnly(True)

        text = ""
        for key in self.dicc.keys():
            text += "Pri(" + key + "): " + " , ".join([str(x) if x is not None else 'ε' for x in self.dicc[key]]) + "\n"

        self.text_edit.setPlainText(text)


class FollowSet(QMainWindow):
    def __init__(self, traductions, dicc, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.dicc = dicc
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.traductions["tituloConjuntoSIG"])
        self.setGeometry(0, 0, 400, 300)
        utils.center_window(self)

        self.text_follow_set = QPlainTextEdit(self)
        self.setCentralWidget(self.text_follow_set)
        self.text_follow_set.setReadOnly(True)

        text = ""
        for key in self.dicc.keys():
            text += "Sig(" + key + "): " + " , ".join([str(x) if x is not None else 'ε' for x in self.dicc[key]]) + "\n"
        self.text_follow_set.setPlainText(text)


class FirstSetSentenceWindow(QMainWindow):
    def __init__(self, traductions, grammar, parent=None):
        super().__init__(parent)
        self.grammar = grammar

        self.setGeometry(0, 0, 300, 100)
        utils.center_window(self)

        self.setWindowTitle(traductions["submenuPRIFormaFrase"])
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.label1 = QLabel(traductions["etiqFormaFrase"])
        self.text_input1 = QLineEdit()
        layout.addWidget(self.label1)
        layout.addWidget(self.text_input1)

        self.label2 = QLabel(traductions["etiqConjFormaFrase"])
        self.text_input2 = QLineEdit()
        self.text_input2.setReadOnly(True)  # Disable
        layout.addWidget(self.label2)
        layout.addWidget(self.text_input2)

        self.ok_button = QPushButton(traductions["etiqCalcular"])
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        # Establecer el widget principal y el
        self.setCentralWidget(central_widget)

    def accept(self): #
        elements = re.findall(r'("[^"]*"|\'[^\']*\'|\S+)', self.text_input1.text())
        if set(elements).difference(self.grammar.non_terminals).difference(self.grammar.terminals) != set():
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Critical)
            error_message.setWindowTitle("Error")
            error_message.setText("error ")

        else:
            first_set_sentence = self.grammar.calculate_first_set_sentence(elements)
            text = " , ".join([str(x) if x is not None else 'ε' for x in first_set_sentence])
            self.text_input2.setText(text)

