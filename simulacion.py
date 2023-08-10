import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QPlainTextEdit, QLabel, QPushButton, \
    QHBoxLayout, QApplication

import tree


class VentanaSimulacion(QMainWindow):
    def __init__(self, tabla=None, parent=None):
        super().__init__(parent)
        self.tabla = tabla
        self.iter = 0
        self.initUI()

    def initUI(self):
        self.setGeometry(400, 200, 450, 150)
        self.setWindowTitle('Ventana de simulación')
        central_widget = QWidget(self)
        grid_layout = QGridLayout(central_widget)

        # Crear los QPlainTextEdit y agregarlos al diseño de cuadrícula
        self.text_edit1 = QPlainTextEdit()
        self.text_edit1.setReadOnly(True)

        self.text_edit2 = QPlainTextEdit()
        self.text_edit2.setReadOnly(True)

        self.text_edit3 = QPlainTextEdit()
        self.text_edit3.setReadOnly(True)
        #self.text_edit3.setPlainText(self.tabla[self.iter][1])  # Escribimos el fichero

        self.text_edit4 = QPlainTextEdit()
        self.text_edit4.setReadOnly(True)
        #self.text_edit4.setPlainText(self.tabla[self.iter][1][:-1])  # Escribimos el fichero

        # Crear las etiquetas y los QPlainTextEdit
        label1 = QLabel("Secuencia de producciones")
        label2 = QLabel("Pila")
        label3 = QLabel("Entrada")
        label4 = QLabel("Texto a analizar")

        # Establecer la alineación del texto en las etiquetas
        label1.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        label2.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        label3.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        label4.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        # Crear los botones
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

        grid_layout.addWidget(self.text_edit1, 1, 0)
        grid_layout.addWidget(self.text_edit2, 1, 1)
        grid_layout.addWidget(self.text_edit3, 3, 0, 1, 3)
        grid_layout.addWidget(self.text_edit4, 5, 0, 1, 3)

        # Agregar el layout de los botones al diseño de cuadrícula
        grid_layout.addLayout(button_layout, 6, 0, 1, 3)  # Fila 4, Columna 0, Ocupa 1 fila y 3 columnas

        # Establecer el widget principal y el
        self.setCentralWidget(central_widget)



    def retroceder(self):
        # Tree window
        #for nodo in self.tabla[self.iter][1][1]:
        #    self.tree_window.delete_node(nodo[1])

        self.iter -= 1
        if self.iter == 0:
            self.btn_retrocede.setEnabled(False)
        self.btn_avanza.setEnabled(True)

        self.text_edit1.setPlainText(write_production(self.tabla[self.iter][2]))
        self.text_edit2.setPlainText(' '.join(self.tabla[self.iter][0]))
        self.text_edit3.setPlainText(self.tabla[self.iter][1])
        self.text_edit4.setPlainText(self.tabla[self.iter][1][:-1])


    def avanzar(self): # '(''x'';''(''x'')'')'
        self.iter += 1
        if self.iter == len(self.tabla):
            self.btn_avanza.setEnabled(False)
        self.btn_retrocede.setEnabled(True)

        self.text_edit1.setPlainText(write_production(self.tabla[self.iter][2]))
        self.text_edit2.setPlainText(write_stack(self.tabla[self.iter][0]))
        self.text_edit3.setPlainText(self.tabla[self.iter][1])
        self.text_edit4.setPlainText(self.tabla[self.iter][1][:-1])

        # Tree window
        #for nodo in self.tabla[self.iter][1][1]:
        #    self.tree_window.add_node(nodo[1], nodo[0], self.tabla[self.iter][1][0][1])


def write_stack(stack):
    string = ""
    for elem in stack:
        string += elem[0]
    return string

def write_production(tuple):
    print("tupla", tuple)
    if tuple == ():
        return ""
    elif tuple[1] is None:
        return str(tuple[0][0]) + "  → ε"
    else:
        string = tuple[0][0] + "→"
        for elem in tuple[1]:
            print(elem[0])
            string += elem[0]

        return string

if __name__ == "__main__":

    app = QApplication(sys.argv)
    widget = VentanaSimulacion()
    widget.show()
    widget.resize(800, 600)
    sys.exit(app.exec())
