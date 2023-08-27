from math import log10

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit, QTableWidgetItem, QTableWidget, QDesktopWidget

import automaton

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
        self.text_follow_set.setReadOnly(True)

        text = ""
        for key in self.dicc.keys():
            text += "Sig(" + key + "): " + " , ".join([str(x) if x is not None else 'ε' for x in self.dicc[key]]) + "\n"
        self.text_follow_set.setPlainText(text)


class AnalysisTableLL1(QMainWindow):
    def __init__(self, analysis_table, parent=None):
        super().__init__(parent)
        self.analysis_table = analysis_table
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Tabla analisis")

        non_terminals = sorted(set(k[0] for k in self.analysis_table.keys()))
        terminals = sorted(set(k[1] for k in self.analysis_table.keys()))

        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable edit cell
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setRowCount(len(non_terminals))
        table.setColumnCount(len(terminals))
        table.setVerticalHeaderLabels(non_terminals)
        table.setHorizontalHeaderLabels(terminals)

        row_height = table.rowHeight(0)
        for row, col in self.analysis_table.keys():
            item_text = ""
            if self.analysis_table[(row, col)] != ["error"]:
                for i, prod in enumerate(self.analysis_table[(row, col)]):
                    if prod is None:
                        item_text += str(row) + "  → ε"
                    else:
                        item_text += "{} → {}".format(row, "  ".join([str(x) for x in prod]))

                    if i < len(self.analysis_table[(row, col)]) - 1:
                        item_text += "\n"

                item = QTableWidgetItem(item_text)

                if len(self.analysis_table[(row, col)]) > 1:
                    # Adapt margins
                    if table.rowHeight(non_terminals.index(row)) < len(self.analysis_table[(row, col)] * row_height):
                        table.setRowHeight(non_terminals.index(row), len(self.analysis_table[(row, col)]) * row_height)

                    item.setBackground(QColor("red"))   # LL1 conflict

                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                table.setItem(non_terminals.index(row), terminals.index(col), item)

        self.setCentralWidget(table)
        self.resize(table.horizontalHeader().length() + 20,
                    table.verticalHeader().length() + 30)

        # Center window to the middle of the screen
        center_window(self)


class ExpandedGrammar(QMainWindow):
    def __init__(self, start_token, non_terminal_tokens, productions, parent=None):
        super().__init__(parent)
        self.start_token = start_token
        self.non_terminal_tokens = non_terminal_tokens
        self.productions = productions
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Gramática ampliada")
        self.setGeometry(0, 0, 300, 200)

        self.text_edit = QPlainTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.text_edit.setReadOnly(True)

        i = 1
        text = "0) " + self.start_token + " → " + self.productions[self.start_token][0][1] + "\n"
        for token in self.productions.keys():
            if token != self.start_token:
                for production in self.productions[token]:
                    if production is None:
                        text += str(i) + ") " + token + "  → ε" + "\n"
                    else:
                        text += str(i) + ") " + "{} → {}".format(token, "  ".join(str(x) for x in production)) + "\n"
                    i += 1

        self.text_edit.setPlainText(text)


class AutomatonText(QMainWindow):
    def __init__(self, nodes, edges, start_token, productions, accion, ir_a, parent=None):
        super().__init__(parent)
        self.nodes = nodes
        self.edges = edges
        self.start_token = start_token
        self.productions = productions
        self.accion = accion
        self.ir_a = ir_a
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Automata escrito")
        self.setGeometry(0, 0, 500, 500)

        center_window(self)

        self.text_edit = QPlainTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.text_edit.setReadOnly(True)

        text = "Gramática\n\n"
        i = 1
        key_list = dict()
        text += "    0 " + self.start_token + ": " + self.productions[self.start_token][0][1] + "\n\n"
        for token in self.productions.keys():
            if token != self.start_token:
                key_list[token] = i
                text += " " * (4 - int(log10(i))) + str(i) + " " + token + ": "
                i += 1
                spacing = " " * (len(token) + 2)
                for index, prod in enumerate(self.productions[token]):
                    if prod is not None:
                        text += " ".join(str(x) for x in prod)
                    if index != len(self.productions[token]) - 1:
                        text += "\n" + " " * (4 - int(log10(i))) + str(i) + spacing + "| "
                        i += 1
                text += "\n\n"

        #text += "Terminales con las reglas donde aparecen\n"

        #text += "No terminales con las reglas donde aparecen\n"
        # on left/ on right
        edge_index = 0

        edges_list = list(self.edges.keys())
        print(edges_list)
        # escribir los estados con las reglas
        for i, node in enumerate(self.nodes):
            text += "Estado " + str(i) + "\n\n"
            text_reduce = ""

            for prod in node:
                if prod[0] == self.start_token:
                    index = 0
                    text += "    " + str(index) + " " + self.start_token + ": " + " ".join([char if char != '.' else '•' for char in prod[1]]) + "\n"
                else:
                    if prod[1] != ['.']:
                        index = key_list[prod[0]] + self.productions[prod[0]].index([char for char in prod[1] if char != '.'])
                        text += " " * (4 - int(log10(index))) + str(index) + " " + prod[0] + ": " + " ".join([char if char != '.' else '•' for char in prod[1]]) + "\n"
                    else:
                        index = key_list[prod[0]] + self.productions[prod[0]].index(None)
                        text += " " * (4 - int(log10(index))) + str(index) + " " + prod[0] + ": •" + "\n"
                print(prod[1], prod[1].index('.'), len(prod[1]))
                if prod[1].index('.') == len(prod[1]) - 1:
                    text_reduce += "     reduce usando la regla " + str(index) + " (" + prod[0] + ")" + "\n"

            text += "\n"

            text_go_to = ""
            while edge_index < len(edges_list) and edges_list[edge_index][0] == str(i):
                if self.edges[str(i), edges_list[edge_index][1]] in self.productions:
                    text_go_to += "    " + self.edges[str(i), edges_list[edge_index][1]] + " ir al estado " + edges_list[edge_index][1] + "\n"
                else:
                    text += "    " + self.edges[str(i), edges_list[edge_index][1]] + " desplazar e ir al estado " + edges_list[edge_index][1] + "\n"
                edge_index += 1

            text += text_reduce + "\n" + text_go_to + "\n"
        # Estado 1
        # 213 identifier: IDENTIFIER •
        # $default  reduce usando la regla 213 (identifier)

        self.text_edit.setPlainText(text)


class ActionTable(QMainWindow): # TODO poner el numero de la produccoin o la produccion
    def __init__(self, accion, terminal_tokens, productions, parent=None):
        super().__init__(parent)
        self.tabla_accion = accion
        self.terminal_tokens = list(terminal_tokens | {"$"})
        self.productions = productions
        self.productions_index = dict()
        i = 1
        for token in productions.keys():
            self.productions_index[token] = i
            i += len(productions[token])
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Tabla acción")
        rows = sum(1 for key in self.tabla_accion.keys() if key[1] == "$")
        table_action = QTableWidget()
        table_action.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable edit cell
        table_action.setSelectionMode(QTableWidget.NoSelection)
        table_action.setColumnCount(len(self.terminal_tokens))
        table_action.setRowCount(rows)
        table_action.setHorizontalHeaderLabels(self.terminal_tokens)
        table_action.setVerticalHeaderLabels([str(i) for i in range(rows)])

        row_height = table_action.rowHeight(0)
        for row, col in self.tabla_accion.keys():
            item_text = ""
            for i, prod in enumerate(self.tabla_accion[row, col]):
                if prod[:9] == "desplazar":
                    item_text += "d" + prod[10:]
                elif prod == "aceptar":
                    item_text += "acep"
                elif prod[:7] == "reducir":
                    item_text += "r " + prod[8:]
                    #parts = prod[8:].split("→")
                    #if parts[1].strip() != "ε":
                    #    item_text += "r" + str(self.productions_index[parts[0].strip()] +
                    #             self.productions[parts[0].strip()].index(parts[1].strip().split()))
                    #else:
                    #    item_text += "r" + str(self.productions_index[parts[0].strip()] +
                #                           self.productions[parts[0].strip()].index(None))

                if i < len(self.tabla_accion[row, col]) - 1:
                    item_text += "\n"

            item = QTableWidgetItem(item_text)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            if len(self.tabla_accion[row, col]) > 1:
                # Adapt margins
                if table_action.rowHeight(row) < len(self.tabla_accion[row, col] * row_height):
                    table_action.setRowHeight(row, len(self.tabla_accion[row, col]) * row_height)

                item.setBackground(QColor("red"))   # SLR conflict

            table_action.setItem(row, self.terminal_tokens.index(col), item)

        self.setCentralWidget(table_action)
        self.resize(table_action.horizontalHeader().length() + 20,
                    table_action.verticalHeader().length() + 30)
        screen = QDesktopWidget().availableGeometry()
        window_size = self.frameGeometry()
        x = screen.width() // 2 - window_size.width()
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)


class GoToTable(QMainWindow):
    def __init__(self, ir_a, non_terminal_tokens, parent=None):
        super().__init__(parent)
        self.ir_a = ir_a
        self.non_terminals = list(non_terminal_tokens) # todo quitar el token inicial
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Tabla ir a")
        rows = sum(1 for key in self.ir_a.keys() if key[1] == "$")
        table_go_to = QTableWidget()
        table_go_to.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable edit cell
        table_go_to.setSelectionMode(QTableWidget.NoSelection)
        table_go_to.setColumnCount(len(self.non_terminals))
        table_go_to.setRowCount(rows)
        table_go_to.setHorizontalHeaderLabels(self.non_terminals)
        table_go_to.setVerticalHeaderLabels([str(i) for i in range(rows)])

        for row, col in self.ir_a.keys():
            if self.ir_a[row, col] != "ERROR":
                item = QTableWidgetItem(str(self.ir_a[(row, col)]))
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                table_go_to.setItem(row, self.non_terminals.index(col), item)

        self.setCentralWidget(table_go_to)
        self.resize(table_go_to.horizontalHeader().length() + 20,
                    table_go_to.verticalHeader().length() + 30)
        screen = QDesktopWidget().availableGeometry()
        window_size = self.frameGeometry()
        x = screen.width() // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)


class AnalysisTableSLR1(QMainWindow):
    def __init__(self, accion, ir_a, nodes, edges, terminal_tokens, non_terminal_tokens, start_token, productions, window, parent=None):
        super().__init__(parent)
        action_window = ActionTable(accion, terminal_tokens, productions, self)
        action_window.show()
        go_to_window = GoToTable(ir_a, non_terminal_tokens, self)
        go_to_window.show()
        automaton_text_window = AutomatonText(nodes, edges, start_token, productions, accion, ir_a, self)
        automaton_text_window.show()
        automaton_window = automaton.AutomatonWindow(nodes, edges, window, self)
        automaton_window.show()
        extended_grammar = ExpandedGrammar(start_token, non_terminal_tokens, productions, self)
        extended_grammar.show()


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

