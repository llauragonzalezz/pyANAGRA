"""
Filename:
Developed by Laura González Pizarro
Directed by Joaquín Ezpeleta Mateo
Universidad de Zaragoza
Description:
"""
import json
import re
from math import log10

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QPlainTextEdit, QTableWidgetItem, QTableWidget, QDesktopWidget,  QFileDialog

import automaton
import utils

class AnalysisTableLL1(QMainWindow):
    def __init__(self, traductions, analysis_table, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.analysis_table = analysis_table
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.traductions["tituloTablaLL1"])

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
        self.resize(table.horizontalHeader().length() + 32,
                    table.verticalHeader().length() + 42)

        # Center window to the middle of the screen
        utils.center_window(self)

    def save_as_json(self):
        file_route, _ = QFileDialog.getSaveFileName(self, self.traductions["tituloGuardarComo"])
        if file_route:
            with open(file_route, 'w') as file:
                data = {str(k): v if v != ["error"] else [""] for k, v in self.analysis_table.items()}
                json.dump(data, file, indent=4)


class ExpandedGrammar(QMainWindow):
    def __init__(self, traductions, start_token, non_terminals, productions, type, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.start_token = start_token
        self.non_terminals = non_terminals
        self.productions = productions
        self.type = type
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.traductions["tituloAmpliada"] + self.type)
        self.setGeometry(0, 0, 300, 200)
        utils.center_window(self)
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

        utils.center_window(self)

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


class ActionTable(QMainWindow):
    def __init__(self, traductions, action, terminals, productions, type, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.tabla_accion = action
        self.terminals = list(terminals | {"$"})
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
        table_action.setColumnCount(len(self.terminals))
        table_action.setRowCount(rows)
        table_action.setHorizontalHeaderLabels(self.terminals)
        table_action.setVerticalHeaderLabels([str(i) for i in range(rows)])

        row_height = table_action.rowHeight(0)
        for row, col in self.tabla_accion.keys():
            item_text = ""
            for i, prod in enumerate(self.tabla_accion[row, col]):
                if prod[:5] == "shift":
                    item_text += "d " + prod[6:]
                elif prod == "accept":
                    item_text += "acep"
                elif prod[:6] == "reduce":
                    item_text += "r " + prod[7:]

                if i < len(self.tabla_accion[row, col]) - 1:
                    item_text += "\n"

            item = QTableWidgetItem(item_text)
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)

            if len(self.tabla_accion[row, col]) > 1:
                # Adapt margins
                if table_action.rowHeight(row) < len(self.tabla_accion[row, col] * row_height):
                    table_action.setRowHeight(row, len(self.tabla_accion[row, col]) * row_height)

                item.setBackground(QColor("red"))   # SLR conflict

            table_action.setItem(row, self.terminals.index(col), item)

        self.setCentralWidget(table_action)
        self.resize(table_action.horizontalHeader().length() + 20,
                    table_action.verticalHeader().length() + 30)
        screen = QDesktopWidget().availableGeometry()
        window_size = self.frameGeometry()
        x = screen.width() // 2 - window_size.width()
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)


class GoToTable(QMainWindow):
    def __init__(self, traductions, ir_a, non_terminals, type, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.ir_a = ir_a
        self.non_terminals = list(non_terminals)
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


class AnalysisWindowBottomUp(QMainWindow):
    def __init__(self, traductions, max_lenght, action, ir_a, nodes, edges, terminals, non_terminals, start_token, productions, window, type, parent=None):
        super().__init__(parent)
        extended_grammar = ExpandedGrammar(traductions, start_token, non_terminals, productions, type, self)
        extended_grammar.show()
        action_window = ActionTable(traductions, action, terminals, productions, type, self)
        action_window.show()
        go_to_window = GoToTable(traductions, ir_a, non_terminals, type, self)
        go_to_window.show()
        automaton_text_window = AutomatonText(traductions, nodes, edges, start_token, productions, type, self)
        automaton_text_window.show()
        if len(nodes) <= max_lenght:
            automaton_window = automaton.AutomatonWindow(traductions, nodes, edges, window, type, self)
            automaton_window.show()
