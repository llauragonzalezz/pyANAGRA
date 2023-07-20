import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QPlainTextEdit, QLabel, QPushButton, \
    QHBoxLayout

class VentanaSimulacion(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setGeometry(400, 200, 450, 150)
        self.setWindowTitle('Ventana de Mensaje')
        central_widget = QWidget(self)
        grid_layout = QGridLayout(central_widget)

        # Crear los QPlainTextEdit y agregarlos al diseño de cuadrícula
        text_edit1 = QPlainTextEdit()
        text_edit2 = QPlainTextEdit()
        text_edit3 = QPlainTextEdit()
        text_edit4 = QPlainTextEdit()

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
        btn_retrocede = QPushButton("Retrocede")
        btn_retrocede.triggered.connect(self.retroceder)

        btn_avanza = QPushButton("Avanza")
        btn_avanza.triggered.connect(self.avanzar)

        # Crear un layout horizontal para los botones y agregarlos
        button_layout = QHBoxLayout()
        button_layout.addWidget(btn_retrocede)
        button_layout.addWidget(btn_avanza)

        # Agregar las etiquetas, los QPlainTextEdit y los botones al diseño de cuadrícula
        grid_layout.addWidget(label1, 0, 0)
        grid_layout.addWidget(label2, 0, 1)
        grid_layout.addWidget(label3, 2, 0, 1, 2)
        grid_layout.addWidget(label4, 4, 0, 1, 2)

        grid_layout.addWidget(text_edit1, 1, 0)
        grid_layout.addWidget(text_edit2, 1, 1)
        grid_layout.addWidget(text_edit3, 3, 0, 1, 3)
        grid_layout.addWidget(text_edit4, 5, 0, 1, 3)

        # Agregar el layout de los botones al diseño de cuadrícula
        grid_layout.addLayout(button_layout, 6, 0, 1, 3)  # Fila 4, Columna 0, Ocupa 1 fila y 3 columnas

        # Establecer el widget principal y el
        self.setCentralWidget(central_widget)

    def retroceder(self):
        print()

    def avanzar(self):
        print()

