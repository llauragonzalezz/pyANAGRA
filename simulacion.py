"""
Filename:
Developed by Laura González Pizarro
Directed by Joaquín Ezpeleta Mateo
Universidad de Zaragoza
Description:
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QPlainTextEdit, QLabel, QPushButton, \
    QHBoxLayout, QDesktopWidget, QMessageBox

import tree


class VentanaSimulacion(QMainWindow):
    def __init__(self, traductions, table, error, grammar, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.table = table
        self.error = error
        self.terminals = grammar.terminals
        self.non_terminals = grammar.non_terminals
        self.iter = 0
        self.tree_window = tree.TreeWindow(traductions=traductions, parent=self)
        self.tree_window.show()
        self.stack = []
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 500, 450)
        screen = QDesktopWidget().availableGeometry()
        window_size = self.frameGeometry()
        x = screen.width() // 2 - window_size.width()
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

        self.setWindowTitle(self.traductions["tituloVentanaSimulacion"])
        central_widget = QWidget(self)
        grid_layout = QGridLayout(central_widget)

        # Crear los QPlainTextEdit y agregarlos al diseño de cuadrícula
        self.text_production = QPlainTextEdit()
        self.text_production.setReadOnly(True)

        self.text_stack = QPlainTextEdit()
        self.text_stack.setReadOnly(True)

        self.text_edit3 = QPlainTextEdit()
        self.text_edit3.setReadOnly(True)
        self.text_edit3.setPlainText(self.table[self.iter][1])  # Escribimos el fichero

        self.text_input = QPlainTextEdit()
        self.text_input.setReadOnly(True)
        self.text_input.setPlainText(self.table[self.iter][1][:-1])  # Escribimos el fichero

        # Crear las etiquetas y los QPlainTextEdit self.traductions["tituloVentanaSimulacion"]
        label1 = QLabel(self.traductions["etiqSeq"])
        label2 = QLabel(self.traductions["etiqPila"])
        label3 = QLabel(self.traductions["etiqEntrada"])
        label4 = QLabel(self.traductions["etiqTextoAnalizar"])

        # Aling labels center
        label1.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        label2.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        label3.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        label4.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        # Buttons
        self.btn_retrocede = QPushButton(self.traductions["etiqRetroceder"])
        self.btn_retrocede.clicked.connect(self.retroceder)
        self.btn_retrocede.setEnabled(False)

        self.btn_avanza = QPushButton(self.traductions["etiqAvanzar"])
        self.btn_avanza.clicked.connect(self.avanzar)

        # Crear un layout horizontal para los botones y agregarlos
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_retrocede)
        button_layout.addWidget(self.btn_avanza)

        # Agregar las etiquetas, los QPlainTextEdit y los botones al diseño de cuadrícula
        grid_layout.addWidget(label1, 0, 0)
        grid_layout.addWidget(label2, 0, 1)
        grid_layout.addWidget(label3, 2, 0, 1, 2)
        grid_layout.addWidget(label4, 4, 0, 1, 2)

        grid_layout.addWidget(self.text_production, 1, 0)
        grid_layout.addWidget(self.text_stack, 1, 1)
        grid_layout.addWidget(self.text_edit3, 3, 0, 1, 3)
        grid_layout.addWidget(self.text_input, 5, 0, 1, 3)

        # Agregar el layout de los botones al diseño de cuadrícula
        grid_layout.addLayout(button_layout, 6, 0, 1, 3)

        self.text_edit3.setFixedHeight(4 * self.text_production.fontMetrics().lineSpacing())
        self.text_input.setFixedHeight(4 * self.text_stack.fontMetrics().lineSpacing())

        # Establecer el widget principal y el
        self.setCentralWidget(central_widget)

    def retroceder(self):
        # Tree window
        if self.iter == 1:
            self.tree_window.delete_node(self.table[0][2][0][1])
        elif self.iter > 0 and self.table[self.iter-1][2] and self.table[self.iter-1][2][1] is not None:
            for nodo in self.table[self.iter-1][2][1]:
                self.tree_window.delete_node(nodo[1])

        self.iter -= 1
        if self.iter == 0:
            self.btn_retrocede.setEnabled(False)
        self.btn_avanza.setEnabled(True)

        self.text_production.setPlainText(write_production([sublist[2] for sublist in self.table[:self.iter]]))
        self.text_stack.setPlainText(write_stack(self.table[self.iter][0]))
        #self.text_edit3.setPlainText(self.table[self.iter][1])
        self.text_input.setPlainText(self.table[self.iter][1][:-1])


    def avanzar(self): # '(''x'';''(''x'')'')'
        self.iter += 1
        self.btn_retrocede.setEnabled(True)

        self.text_production.setPlainText(write_production([sublist[2] for sublist in self.table[:self.iter]]))
        self.text_stack.setPlainText(write_stack(self.table[self.iter][0]))
        #self.text_edit3.setPlainText(self.table[self.iter][1])
        self.text_input.setPlainText(self.table[self.iter][1][:-1])

        # Update tree window
        if self.iter == 1:
            self.tree_window.create_node(self.table[0][2][0][1], self.table[0][2][0][0], self.table[0][2][0][0] in self.terminals)
        elif self.iter > 0 and self.table[self.iter-1][2] and self.table[self.iter-1][2][1] is not None:
            for nodo in self.table[self.iter-1][2][1]:
                self.tree_window.add_node_to_parent(nodo[1], nodo[0], nodo[0] in self.terminals,
                                                    self.table[self.iter-1][2][0][1])
        if self.iter == len(self.table)-1:
            self.btn_avanza.setEnabled(False)

            message_box = QMessageBox()
            message_box.setWindowTitle(self.traductions["mensaje"])
            if self.error:
                message_box.setIcon(QMessageBox.Critical)
                message_box.setText(self.traductions["mensajeCadenaNoAceptada"])
            else:
                message_box.setText(self.traductions["mensajeCadenaAceptada"])

            message_box.exec_()



class VentanaSimulacionSLR(QMainWindow):
    def __init__(self, traductions, table, error, grammar, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.table = table
        self.error = error
        self.terminals = grammar.terminals
        self.non_terminals = grammar.non_terminals
        self.iter = 0
        self.tree_window = tree.TreeWindow(traductions=traductions, parent=self)
        self.tree_window.show()
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 500, 450)
        screen = QDesktopWidget().availableGeometry()
        window_size = self.frameGeometry()
        x = screen.width() // 2 - window_size.width()
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

        self.setWindowTitle(self.traductions["tituloVentanaSimulacion"])
        central_widget = QWidget(self)
        grid_layout = QGridLayout(central_widget)

        # Crear los QPlainTextEdit y agregarlos al diseño de cuadrícula
        self.text_production = QPlainTextEdit()
        self.text_production.setReadOnly(True)

        self.text_stack = QPlainTextEdit()
        self.text_stack.setReadOnly(True)

        self.text_edit3 = QPlainTextEdit()
        self.text_edit3.setReadOnly(True)
        self.text_edit3.setPlainText(self.table[self.iter][1])  # Escribimos el fichero

        self.text_input = QPlainTextEdit()
        self.text_input.setReadOnly(True)
        self.text_input.setPlainText(self.table[self.iter][1][:-1])  # Escribimos el fichero

        # Crear las etiquetas y los QPlainTextEdit
        label1 = QLabel(self.traductions["etiqSeq"])
        label2 = QLabel(self.traductions["etiqPila"])
        label3 = QLabel(self.traductions["etiqEntrada"])
        label4 = QLabel(self.traductions["etiqTextoAnalizar"])

        # Aling labels center
        label1.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        label2.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        label3.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        label4.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        # Buttons
        self.btn_retrocede = QPushButton(self.traductions["etiqRetroceder"])
        self.btn_retrocede.clicked.connect(self.retroceder)
        self.btn_retrocede.setEnabled(False)

        self.btn_avanza = QPushButton(self.traductions["etiqAvanzar"])
        self.btn_avanza.clicked.connect(self.avanzar)

        # Crear un layout horizontal para los botones y agregarlos
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_retrocede)
        button_layout.addWidget(self.btn_avanza)

        # Agregar las etiquetas, los QPlainTextEdit y los botones al diseño de cuadrícula
        grid_layout.addWidget(label1, 0, 0)
        grid_layout.addWidget(label2, 0, 1)
        grid_layout.addWidget(label3, 2, 0, 1, 2)
        grid_layout.addWidget(label4, 4, 0, 1, 2)

        grid_layout.addWidget(self.text_production, 1, 0)
        grid_layout.addWidget(self.text_stack, 1, 1)
        grid_layout.addWidget(self.text_edit3, 3, 0, 1, 3)
        grid_layout.addWidget(self.text_input, 5, 0, 1, 3)

        # Agregar el layout de los botones al diseño de cuadrícula
        grid_layout.addLayout(button_layout, 6, 0, 1, 3)
        #self.text_production.setFixedHeight(7 * self.text_production.fontMetrics().lineSpacing())
        #self.text_stack.setFixedHeight(7 * self.text_stack.fontMetrics().lineSpacing())
        self.text_edit3.setFixedHeight(4 * self.text_production.fontMetrics().lineSpacing())
        self.text_input.setFixedHeight(4 * self.text_stack.fontMetrics().lineSpacing())

        # Establecer el widget principal y el
        self.setCentralWidget(central_widget)

    def retroceder(self):
        # Tree window
        if self.table[self.iter][2] != ():
            self.tree_window.delete_parent(self.table[self.iter][2][0][1])

        if self.table[self.iter][3] != ():
            self.tree_window.delete_node(self.table[self.iter][3][1])


        self.iter -= 1
        if self.iter == 0:
            self.btn_retrocede.setEnabled(False)
        self.btn_avanza.setEnabled(True)

        self.text_production.setPlainText(write_production([sublist[2] for sublist in self.table[:self.iter+1]]))
        self.text_stack.setPlainText(write_stack(self.table[self.iter][0]))
        #self.text_edit3.setPlainText(self.table[self.iter][1])

        self.text_input.setPlainText(self.table[self.iter][1][:-1])


    def avanzar(self):  # '(''x'';''(''x'')'')'
        self.iter += 1
        self.btn_retrocede.setEnabled(True)
        self.text_production.setPlainText(write_production([sublist[2] for sublist in self.table[:self.iter+1]]))
        self.text_stack.setPlainText(write_stack(self.table[self.iter][0]))
        #self.text_edit3.setPlainText(self.table[self.iter][1])
        self.text_input.setPlainText(self.table[self.iter][1][:-1])

        # Update tree window
        if self.table[self.iter][2] and self.table[self.iter][2][1] is not None:
            self.tree_window.add_parent_to_nodes(self.table[self.iter][2][0][1], self.table[self.iter][2][0][0],
                                                 self.table[self.iter][2][0][0] in self.terminals,
                                                 [tupla[1] for tupla in self.table[self.iter][2][1]])

        if self.table[self.iter][3] != ():
            self.tree_window.create_node(self.table[self.iter][3][1], self.table[self.iter][3][0],
                                         self.table[self.iter][3][0] in self.terminals)

        if self.iter == len(self.table) - 1:
            self.btn_avanza.setEnabled(False)

            message_box = QMessageBox()
            message_box.setWindowTitle(self.traductions["mensaje"])
            if self.error:
                message_box.setIcon(QMessageBox.Critical)
                message_box.setText(self.traductions["mensajeCadenaNoAceptada"])
            else:
                message_box.setText(self.traductions["mensajeCadenaAceptada"])

            message_box.exec_()


def write_stack(stack):
    stack = reversed(stack)
    string = ""
    for elem in stack:
        string = str(elem[0]) + " \n" + string
    
    return string
# id '+' id


def write_production(tuple_list):
    string = ""
    for tuple in tuple_list:
        if tuple != () and len(tuple) > 1:
            if tuple[1] is None:
                string += str(tuple[0][0]) + "  → ε \n"
            else:
                string += tuple[0][0] + "→ "
                for elem in reversed(tuple[1]):
                    string += elem[0] + " "
                string += "\n"
    return string
