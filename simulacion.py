import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QPlainTextEdit, QLabel, QPushButton, \
    QHBoxLayout, QApplication, QDesktopWidget

import tree


class VentanaSimulacion(QMainWindow):
    def __init__(self, table, start_token, terminals, non_terminals, parent=None):
        super().__init__(parent)
        self.table = table
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.iter = 0
        self.tree_window = tree.MainWindow(start_token=start_token, parent=self)
        self.tree_window.show()
        self.initUI()

    def initUI(self):
        self.setGeometry(0, 0, 450, 150)
        screen = QDesktopWidget().availableGeometry()
        window_size = self.frameGeometry()
        x = screen.width() // 2 - window_size.width()
        y = screen.height() // 2 - window_size.height()
        self.move(x, y)

        self.setWindowTitle('Ventana de simulación')
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
        label1 = QLabel("Secuencia de producciones")
        label2 = QLabel("Pila")
        label3 = QLabel("Entrada")
        label4 = QLabel("Texto a analizar")

        # Aling labels center
        label1.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        label2.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        label3.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        label4.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        # Buttons
        self.btn_retrocede = QPushButton("Retrocede")
        self.btn_retrocede.clicked.connect(self.retroceder)
        self.btn_retrocede.setEnabled(False)

        self.btn_avanza = QPushButton("Avanza")
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

        # Establecer el widget principal y el
        self.setCentralWidget(central_widget)

    def retroceder(self):
        # Tree window
        if self.table[self.iter][2] and self.table[self.iter][2][1] is not None:
            for nodo in self.table[self.iter][2][1]:
                print("Borramos el nodo:", nodo[1])
                self.tree_window.delete_node(nodo[1])

        self.iter -= 1
        if self.iter == 0:
            self.btn_retrocede.setEnabled(False)
        self.btn_avanza.setEnabled(True)

        self.text_production.setPlainText(write_production(self.table[self.iter][2]))
        self.text_stack.setPlainText(write_stack(self.table[self.iter][0]))
        #self.text_edit3.setPlainText(self.table[self.iter][1])
        self.text_input.setPlainText(self.table[self.iter][1][:-1])


    def avanzar(self): # '(''x'';''(''x'')'')'
        self.iter += 1
        if self.iter == len(self.table)-1:
            self.btn_avanza.setEnabled(False)
        self.btn_retrocede.setEnabled(True)

        self.text_production.setPlainText(write_production(self.table[self.iter][2]))
        self.text_stack.setPlainText(write_stack(self.table[self.iter][0]))
        #self.text_edit3.setPlainText(self.table[self.iter][1])
        self.text_input.setPlainText(self.table[self.iter][1][:-1])

        # Update tree window
        print(self.table[self.iter][2])
        if self.table[self.iter][2] and self.table[self.iter][2][1] is not None:
            for nodo in self.table[self.iter][2][1]:
                self.tree_window.add_node(nodo[1], nodo[0], nodo[0] in self.terminals, self.table[self.iter][2][0][1])

def write_stack(stack):
    string = ""
    for elem in stack:
        string += elem[0]
    return string

def write_production(tuple):
    if tuple == ():
        return ""
    elif tuple[1] is None:
        return str(tuple[0][0]) + "  → ε"
    else:
        string = tuple[0][0] + "→"
        for elem in tuple[1]:
            string += elem[0]

        return string
