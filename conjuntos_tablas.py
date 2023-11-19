"""
Filename:
Author: Laura González Pizarro
Description:
"""
import json
import re
from math import log10

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit, QTableWidgetItem, QTableWidget, QDesktopWidget, QMenuBar, \
    QMenu, QAction, QFileDialog, QPushButton, QLineEdit, QLabel, QVBoxLayout, QWidget, QMessageBox

import automaton
import conjuntos as conj

def center_window(window):
    screen = QDesktopWidget().availableGeometry()
    window_size = window.frameGeometry()
    x = (screen.width() - window_size.width()) // 2
    y = (screen.height() - window_size.height()) // 2
    window.move(x, y)


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
        center_window(self)

        self.text_edit = QPlainTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.text_edit.setReadOnly(True)

        text = ""
        for key in self.dicc.keys():  # FIXME LOS ESPACIOS NO FUNCIONAN TIENE QUE SER CARACTERES NO IMPRIMIBLES COMO \u00A0
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
        # Center window to the middle of the screen
        center_window(self)

        self.text_follow_set = QPlainTextEdit(self)
        self.setCentralWidget(self.text_follow_set)
        self.text_follow_set.setReadOnly(True)

        text = ""
        for key in self.dicc.keys():
            text += "Sig(" + key + "): " + " , ".join([str(x) if x is not None else 'ε' for x in self.dicc[key]]) + "\n"
        self.text_follow_set.setPlainText(text)



class FirstSetSentenceWindow(QMainWindow):
    def __init__(self, traductions, terminal_tokens, non_terminal_tokens, productions, parent=None):
        super().__init__(parent)
        self.terminal_tokens = terminal_tokens
        self.non_terminal_tokens = non_terminal_tokens
        self.productions = productions

        self.setGeometry(0, 0, 300, 100)
        center_window(self)

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
        if set(elements).difference(self.non_terminal_tokens).difference(self.terminal_tokens) != set():
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Critical)
            error_message.setWindowTitle("Error")
            error_message.setText("error ")  # FIXME poner mensaje de error

        else:
            first_set_sentence = conj.calculate_first_set_sentence(elements, self.terminal_tokens,
                                                                   self.non_terminal_tokens, self.productions)
            text = " , ".join([str(x) if x is not None else 'ε' for x in first_set_sentence])
            self.text_input2.setText(text)

class AnalysisTableLL1(QMainWindow):
    def __init__(self, traductions, analysis_table, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.analysis_table = analysis_table
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.traductions["tituloTablaLL1"])

        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)
        file_menu = QMenu("File", self) # fixme
        self.menubar.addMenu(file_menu)
        new_action = QAction(self.traductions["submenuNuevo"], self)
        new_action.triggered.connect(self.save_as_json)
        file_menu.addAction(new_action)


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

    def save_as_json(self):
        file_route, _ = QFileDialog.getSaveFileName(self, self.traductions["tituloGuardarComo"])
        if file_route:
            with open(file_route, 'w') as file:
                data = {str(k): v if v != ["error"] else [""] for k, v in self.analysis_table.items()}
                for k, v in self.analysis_table.items():
                    print(k, v)
                json.dump(data, file, indent=4)


class ExpandedGrammar(QMainWindow):
    def __init__(self, traductions, start_token, non_terminal_tokens, productions, type, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.start_token = start_token
        self.non_terminal_tokens = non_terminal_tokens
        self.productions = productions
        self.type = type
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.traductions["tituloAmpliada"] + self.type)
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
    def __init__(self, traductions, nodes, edges, start_token, productions, type, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.nodes = nodes
        self.edges = edges
        self.start_token = start_token
        self.productions = productions
        self.type = type
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.traductions["tituloEscrito"] + self.type)
        self.setGeometry(0, 0, 500, 500)

        center_window(self)

        self.text_edit = QPlainTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.text_edit.setReadOnly(True)

        text = self.traductions["menuGramatica"] + "\n\n"
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
        # escribir los estados con las reglas
        for i, node in enumerate(self.nodes):
            text += self.traductions["estado"] + str(i) + "\n\n"
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
                if prod[1].index('.') == len(prod[1]) - 1:
                    text_reduce += self.traductions["tituloReducir"] + str(index) + " (" + prod[0] + ")" + "\n"

            text += "\n"

            text_go_to = ""
            while edge_index < len(edges_list) and edges_list[edge_index][0] == str(i):
                if self.edges[str(i), edges_list[edge_index][1]] in self.productions: # self.traductions["tituloReducir"]
                    text_go_to += "    " + self.edges[str(i), edges_list[edge_index][1]] + self.traductions["tituloIrA"] + edges_list[edge_index][1] + "\n"
                else:
                    text += "    " + self.edges[str(i), edges_list[edge_index][1]] + self.traductions["tituloDesplazarEIr"] + edges_list[edge_index][1] + "\n"
                edge_index += 1

            text += "\n" + text_reduce + "\n" + text_go_to + "\n"

        self.text_edit.setPlainText(text)


class ActionTable(QMainWindow): # TODO poner el numero de la produccoin o la produccion
    def __init__(self, traductions, accion, terminal_tokens, productions, type, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.tabla_accion = accion
        self.terminal_tokens = list(terminal_tokens | {"$"})
        self.productions = productions
        self.type = type
        self.productions_index = dict()
        i = 1
        for token in productions.keys():
            self.productions_index[token] = i
            i += len(productions[token])
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.traductions["etiqTablaAccion"] + self.type)
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
                    item_text += "d " + prod[10:]
                elif prod == "aceptar":
                    item_text += "acep"
                elif prod[:7] == "reducir":
                    item_text += "r " + prod[8:]

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
    def __init__(self, traductions, ir_a, non_terminal_tokens, type, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.ir_a = ir_a
        self.non_terminals = list(non_terminal_tokens)
        self.type = type
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.traductions["etiqTablaIrA"] + self.type)
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


#todo cambiar nombre ya que lo usan lr y lalr tambien
class AnalysisTableSLR1(QMainWindow):
    def __init__(self, traductions, max_lenght, accion, ir_a, nodes, edges, terminal_tokens, non_terminal_tokens, start_token, productions, window, type,parent=None):
        super().__init__(parent)
        action_window = ActionTable(traductions, accion, terminal_tokens, productions, type, self)
        action_window.show()
        go_to_window = GoToTable(traductions, ir_a, non_terminal_tokens, type, self)
        go_to_window.show()
        automaton_text_window = AutomatonText(traductions, nodes, edges, start_token, productions, type, self)
        automaton_text_window.show()
        if len(nodes) <= max_lenght:
            automaton_window = automaton.AutomatonWindow(traductions, nodes, edges, window, type, self)
            automaton_window.show()
        extended_grammar = ExpandedGrammar(traductions, start_token, non_terminal_tokens, productions, type, self)
        extended_grammar.show()

