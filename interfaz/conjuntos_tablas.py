from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit, QTableWidgetItem, QTableWidget, QDesktopWidget


def center_window(window):
    screen = QDesktopWidget().availableGeometry()
    window_size = window.frameGeometry()
    x = (screen.width() - window_size.width()) // 2
    y = (screen.height() - window_size.height()) // 2
    window.move(x, y)

class FirstSet(QMainWindow):
    def __init__(self, dicc, parent=None):
        super().__init__(parent)
        self.dicc = dicc
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Conjunto primero")
        self.setGeometry(0, 0, 400, 300)
        # Center window to the middle of the screen
        center_window(self)

        self.text_edit = QPlainTextEdit(self)
        self.setCentralWidget(self.text_edit)
        #font = self.text_edit.font()
        #font.setPointSize(14) # TODO: PONER PARA CAMBIAR EL TAMAÑO DE LA LETRA?? Y FUENTE (?)
        #self.text_edit.setFont(font)
        self.text_edit.setReadOnly(True)

        text = ""
        for key in self.dicc.keys():  # FIXME LOS ESPACIOS NO FUNCIONAN TIENE QUE SER CARACTERES NO IMPRIMIBLES COMO \u00A0
            text += "Pri(" + key + "): " + " , ".join([str(x) if x is not None else 'ε' for x in self.dicc[key]]) + "\n"

        self.text_edit.setPlainText(text)


class FollowSet(QMainWindow):
    def __init__(self, dicc, parent=None):
        super().__init__(parent)
        self.dicc = dicc
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Conjunto siguiente")
        self.setGeometry(0, 0, 400, 300)
        # Center window to the middle of the screen
        center_window(self)

        self.text_follow_set = QPlainTextEdit(self)
        self.setCentralWidget(self.text_follow_set)
        #font = self.text_edit.font()
        #font.setPointSize(14)
        #self.text_edit.setFont(font)
        self.text_follow_set.setReadOnly(True)

        text = ""
        for key in self.dicc.keys():
            text += "Sig(" + key + "): " + " , ".join([str(x) if x is not None else 'ε' for x in self.dicc[key]]) + "\n"
        self.text_follow_set.setPlainText(text)


class AnalysisTable(QMainWindow):
    def __init__(self, dicc, parent=None):
        super().__init__(parent)
        self.dicc = dicc
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Tabla analisis")

        non_terminals = sorted(set(k[0] for k in self.dicc.keys()))
        terminals = sorted(set(k[1] for k in self.dicc.keys()))

        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable edit cell
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setRowCount(len(non_terminals))
        table.setColumnCount(len(terminals))
        table.setVerticalHeaderLabels(non_terminals)
        table.setHorizontalHeaderLabels(terminals)

        row_height = table.rowHeight(0)
        for row, col in self.dicc.keys():
            item_text = ""
            if self.dicc[(row, col)]:
                for i, prod in enumerate(self.dicc[(row, col)]):
                    if prod is None:
                        item_text += str(row) + "  → ε"
                    else:
                        item_text += "{} → {}".format(row, "  ".join([str(x) for x in prod]))

                    if i < len(self.dicc[(row, col)]) - 1:
                        item_text += "\n"

            item = QTableWidgetItem(item_text)

            if len(self.dicc[(row, col)]) > 1:
                # Adapt margins
                if table.rowHeight(non_terminals.index(row)) < len(self.dicc[(row, col)] * row_height):
                    table.setRowHeight(non_terminals.index(row), len(self.dicc[(row, col)]) * row_height)

                item.setBackground(QColor("red"))   # LL1 conflict

            table.setItem(non_terminals.index(row), terminals.index(col), item)

        self.setCentralWidget(table)
        self.resize(table.horizontalHeader().length() + 20,
                    table.verticalHeader().length() + 30)

        # Center window to the middle of the screen
        center_window(self)

class SimulationTable(QMainWindow):
    def __init__(self, dicc, parent=None):
        super().__init__(parent)
        self.dicc = dicc
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Tabla simulacion")
        # Center window to the middle of the screen
        center_window(self)

        table = QTableWidget(len(self.dicc), 3)
        table.setHorizontalHeaderLabels(["Pila", "Entrada", "Producción usada(salida)"])

        for i, tuple in enumerate(self.dicc.values()):
            stack = tuple[0]
            item = QTableWidgetItem("".join(stack))
            table.setItem(i, 0, item)

            input = tuple[1]
            item = QTableWidgetItem(input)
            table.setItem(i, 1, item)

            if len(tuple) == 2:
                item = QTableWidgetItem("")
                table.setItem(i, 2, item)
            else:
                production = tuple[2]
                if production:
                    if production[1][0] is None:
                        item = str(production[0]) + "  → ε"
                    else:
                        item = "{} → {}".format(production[0], "  ".join(str(x) for x in production[1][0]))
                else:
                    item = ""

                table.setItem(i, 2, QTableWidgetItem(item))

        self.setCentralWidget(table)
        self.resize(table.horizontalHeader().length() + 20,
                    table.verticalHeader().length() + 60)

