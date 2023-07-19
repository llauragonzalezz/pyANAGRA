import os
import sys
import json


from PyQt5.QtGui import QKeySequence, QClipboard, QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow,  QWidgetAction, \
    QPlainTextEdit, QTableWidgetItem, QTableWidget


class NewApplication:
    def __init__(self):
        super().__init__(sys.argv)

class ConjuntoPrimero(QMainWindow):
    def __init__(self, diccionario, parent=None):
        super().__init__(parent)
        self.initUI(diccionario)

    def initUI(self, diccionario):
        self.setGeometry(100, 100, 400, 300)

        self.setWindowTitle("Conjunto primero")
        self.text_edit = QPlainTextEdit(self)
        self.setCentralWidget(self.text_edit)
        font = self.text_edit.font()
        font.setPointSize(14) # TODO: PONER PARA CAMBIAR EL TAMAÑO DE LA LETRA?? Y FUENTE (?)
        self.text_edit.setFont(font)
        self.text_edit.setReadOnly(True)
        primero = diccionario
        texto = ""
        for key in primero.keys():  # FIXME LOS ESPACIOS NO FUNCIONAN TIENE QUE SER CARACTERES NO IMPRIMIBLES COMO \u00A0
            # FIXME PONGO EL BOTON DE CERRAR COMO EN ANAGRA 2
            texto += "Pri(" + key + "): " + " , ".join([str(x) if x is not None else 'ε' for x in primero[key]]) + "\n"

        print(texto)
        self.text_edit.setPlainText(texto)


class ConjuntoSiguiente(QMainWindow):
    def __init__(self, diccionario, parent=None):
        super().__init__(parent)
        self.initUI(diccionario)

    def initUI(self, diccionario):
        self.setWindowTitle("Conjunto siguiente")
        self.text_edit = QPlainTextEdit(self)
        self.setCentralWidget(self.text_edit)
        font = self.text_edit.font()
        font.setPointSize(14)
        self.text_edit.setFont(font)
        self.text_edit.setReadOnly(True)

        siguiente = diccionario
        texto = ""
        for key in siguiente.keys():
            texto += "Sig(" + key + "): " + " , ".join([str(x) if x is not None else 'ε' for x in siguiente[key]]) + "\n"

        self.text_edit.setPlainText(texto)

class TablaAnalisis(QMainWindow):
    def __init__(self, diccionario, parent=None):
        super().__init__(parent)
        self.initUI(diccionario)

    def initUI(self, tabla):
        self.setWindowTitle("Tabla analisis")
        print(tabla)
        no_terminales = sorted(set(k[0] for k in tabla.keys()))
        terminales = sorted(set(k[1] for k in tabla.keys()))

        table = QTableWidget()
        table.setRowCount(len(no_terminales))
        table.setColumnCount(len(terminales))
        table.setVerticalHeaderLabels(no_terminales)
        table.setHorizontalHeaderLabels(terminales)

        for fila, columna in tabla.keys():
            indice_fila = no_terminales.index(fila)
            indice_columna = terminales.index(columna)
            if tabla[(fila, columna)]:
                if tabla[(fila, columna)][0] is None:
                    item = str(fila) + "  → ε"
                else:
                    item = "{} → {}".format(fila, "  ".join(
                        [str(x) if x is not None else 'ε' for x in tabla[(fila, columna)][0]]))
            else:
                item = ""
            table.setItem(indice_fila, indice_columna, QTableWidgetItem(item))

        self.setCentralWidget(table)
class TablaSimulacion(QMainWindow):
    def __init__(self, diccionario, parent=None):
        super().__init__(parent)
        self.initUI(diccionario)

    def initUI(self, tabla):
        print("tabla:", tabla)
        self.setWindowTitle("Tabla simulacion")
        table = QTableWidget(len(tabla), 3)
        table.setHorizontalHeaderLabels(["Pila", "Entrada", "Producción usada(salida)"])

        for i, tupla in enumerate(tabla.values()):
            pila = tupla[0]
            item = QTableWidgetItem("".join(pila))
            table.setItem(i, 0, item)

            cadena = tupla[1]
            item = QTableWidgetItem(cadena)
            table.setItem(i, 1, item)

            if len(tupla) == 2:
                item = QTableWidgetItem("")
                table.setItem(i, 2, item)
            else:
                produccion = tupla[2]
                if produccion:
                    if produccion[1][0] is None:
                        item = str(produccion[0]) + "  → ε"
                    else:
                        item = "{} → {}".format(produccion[0], "  ".join(str(x) for x in produccion[1][0]))
                else:
                    item = ""

                table.setItem(i, 2, QTableWidgetItem(item))

        self.setCentralWidget(table)

class MainWindow(QMainWindow):

    def __init__(self, parametro, diccionario):
        super().__init__()
        self.setGeometry(100, 100, 400, 300)

        if parametro == "-p":
            self.setWindowTitle("Conjunto primero")
            self.text_edit = QPlainTextEdit(self)
            self.setCentralWidget(self.text_edit)
            font = self.text_edit.font()
            font.setPointSize(14) # TODO: PONER PARA CAMBIAR EL TAMAÑO DE LA LETRA?? Y FUENTE (?)
            self.text_edit.setFont(font)
            self.text_edit.setReadOnly(True)

            self.mostrar_conjunto_primero(diccionario)
        elif sys.argv[1] == "-s":
            self.setWindowTitle("Conjunto siguiente")
            self.text_edit = QPlainTextEdit(self)
            self.setCentralWidget(self.text_edit)
            font = self.text_edit.font()
            font.setPointSize(14)
            self.text_edit.setFont(font)
            self.text_edit.setReadOnly(True)

            self.mostrar_conjunto_siguiente()

        elif sys.argv[1] == "-t":
            self.setWindowTitle("Tabla analisis")
            self.mostrar_tabla()

        elif sys.argv[1] == "-sim":
            self.setWindowTitle("Tabla simulacion")
            self.mostrar_tabla_simulacion()

    def mostrar_conjunto_primero(self, diccionario):
        # Cargando el archivo JSON
        #with open(sys.argv[2], "r") as archivo_json:
        #    contenido_json = archivo_json.read()

        #os.remove(sys.argv[2]) # borramos el fichero temporal

        # Convirtiendo el contenido en un diccionario
        #primero = json.loads(contenido_json)
        primero = diccionario
        texto = ""
        for key in primero.keys(): # FIXME LOS ESPACIOS NO FUNCIONAN TIENE QUE SER CARACTERES NO IMPRIMIBLES COMO \u00A0
            # FIXME PONGO EL BOTON DE CERRAR COMO EN ANAGRA 2
            texto += "Pri(" + key + "): " + " , ".join([str(x) if x is not None else 'ε' for x in primero[key]]) + "\n"

        self.text_edit.setPlainText(texto)

    def mostrar_conjunto_siguiente(self):
        # Cargando el archivo JSON
        with open(sys.argv[2], "r") as archivo_json:
            contenido_json = archivo_json.read()

        os.remove(sys.argv[2]) # borramos el fichero temporal

        # Convirtiendo el contenido en un diccionario
        siguiente = json.loads(contenido_json)
        texto = ""
        for key in siguiente.keys():
            texto += "Sig(" + key + "): " + " , ".join([str(x) if x is not None else 'ε' for x in siguiente[key]]) + "\n"

        self.text_edit.setPlainText(texto)

    def mostrar_tabla(self):
        # Cargando el archivo JSON
        with open("mi_diccionario.json", "r") as archivo_json:
            contenido_json = archivo_json.read()
        os.remove(sys.argv[2])  # borramos el fichero temporal

        # Convirtiendo el contenido en un diccionario
        tabla = {tuple(s.replace("\\", "") for s in k.split(",")): v for k, v in json.loads(contenido_json).items()}

        no_terminales = sorted(set(k[0] for k in tabla.keys()))
        terminales = sorted(set(k[1] for k in tabla.keys()))

        table = QTableWidget()
        table.setRowCount(len(no_terminales))
        table.setColumnCount(len(terminales))
        table.setVerticalHeaderLabels(no_terminales)
        table.setHorizontalHeaderLabels(terminales)

        for fila, columna in tabla.keys():
            indice_fila = no_terminales.index(fila)
            indice_columna = terminales.index(columna)
            if tabla[(fila, columna)]:
                if tabla[(fila, columna)][0] is None:
                    item = str(fila) + "  → ε"
                else:
                    item = "{} → {}".format(fila, "  ".join([str(x) if x is not None else 'ε' for x in tabla[(fila, columna)][0]]))
            else:
                item = ""
            table.setItem(indice_fila, indice_columna, QTableWidgetItem(item))

        self.setCentralWidget(table)

    def mostrar_tabla_simulacion(self):
        # Cargando el archivo JSON
        with open("mi_diccionario.json", "r") as archivo_json:
            contenido_json = archivo_json.read()
        os.remove(sys.argv[2])  # borramos el fichero temporal

        # Convirtiendo el contenido en un diccionario
        tabla = json.loads(contenido_json)

        table = QTableWidget(len(tabla), 3)
        table.setHorizontalHeaderLabels(["Pila", "Entrada", "Producción usada(salida)"])

        for i, tupla in enumerate(tabla.values()):
            pila = tupla[0]
            item = QTableWidgetItem("".join(pila))
            table.setItem(i, 0, item)

            cadena = tupla[1]
            item = QTableWidgetItem(cadena)
            table.setItem(i, 1, item)

            if len(tupla) == 2:
                item = QTableWidgetItem("")
                table.setItem(i, 2, item)
            else:
                produccion = tupla[2]
                if produccion:
                    if produccion[1][0] is None:
                        item = str(produccion[0]) + "  → ε"
                    else:
                        item = "{} → {}".format(produccion[0], "  ".join(str(x) for x in produccion[1][0]))
                else:
                    item = ""

                table.setItem(i, 2, QTableWidgetItem(item))

        self.setCentralWidget(table)


#if __name__ == "__main__":
#    app = QApplication(sys.argv)
#    ventana = MainWindow()
#    ventana.show()
#    app.exec_()
#    sys.exit()


def main(parametro, diccionario):
    app = QApplication(sys.argv)
    ventana = MainWindow(parametro, diccionario)
    ventana.show()
    app.exec_()
    sys.exit()

    #widget.show()
    #widget.resize(800, 600)

    #sys.exit(app.exec())

#def run_graph_viewer(graph):
    #main(graph)