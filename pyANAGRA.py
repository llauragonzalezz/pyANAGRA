"""
Filename:
Developed by Laura González Pizarro
Directed by Joaquín Ezpeleta Mateo
Universidad de Zaragoza
Description:
"""
import json
import os
import re
import sys

from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QKeySequence, QClipboard, QTextCursor, QTextCharFormat, QColor, QFont, QPixmap, QTextDocument
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, qApp, QAction, QCheckBox, QPlainTextEdit, \
    QWidgetAction, QMessageBox, QFileDialog, QStatusBar, QLabel, QInputDialog, QTextEdit, QFontDialog, QColorDialog

import LALR
import LL1
import LR
import bottom_up as bu
import grammar
import tables
import sets
import SLR
import bisonparse
import utils
from ply import *



class WorkerLL1(QObject):
    result_signal = pyqtSignal(dict)

    def __init__(self, grammar):
        super().__init__()
        self.grammar = grammar
        self.isRunning = True

    def run(self):
        table_LL1 = LL1.calculate_table(self.grammar)

        if self.isRunning:
            self.result_signal.emit(table_LL1)

    def stop(self):
        self.isRunning = False

class WorkerLR(QObject):
    result_signal = pyqtSignal(tuple)

    def __init__(self, grammar, ext_grammar):
        super().__init__()
        self.grammar = grammar
        self.ext_grammar = ext_grammar
        self.isRunning = True

    def run(self):
        #first_set = conj.calculate_first_set(self.grammar)
        first_set = self.grammar.calculate_first_set()
        conj_LR1 = LR.conj_LR1(first_set, self.ext_grammar)
        action_table_LR = LR.action_table(first_set, conj_LR1, self.ext_grammar)
        go_to_table_LR = LR.go_to_table(first_set, conj_LR1, self.ext_grammar)
        edges_LR = LR.create_automaton(first_set, conj_LR1, self.ext_grammar)

        if self.isRunning:
            self.result_signal.emit((conj_LR1, action_table_LR, go_to_table_LR, edges_LR))

    def stop(self):
        self.isRunning = False


class WorkerLALR(QObject):
    result_signal = pyqtSignal(tuple)

    def __init__(self, grammar, ext_grammar):
        super().__init__()
        self.grammar = grammar
        self.ext_grammar = ext_grammar
        self.isRunning = True


    def run(self):
        #first_set = conj.calculate_first_set(self.grammar)
        first_set = self.grammar.calculate_first_set()
        conj_LALR = LALR.conj_LR1(first_set, self.ext_grammar)
        action_table_LALR = LALR.action_table(first_set, conj_LALR, self.ext_grammar)
        go_to_table_LALR = LALR.go_to_table(first_set, conj_LALR, self.ext_grammar)
        edges_LALR = LALR.create_automaton(first_set, conj_LALR, self.ext_grammar)
        if self.isRunning:
            self.result_signal.emit((conj_LALR, action_table_LALR, go_to_table_LALR, edges_LALR))

    def stop(self):
        self.isRunning = False

class WorkerSLR(QObject):
    result_signal = pyqtSignal(tuple)

    def __init__(self, grammar, ext_grammar):
        super().__init__()
        self.grammar = grammar
        self.ext_grammar = ext_grammar
        self.isRunning = True


    def run(self):
        #follow_set = conj.calculate_follow_set(self.grammar)
        follow_set = self.grammar.calculate_follow_set()
        conj_LR0 = SLR.conj_LR0(self.ext_grammar)
        action_table_SLR = SLR.action_table(conj_LR0, self.ext_grammar, follow_set)
        go_to_table_SLR = SLR.go_to_table(conj_LR0, self.ext_grammar)
        edges_SLR = SLR.create_automaton(conj_LR0, self.ext_grammar)
        if self.isRunning:
            self.result_signal.emit((conj_LR0, action_table_SLR, go_to_table_SLR, edges_SLR))

    def stop(self):
        self.isRunning = False


class MainWindow(QMainWindow):

    def __init__(self, grammar="", parent=None):
        super().__init__(parent)

        self.grammar = grammar

        self.table = dict()
        self.file = False

        self.table_LL1 = {}
        self.conj_LR0 = self.action_table_SLR = self.go_to_table_SLR = self.edges_SLR = {}
        self.conj_LALR = self.action_table_LALR = self.go_to_table_LALR = self.edges_LALR = {}
        self.conj_LR1 = self.action_table_LR = self.go_to_table_LR = self.edges_LR = {}
        self.log_window = utils.InformationLog(self)

        self.setWindowTitle("ANAGRA")
        self.setGeometry(0, 0, 800, 600)
        # Center window to the middle of the screen
        utils.center_window(self)

        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.text_grammar = QPlainTextEdit(self)
        self.text_grammar.cursorPositionChanged.connect(self.update_row_column)
        self.setCentralWidget(self.text_grammar)
        self.changes = 0
        self.configuration()

        # Barra modo, linea y columna del cursor
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.mode_label = QLabel()
        self.row_label = QLabel()
        self.column_label = QLabel()

        self.status_bar.addWidget(self.mode_label)
        self.status_bar.addPermanentWidget(self.row_label)
        self.status_bar.addPermanentWidget(self.column_label)

        if self.grammar != "":
            self.menu_gramaticas()
            self.show_grammar()
        else:
            self.menu_inicial()

        self.update_row_column()

    def configuration(self):
        config_file = open('locales/config.json')
        self.data = json.load(config_file)

        if not self.data["default"]:
            font_text_grammar = QFont()
            font_text_grammar.setFamily(self.data["family"])
            font_text_grammar.setPointSize(self.data["point_size"])
            font_text_grammar.setBold(self.data["bold"])
            font_text_grammar.setItalic(self.data["italic"])
            font_text_grammar.setUnderline(self.data["underline"])
            color = self.data["color"]
            self.text_grammar.setFont(font_text_grammar)
            self.text_grammar.setStyleSheet(f"color: {color};")

        self.tabs = self.data["tabs"]
        self.states = self.data["states"]
        self.english = self.data["english"]

        if self.data["english"]:
            traduction_file = open('locales/english.json')
        else:
            traduction_file = open('locales/spanish.json')
        self.traductions = json.load(traduction_file)


    def grammar_menu(self, edit_mode=False):
        grammar_qmenu = QMenu(self.traductions["menuGramatica"], self)
        self.menubar.addMenu(grammar_qmenu)

        # Options for grammar menu
        new_action = QAction(self.traductions["submenuNuevo"], self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_app)
        grammar_qmenu.addAction(new_action)

        open_action = QAction(self.traductions["submenuAbrir"], self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setEnabled(not edit_mode)  # Enable/Disable action
        open_action.triggered.connect(self.open_file)
        grammar_qmenu.addAction(open_action)

        edit_action = QAction(self.traductions["submenuEditar"], self)
        edit_action.setEnabled(edit_mode)  # Enable/Disable action
        edit_action.triggered.connect(self.edit_file)
        grammar_qmenu.addAction(edit_action)

        save_action = QAction(self.traductions["submenuGuardar"], self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setEnabled(edit_mode)  # Enable/Disable action
        save_action.triggered.connect(self.save_file)
        grammar_qmenu.addAction(save_action)

        save_as_action = QAction(self.traductions["submenuGuardarComo"], self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        grammar_qmenu.addAction(save_as_action)

        grammar_qmenu.addSeparator()

        exit_action = QAction(self.traductions["submenuSalir"], self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.exit)
        grammar_qmenu.addAction(exit_action)

    def edit_menu(self, edit_mode=False):
        edit_qmenu = QMenu(self.traductions["menuEdicion"], self)
        self.menubar.addMenu(edit_qmenu)

        # Opciones de menú al menú editar
        cut_action = QAction(self.traductions["submenuCortar"], self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.cut)
        edit_qmenu.addAction(cut_action)

        copy_action = QAction(self.traductions["submenuCopiar"], self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy)
        edit_qmenu.addAction(copy_action)

        paste_action = QAction(self.traductions["submenuPegar"], self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste)
        edit_qmenu.addAction(paste_action)

        delete_action = QAction(self.traductions["submenuBorrar"], self)
        delete_action.triggered.connect(self.delete)
        edit_qmenu.addAction(delete_action)

        seleccionar_todo_action = QAction(self.traductions["submenuSeleccionarTodo"], self)
        seleccionar_todo_action.setShortcut(QKeySequence.SelectAll)
        seleccionar_todo_action.triggered.connect(self.select_all)
        edit_qmenu.addAction(seleccionar_todo_action)

        edit_qmenu.addSeparator()  # Línea de separación

        accept_grammar_action = QAction(self.traductions["submenuAceptarGramatica"], self)
        accept_grammar_action.triggered.connect(self.accept_grammar)
        accept_grammar_action.setEnabled(not edit_mode)  # Enable/Disable action
        edit_qmenu.addAction(accept_grammar_action)

    def find_menu(self):
        find_qmenu = QMenu(self.traductions["menuBuscar"], self)
        self.menubar.addMenu(find_qmenu)

        # Options Find menu
        find_action = QAction(self.traductions["menuBuscar"], self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.find)
        find_qmenu.addAction(find_action)

        remplace_action = QAction(self.traductions["submenuReemplazar"], self)
        remplace_action.setShortcut(QKeySequence.Replace)
        remplace_action.triggered.connect(self.remplace)
        find_qmenu.addAction(remplace_action)

    def text_menu(self, gramatica=False):
        text_qmenu = QMenu(self.traductions["menuTexto"], self)
        self.menubar.addMenu(text_qmenu)

        # Opciones de menú al menú text
        font_action = QAction(self.traductions["submenuFuente"], self)
        font_action.triggered.connect(self.change_font)
        text_qmenu.addAction(font_action)

        color_action = QAction(self.traductions["submenuColor"], self)
        color_action.triggered.connect(self.change_colour)
        text_qmenu.addAction(color_action)

        tab_action = QAction(self.traductions["submenuTabulador"], self)
        tab_action.triggered.connect(self.change_tab)
        text_qmenu.addAction(tab_action)

        text_qmenu.addSeparator()  # Línea de separación

        extended_action = QAction(self.traductions["submenuExtendido"], self)
        extended_action.triggered.connect(self.show_grammar)
        extended_action.setEnabled(gramatica)  # Enable/Disable action
        text_qmenu.addAction(extended_action)

        compact_action = QAction(self.traductions["submenuCompacto"], self)
        compact_action.triggered.connect(self.show_compact_grammar)
        compact_action.setEnabled(gramatica)  # Enable/Disable action
        text_qmenu.addAction(compact_action)

        text_qmenu.addSeparator()  # Línea de separación

        languaje_menu = QMenu(self.traductions["submenuIdioma"], self)

        self.english_checkbox = QCheckBox("English", self)
        self.english_checkbox.setChecked(self.english)
        self.english_checkbox.clicked.connect(lambda: self.cambiar_idioma(1))
        widgetEnglish = QWidgetAction(self)
        widgetEnglish.setDefaultWidget(self.english_checkbox)

        self.spanish_checkbox = QCheckBox("Castellano", self)
        self.spanish_checkbox.setChecked(not self.english)
        self.spanish_checkbox.clicked.connect(lambda: self.cambiar_idioma(0))
        widgetCastellano = QWidgetAction(self)
        widgetCastellano.setDefaultWidget(self.spanish_checkbox)

        languaje_menu.setContentsMargins(15, 0, 0, 0)
        languaje_menu.addAction(widgetEnglish)
        languaje_menu.addAction(widgetCastellano)
        text_qmenu.addMenu(languaje_menu)

        save_preferences_action = QAction(self.traductions["submenuGuardarPreferenc"], self) # json
        save_preferences_action.triggered.connect(self.save_preferences)
        text_qmenu.addAction(save_preferences_action)

    def help_menu(self):
        help_qmenu = QMenu(self.traductions["menuAyuda"], self)
        self.menubar.addMenu(help_qmenu)

        # Opciones de menú al menú ayuda
        information_action = QAction(self.traductions["submenuInformacion"], self)
        information_action.triggered.connect(self.show_log)
        help_qmenu.addAction(information_action)

        about_action = QAction(self.traductions["submenuAcercaDe"], self)
        about_action.triggered.connect(self.show_information) # TODO poner enlace al repositiorio git
        help_qmenu.addAction(about_action)

    def tools_menu(self):
        tools_qmenu = QMenu(self.traductions["menuHerramientas"], self)
        self.menubar.addMenu(tools_qmenu)

        # Opciones de menú al menú herramientas
        first_set_action = QAction(self.traductions["submenuConjuntoPRI"], self)
        first_set_action.triggered.connect(self.calcular_conjunto_primero)
        tools_qmenu.addAction(first_set_action)

        follow_set_action = QAction(self.traductions["submenuConjuntoSIG"], self)
        follow_set_action.triggered.connect(self.calcular_conjunto_siguiente)
        tools_qmenu.addAction(follow_set_action)

        first_set_sentence_action = QAction(self.traductions["submenuPRIFormaFrase"], self)  
        first_set_sentence_action.triggered.connect(self.calcular_conjunto_primero_frase)
        tools_qmenu.addAction(first_set_sentence_action)

    def transformations_menu(self):
        transformations_qmenu = QMenu(self.traductions["menuTransformaciones"], self)
        self.menubar.addMenu(transformations_qmenu)

        left_factoring_action = QAction(self.traductions["submenuFactorizacionIzq"], self)
        left_factoring_action.triggered.connect(self.left_factoring)
        transformations_qmenu.addAction(left_factoring_action)

        removal_underivable_non_terminals_action = QAction(self.traductions["submenuNoDerivables"], self)
        removal_underivable_non_terminals_action.triggered.connect(self.removal_underivable_non_terminals)
        transformations_qmenu.addAction(removal_underivable_non_terminals_action)

        removal_left_recursion_action = QAction(self.traductions["submenuRecursividadIzq"], self)
        removal_left_recursion_action.triggered.connect(self.removal_left_recursion)
        transformations_qmenu.addAction(removal_left_recursion_action)

        removal_unreachable_terminals_action = QAction(self.traductions["submenuNoAccesibles"], self)
        removal_unreachable_terminals_action.triggered.connect(self.removal_unreachable_terminals)
        transformations_qmenu.addAction(removal_unreachable_terminals_action)

        removal_eps_prod_action = QAction(self.traductions["submenuAnulables"], self)
        removal_eps_prod_action.triggered.connect(self.removal_eps_prod)
        transformations_qmenu.addAction(removal_eps_prod_action)

        removal_unit_prod_action = QAction(self.traductions["submenuCiclos"], self)
        removal_unit_prod_action.triggered.connect(self.removal_unit_prod)
        transformations_qmenu.addAction(removal_unit_prod_action)

        chomsky_normal_form_action = QAction(self.traductions["submenuFNChomsky"], self)
        chomsky_normal_form_action.triggered.connect(self.chomsky_normal_form)
        transformations_qmenu.addAction(chomsky_normal_form_action)

        greibach_normal_form_action = QAction(self.traductions["submenuFNGreibach"], self)
        greibach_normal_form_action.triggered.connect(self.greibach_normal_form)
        transformations_qmenu.addAction(greibach_normal_form_action)

    def parse_menu(self):
        parse_qmenu = QMenu(self.traductions["menuAnalizar"], self)
        self.menubar.addMenu(parse_qmenu)

        parse_LL1_grammar_action = QAction(self.traductions["submenuAnalizarLL1"], self)
        parse_LL1_grammar_action.triggered.connect(self.parse_LL1_grammar)
        parse_qmenu.addAction(parse_LL1_grammar_action)

        self.save_LL1_table_action = QAction("Guardar tabla LL(1)", self)
        self.save_LL1_table_action.triggered.connect(self.save_LL1_table)
        self.save_LL1_table_action.setEnabled(False)  # Enable/Disable action
        parse_qmenu.addAction(self.save_LL1_table_action)

        parse_SLR_grammar_action = QAction(self.traductions["submenuAnalizarSLR1"], self)
        parse_SLR_grammar_action.triggered.connect(self.parse_SLR_grammar)
        parse_qmenu.addAction(parse_SLR_grammar_action)

        self.save_SLR_table_action = QAction("Guardar tablas SLR", self)
        self.save_SLR_table_action.triggered.connect(self.save_SLR_table)
        self.save_SLR_table_action.setEnabled(False)  # Enable/Disable action
        parse_qmenu.addAction(self.save_SLR_table_action)

        parse_LALR_grammar_action = QAction(self.traductions["submenuAnalizarLALR1"], self)
        parse_LALR_grammar_action.triggered.connect(self.parse_LALR_grammar)
        parse_qmenu.addAction(parse_LALR_grammar_action)

        self.save_LALR_table_action = QAction("Guardar tablas LALR", self)
        self.save_LALR_table_action.triggered.connect(self.save_LALR_table)
        self.save_LALR_table_action.setEnabled(False)  # Enable/Disable action
        parse_qmenu.addAction(self.save_LALR_table_action)

        parse_LR_grammar_action = QAction(self.traductions["submenuAnalizarLR1"], self)
        parse_LR_grammar_action.triggered.connect(self.parse_LR_grammar)
        parse_qmenu.addAction(parse_LR_grammar_action)

        self.save_LR_table_action = QAction("Guardar tablas LR", self)
        self.save_LR_table_action.triggered.connect(self.save_LR_table)
        self.save_LR_table_action.setEnabled(False)  # Enable/Disable action
        parse_qmenu.addAction(self.save_LR_table_action)


    def simulate_menu(self):
        simulate_qmenu = QMenu(self.traductions["menuSimular"], self)
        self.menubar.addMenu(simulate_qmenu)

        self.parse_LL1_input_action = QAction(self.traductions["submenuSimularLL1"], self)
        self.parse_LL1_input_action.triggered.connect(self.parse_LL1_input)
        self.parse_LL1_input_action.setEnabled(False)  # Enable/Disable action
        simulate_qmenu.addAction(self.parse_LL1_input_action)

        self.parse_SLR_input_action = QAction(self.traductions["submenuSimularSLR1"], self)
        self.parse_SLR_input_action.triggered.connect(self.parse_SLR_input)
        self.parse_SLR_input_action.setEnabled(False)  # Enable/Disable action
        simulate_qmenu.addAction(self.parse_SLR_input_action)

        self.parse_LALR_input_action = QAction(self.traductions["submenuSimularLALR1"], self)
        self.parse_LALR_input_action.triggered.connect(self.parse_LALR_input)
        self.parse_LALR_input_action.setEnabled(False)  # Enable/Disable action
        simulate_qmenu.addAction(self.parse_LALR_input_action)

        self.parse_LR_input_action = QAction(self.traductions["submenuSimularLR1"], self)
        self.parse_LR_input_action.triggered.connect(self.parse_LR_input)
        self.parse_LR_input_action.setEnabled(False)  # Enable/Disable action
        simulate_qmenu.addAction(self.parse_LR_input_action)


    def menu_inicial(self):
        self.grammar_menu()
        self.edit_menu()
        self.find_menu()
        self.text_menu()
        self.help_menu()

        self.text_grammar.setReadOnly(False)  # Enable writting mode
        self.mode_label.setText(self.traductions["escritura"])

    def menu_gramaticas(self):
        self.menubar.clear()
        self.grammar_menu(True)
        self.find_menu()
        self.text_menu(True)

        self.tools_menu()
        self.transformations_menu()
        self.parse_menu()
        self.simulate_menu()
        self.help_menu()

        self.text_grammar.setReadOnly(True)  # Disable writting mode
        self.mode_label.setText(self.traductions["lectura"])


    def closeEvent(self, event):
        self.exit()


    def update_row_column(self):
        cursor = self.text_grammar.textCursor()
        row = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.row_label.setText(self.traductions["linea"] + ": " + str(row))
        self.column_label.setText(self.traductions["columna"] + ": " + str(col))

        # Remove highlight from extraSelections
        self.text_grammar.setExtraSelections([])
        self.text_grammar.setCurrentCharFormat(QTextCharFormat())

    def yacc_parse_grammar(self, text):
        self.text_grammar.setPlainText(text)

        try:
            self.grammar = yacc.parse(text)
            self.menu_gramaticas()
            self.log_window.add_information(self.traductions["mensajeGramaticaExito"])

        except SyntaxError as e:
            self.log_window.add_information(self.traductions["mensajeGramaticaFracaso"])
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Critical)
            error_message.setWindowTitle("Error")
            if str(e)[0] == "l":
                pos = 0
                cursor = QTextCursor(self.main_window.text_grammar.document())
                cursor = self.main_window.text_grammar.document().find(str(e), cursor, QTextDocument.FindWholeWords | QTextDocument.FindCaseSensitively)
                error_message.setText(self.message_error("Illegal character ", 0))
            else:
                error_message.setText(self.message_error("Illegal character", int(str(e))))
            error_message.setStandardButtons(QMessageBox.Ok)
            error_message.exec_()

        except Exception as e:
            self.log_window.add_information(self.traductions["mensajeGramaticaFracaso"])
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Critical)
            error_message.setWindowTitle("Error")
            if str(e)[0] == "l":
                cursor = QTextCursor(self.text_grammar.document())
                cursor = self.text_grammar.document().find(str(e)[1:], cursor, QTextDocument.FindWholeWords | QTextDocument.FindCaseSensitively)
                line = cursor.blockNumber() + 1
                col = cursor.positionInBlock() + 1

                seleccion = QTextEdit.ExtraSelection()
                seleccion.format.setBackground(QColor("red"))
                cursor.movePosition(QTextCursor.StartOfBlock)
                cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                seleccion.cursor = cursor
                self.text_grammar.setExtraSelections([seleccion])
                error_message.setText(f'Illegal character {str(e)[1:]} at line {line} and column {col}')
            else:
                error_message.setText(self.message_error("Syntax error ", int(str(e))))
            error_message.setStandardButtons(QMessageBox.Ok)
            error_message.exec_()

    def message_error(self, message, pos):
        if pos == -1:
            pos = len(self.text_grammar.toPlainText()) - 1
        text = self.text_grammar.toPlainText()[:pos+1]
        line = text.count('\n') + 1
        col = len(text) - text.rfind('\n')
        seleccion = QTextEdit.ExtraSelection()
        seleccion.format.setBackground(QColor("red"))  # Cambiar el color de fondo a rojo

        cursor = QTextCursor(self.text_grammar.document())
        for _ in range(line - 1):  # Restamos 1 porque los índices comienzan desde 1
            cursor.movePosition(QTextCursor.NextBlock)

            # Seleccionar toda la línea
        cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)

        seleccion.cursor = cursor
        self.text_grammar.setExtraSelections([seleccion])

        return f'{message} {text[pos]} at line {line} and column {col}'

    def new_app(self):  
        python_path = sys.executable
        os.system(python_path + " " + os.path.abspath(__file__) + " &")

    def open_file(self):
        dialogo = QFileDialog(self, self.traductions["tituloAbrir"])
        dialogo.setFileMode(QFileDialog.ExistingFile)

        if dialogo.exec_() == QFileDialog.Accepted:
            # Obtenemos la ruta del archivo
            self.file = dialogo.selectedFiles()[0]
            text = open(self.file).read()
            self.log_window.add_information(self.traductions["mensajeAbriendo"] + self.file)
            self.log_window.add_information(self.traductions["mensajeAbierto"])

            self.yacc_parse_grammar(text)


    def edit_file(self):
        bisonparse.token_inicial = ""
        bisonparse.terminals = set()
        bisonparse.non_terminals = set()
        bisonparse.producciones = dict()
        bisonparse.aux_symbols = set()

        self.grammar = ""
        self.table = dict()

        self.table_LL1 = {}
        self.conj_LR0 = self.action_table_SLR = self.go_to_table_SLR = self.edges_SLR = {}
        self.conj_LALR = self.action_table_LALR = self.go_to_table_LALR = self.edges_LALR = {}
        self.conj_LR1 = self.action_table_LR = self.go_to_table_LR = self.edges_LR = {}

        self.menubar.clear()
        self.menu_inicial()

    def save_file(self):
        if self.file:  # Check if using file as input
            file = self.file
        else:
            file = QFileDialog.getSaveFileName(self, self.traductions["tituloGuardar"])[0]
            if not file:
                return

        file = open(file, 'w')
        texto = self.text_grammar.toPlainText()
        file.write(texto)
        file.close()
        self.log_window.add_information(self.traductions["mensajeGuardado"] + file)

    def save_file_as(self):
        file, _ = QFileDialog.getSaveFileName(self, self.traductions["tituloGuardarComo"])
        if file:
            fichero = open(file, 'w')
            texto = self.text_grammar.toPlainText()
            fichero.write(texto)
            fichero.close()
            self.log_window.add_information(self.traductions["mensajeGuardado"] + file)

    def exit(self):
        #if self.changes or not self.text_grammar.isReadOnly():
        confirm_dialog = QMessageBox(self)
        confirm_dialog.setWindowTitle(self.traductions["mensajeSalida1"])
        confirm_dialog.setText(self.traductions["mensajeSalida1"] + self.traductions["mensajeSalida2"] )
        confirm_dialog.setStandardButtons(QMessageBox.Yes)

        result = confirm_dialog.exec_()
        if confirm_dialog.clickedButton() == QMessageBox.Yes:
            QApplication.quit()


    def accept_grammar(self):
        text = self.text_grammar.toPlainText()
        self.yacc_parse_grammar(text)

    def find(self):
        find_window = utils.FindWindow(self.traductions, main_window, self)
        find_window.show()

    def remplace(self):
        remplace_window = utils.RemplaceWindow(self.traductions, main_window, self)
        remplace_window.show()

    def cut(self):
        clipboard = qApp.clipboard()
        texto = self.text_grammar.textCursor().selectedText()
        clipboard.setText(texto)                                # Save text in clipboard
        self.text_grammar.textCursor().removeSelectedText()     # Erease selected text

    def copy(self):
        clipboard = qApp.clipboard()
        text = self.text_grammar.textCursor().selectedText()
        clipboard.setText(text)                                 # Save selected text in clipboard

    def paste(self):
        clipboard = qApp.clipboard()
        text = clipboard.text(QClipboard.Clipboard)
        self.text_grammar.textCursor().insertText(text)         # Paste copied text

    def delete(self):
        self.text_grammar.textCursor().removeSelectedText()     # Erease selected text

    def select_all(self):
        cursor = self.text_grammar.textCursor()
        cursor.select(QTextCursor.Document)
        self.text_grammar.setTextCursor(cursor)

    def show_log(self):  
        self.log_window.show()

    def show_information(self):
        mensaje = QMessageBox()
        mensaje.setWindowTitle(self.traductions["mensaje"])

        label_izquierda = QLabel(mensaje)
        pixmap_izquierda = QPixmap("uz.png").scaled(220, 220, aspectRatioMode=Qt.KeepAspectRatio)
        mensaje.setIconPixmap(pixmap_izquierda)
        label_izquierda.setAlignment(Qt.AlignHCenter)

        message = self.traductions["mensajeAcercaDe1"] + " " + \
                  self.traductions["mensajeAcercaDe2"] + "\n\n" + \
                  self.traductions["mensajeAcercaDe3"] + "\n" + \
                  self.traductions["mensajeAcercaDe4"]
        mensaje.setText(message)

        # Agregar widgets directamente al contenedor principal del QMessageBox
        mensaje.layout().addWidget(label_izquierda, 0, 0, alignment=Qt.AlignLeft)
        mensaje.exec_()


    def change_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.text_grammar.setFont(font)
            self.changes = True
            self.data["default"] = False
            self.data["family"] = font.family()
            self.data["point_size"] = font.pointSize()
            self.data["bold"] = font.bold()
            self.data["italic"] = font.italic()
            self.data["underline"] = font.underline()


    def change_colour(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.changes = True
            self.text_grammar.setStyleSheet(f"color: {color.name()};")
            self.data["default"] = False
            self.data["color"] = color.name()

    def change_tab(self):  
        spaces, ok = QInputDialog.getText(self, self.traductions["submenuTabulador"], self.traductions["mensajeTabulador"])
        if ok:
            if spaces.isdigit() and int(spaces) > 0:
                self.tabs = int(spaces)
                self.changes = True
                self.data["tabs"] = spaces
                self.show_grammar()
            else: # mensaje de error
                error_message = QMessageBox()
                error_message.setIcon(QMessageBox.Critical)
                error_message.setWindowTitle("Error")
                error_message.setText("error ")


    def cambiar_idioma(self, english):
        if (not english and self.english_checkbox.isChecked()) or (english and self.spanish_checkbox.isChecked()):
            confirm_dialog = QMessageBox(self)
            confirm_dialog.setWindowTitle(self.traductions["tituloCambioIdioma"])
            confirm_dialog.setText(self.traductions["mensajeCambioIdioma"])
            confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            result = confirm_dialog.exec_()
            if result == QMessageBox.Yes:
                if english:
                    self.english_checkbox.setChecked(True)
                    self.spanish_checkbox.setChecked(False)
                else:
                    self.english_checkbox.setChecked(False)
                    self.spanish_checkbox.setChecked(True)

                with open('locales/config.json', 'r') as file:
                    data = json.load(file)

                data["english"] = english

                with open('locales/config.json', 'w') as file:
                    json.dump(data, file, indent=4)

            else:
                if english:
                    self.english_checkbox.setChecked(False)
                else:
                    self.spanish_checkbox.setChecked(False)
        elif english:
            self.english_checkbox.setChecked(True)
        else:
            self.spanish_checkbox.setChecked(True)

    def save_preferences(self):
        if self.changes:
            with open('locales/config.json', 'w') as file:
                json.dump(self.data, file, indent=4)


    def calcular_conjunto_primero(self):
        self.log_window.add_information(self.traductions["mensajeConjuntoPRI"])
        #first_set = conj.calculate_first_set(self.grammar)
        first_set = self.grammar.calculate_first_set()
        first_set_window = sets.FirstSet(self.traductions, first_set, self)
        first_set_window.show()

    def calcular_conjunto_siguiente(self):
        self.log_window.add_information(self.traductions["mensajeConjuntoSIG"])
        #follow_set = conj.calculate_follow_set(self.grammar)
        follow_set = self.grammar.calculate_follow_set()
        follow_set_window = sets.FollowSet(self.traductions, follow_set, self)
        follow_set_window.show()

    def calcular_conjunto_primero_frase(self):
        first_set_sentence_window = sets.FirstSetSentenceWindow(self.traductions, self.grammar, self)
        first_set_sentence_window.show()

    def left_factoring(self):
        self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuFactorizacionIzq"])
        self.log_window.add_information(self.traductions["mensajeTransformacion"])

        gr = grammar.left_factoring(self.grammar)
        new_window = MainWindow(gr, self)
        new_window.show()


    def removal_underivable_non_terminals(self):
        pre = True
        message = "El algoritmo de eliminación de símbolos no terminables exige en la PRE " \
                  "que el lenguaje generado sea no vacío."
        if self.grammar.empty_languaje():
            pre = False
            message += "La gramática suministrada genera el lenguaje vacío"

        if not pre:
            QMessageBox.information(self, 'Warning', message)
        else:
            self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuNoDerivables"])
            self.log_window.add_information(self.traductions["mensajeTransformacion"])

            gr = grammar.removal_underivable_non_terminals(self.grammar)
            new_window = MainWindow(gr, self)
            new_window.show()


    def removal_left_recursion(self):
        pre = True
        message = "El algoritmo de eliminación de recursividad a izquierda exige en la PRE " \
                  "que no haya ciclos, ni producciones epsilón. "
        if self.grammar.has_cycles() and self.grammar.has_epsilon_productions():
            pre = False
            message += "En la gramática suministrada hay ciclos y producciones epsilón."
        elif self.grammar.has_cycles():
            pre = False
            message += "En la gramática suministrada hay ciclos."

        elif self.grammar.has_epsilon_productions():
            pre = False
            message += "En la gramática suministrada hay producciones epsilón."

        if not pre:
            QMessageBox.information(self, 'Warning', message)
        else:
            self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuRecursividadIzq"])
            self.log_window.add_information(self.traductions["mensajeTransformacion"])

            gr, _ = grammar.removal_left_recursion(self.grammar)
            new_window = MainWindow(gr, self)
            new_window.show()

    def removal_unreachable_terminals(self):
        pre = True
        message = "El algoritmo de eliminación de símbolos no accesibles exige en la PRE " \
                  "que el lenguaje generado sea no vacío, y que cada símbolo sea " \
                  "terminable"
        if self.grammar.empty_languaje() and self.grammar.has_no_terminals():
            pre = False
            message += "La gramática suministrada genera el lenguaje vacío " \
                       "y hay símbolos no terminables."
        elif self.grammar.empty_languaje():
            pre = False
            message += "La gramática suministrada genera el lenguaje vacío."

        elif self.grammar.has_no_terminals():
            pre = False
            message += "En la gramática suministrada hay símbolos no terminables."

        if not pre:
            QMessageBox.information(self, 'Warning', message)
        else:
            self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuNoAccesibles"])
            self.log_window.add_information(self.traductions["mensajeTransformacion"])

            gr = grammar.removal_unreachable_terminals(self.grammar)
            new_window = MainWindow(gr, self)
            new_window.show()


    def removal_eps_prod(self):
        self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuAnulables"])
        self.log_window.add_information(self.traductions["mensajeTransformacion"])

        gr = grammar.removal_epsilon_productions(self.grammar)
        new_window = MainWindow(gr, self)
        new_window.show()


    def removal_unit_prod(self):
        self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuCiclos"])
        self.log_window.add_information(self.traductions["mensajeTransformacion"])

        gr = grammar.removal_cycles(self.grammar)
        new_window = MainWindow(gr, self)
        new_window.show()


    def chomsky_normal_form(self):
        self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuFNChomsky"])
        self.log_window.add_information(self.traductions["mensajeTransformacion"])

        gr = grammar.chomsky_normal_form(self.grammar)
        new_window = MainWindow(gr, self)
        new_window.show()


    def greibach_normal_form(self):
        self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuFNGreibach"])
        self.log_window.add_information(self.traductions["mensajeTransformacion"])

        gr = grammar.greibach_normal_form(self.grammar)
        new_window = MainWindow(gr, self)
        new_window.show()


    def parse_LL1_grammar(self):
        if not self.table_LL1:
            self.log_window.add_information(self.traductions["mensajeAnalizandoLL1"])

            self.progres_bar_LL1 = utils.ProgressBarWindow("Calculando la tabla para el análisis LL(1)", self.cancelProgressLL1, self)
            self.progres_bar_LL1.show()

            self.thread_LL1 = QThread()
            self.worker_LL1 = WorkerLL1(self.grammar)
            self.worker_LL1.moveToThread(self.thread_LL1)
            self.worker_LL1.result_signal.connect(self.threadResultLL1)
            self.thread_LL1.started.connect(self.worker_LL1.run)
            self.thread_LL1.finished.connect(self.thread_LL1.deleteLater)
            self.thread_LL1.start()

        else:
            analysis_table_window = tables.AnalysisTableLL1(self.traductions, self.table_LL1, self)
            analysis_table_window.show()

    def cancelProgressLL1(self):
        self.progres_bar_LL1.stopProgress()
        self.worker_LL1.stop()

    def threadResultLL1(self, result):
        self.progres_bar_LL1.stopProgress()
        self.table_LL1 = result
        self.thread_LL1.quit()
        self.worker_LL1.deleteLater()

        # Enable options if possible
        conclicts_ll1 = LL1.is_ll1(self.table_LL1, self.grammar)
        is_ll1 = conclicts_ll1 == 0
        if is_ll1:
            self.log_window.add_information(self.traductions["mensajeExitoLL1a"])
        else:
            self.log_window.add_information(self.traductions["mensajeErrorLL1a"])
            self.log_window.add_information(self.traductions["etiqEstadisticas4"] + str(conclicts_ll1))

        self.parse_LL1_input_action.setEnabled(is_ll1)
        self.save_LL1_table_action.setEnabled(is_ll1)
        analysis_table_window = tables.AnalysisTableLL1(self.traductions, self.table_LL1, self)
        analysis_table_window.show()

    def parse_SLR_grammar(self):
        if not (self.conj_LR0 and self.action_table_SLR and self.go_to_table_SLR and self.edges_SLR):
            self.log_window.add_information(self.traductions["mensajeAnalizandoSLR1"])
            self.ext_grammar = bu.extend_grammar(self.grammar)

            self.progres_bar_SLR = utils.ProgressBarWindow("Calculando la colección canónica de \nconjuntos de configuraciones SLR(1)", self.cancelProgressSLR, self)
            self.progres_bar_SLR.show()

            self.thread_SLR = QThread()
            self.worker_SLR = WorkerSLR(self.grammar, self.ext_grammar)
            self.worker_SLR.moveToThread(self.thread_SLR)
            self.worker_SLR.result_signal.connect(self.threadResultSLR)
            self.thread_SLR.started.connect(self.worker_SLR.run)
            self.thread_SLR.finished.connect(self.thread_SLR.deleteLater)
            self.thread_SLR.start()

        else:
            tables.AnalysisWindowBottomUp(self.traductions, self.data["states"], self.action_table_SLR, self.go_to_table_SLR,
                                            self.conj_LR0, self.edges_SLR, self.grammar.terminals, self.grammar.non_terminals,
                                            self.ext_grammar.initial_token, self.ext_grammar.productions, main_window, "SLR(1)", self)

    def cancelProgressSLR(self):
        self.progres_bar_SLR.stopProgress()
        self.worker_SLR.stop()

    def threadResultSLR(self, result_tuple):
        self.progres_bar_SLR.stopProgress()
        self.thread_SLR.quit()
        self.worker_SLR.deleteLater()

        self.conj_LR0 = result_tuple[0]
        self.action_table_SLR = result_tuple[1]
        self.go_to_table_SLR = result_tuple[2]
        self.edges_SLR = result_tuple[3]

        tables.AnalysisWindowBottomUp(self.traductions, self.data["states"], self.action_table_SLR, self.go_to_table_SLR,
                                        self.conj_LR0, self.edges_SLR, self.grammar.terminals, self.grammar.non_terminals,
                                        self.ext_grammar.initial_token, self.ext_grammar.productions, main_window, "SLR(1)", self)

        # Enable options if possible
        conclicts_slr1 = bu.is_bottom_up(self.action_table_SLR)
        is_slr1 = conclicts_slr1 == 0
        if is_slr1:
            self.log_window.add_information(self.traductions["mensajeExitoSLR1"])
        else:
            self.log_window.add_information(self.traductions["mensajeErrorSLR1"])
            self.log_window.add_information(self.traductions["etiqEstadisticas6"] + str(conclicts_slr1))

        self.parse_SLR_input_action.setEnabled(is_slr1)
        self.save_SLR_table_action.setEnabled(is_slr1)


    def parse_LALR_grammar(self):
        if not (self.conj_LALR and self.action_table_LALR and self.go_to_table_LALR and self.edges_LALR):
            self.log_window.add_information(self.traductions["mensajeAnalizandoLALR1"])
            self.ext_grammar = bu.extend_grammar(self.grammar)
            self.ext_grammar.terminals |= {'$'}
            self.progres_bar_LALR = utils.ProgressBarWindow("Calculando la colección canónica de \nconjuntos de configuraciones LALR(1)", self.cancelProgressLALR, self)
            self.progres_bar_LALR.show()

            self.thread_LALR = QThread()
            self.worker_LALR = WorkerLALR(self.grammar, self.ext_grammar)
            self.worker_LALR.moveToThread(self.thread_LALR)
            self.worker_LALR.result_signal.connect(self.threadResultLALR)
            self.thread_LALR.started.connect(self.worker_LALR.run)
            self.thread_LALR.finished.connect(self.thread_LALR.deleteLater)
            self.thread_LALR.start()
        else:
            tables.AnalysisWindowBottomUp(self.traductions, self.data["states"], self.action_table_LALR, self.go_to_table_LALR,
                                            self.conj_LALR, self.edges_LALR, self.grammar.terminals, self.grammar.non_terminals,
                                            self.ext_grammar.initial_token, self.ext_grammar.productions, main_window, "LALR", self)

    def cancelProgressLALR(self):
        self.progres_bar_LALR.stopProgress()
        self.worker_LALR.stop()

    def threadResultLALR(self, result_tuple):
        self.progres_bar_LALR.stopProgress()
        self.thread_LALR.quit()
        self.worker_LALR.deleteLater()

        self.conj_LALR = result_tuple[0]
        self.action_table_LALR = result_tuple[1]
        self.go_to_table_LALR = result_tuple[2]
        self.edges_LALR = result_tuple[3]

        tables.AnalysisWindowBottomUp(self.traductions, self.data["states"], self.action_table_LALR, self.go_to_table_LALR,
                                        self.conj_LALR, self.edges_LALR, self.grammar.terminals, self.grammar.non_terminals,
                                        self.ext_grammar.initial_token, self.ext_grammar.productions, main_window, "LALR", self)

        # Enable options if possible
        conclicts_lalr = bu.is_bottom_up(self.action_table_LALR)
        is_lalr = conclicts_lalr == 0
        if is_lalr:
            self.log_window.add_information(self.traductions["mensajeExitoLALR1"])
        else:
            self.log_window.add_information(self.traductions["mensajeErrorLALR1"])
            self.log_window.add_information(self.traductions["etiqEstadisticas6"] + str(conclicts_lalr))

        self.parse_LALR_input_action.setEnabled(is_lalr)
        self.save_LALR_table_action.setEnabled(is_lalr)

    def parse_LR_grammar(self):
        if not (self.conj_LR1 and self.action_table_LR and self.go_to_table_LR and self.edges_LR):
            self.log_window.add_information(self.traductions["mensajeAnalizandoLR1"])
            self.ext_grammar = bu.extend_grammar(self.grammar)
            self.ext_grammar.terminals |= {'$'}
            self.progres_bar_LR = utils.ProgressBarWindow("Calculando la colección canónica de \nconjuntos de configuraciones LR(0)", self.cancelProgressLR, self)
            self.progres_bar_LR.show()

            self.thread_LR = QThread()
            self.worker_LR = WorkerLR(self.grammar, self.ext_grammar)
            self.worker_LR.moveToThread(self.thread_LR)
            self.worker_LR.result_signal.connect(self.threadResultLR)
            self.thread_LR.started.connect(self.worker_LR.run)
            self.thread_LR.finished.connect(self.thread_LR.deleteLater)
            self.thread_LR.start()

        else:
            tables.AnalysisWindowBottomUp(self.traductions, self.data["states"], self.action_table_LR, self.go_to_table_LR,
                                            self.conj_LR1, self.edges_LR, self.grammar.terminals, self.grammar.non_terminals,
                                            self.ext_grammar.initial_token, self.ext_grammar.productions, main_window, "LR", self)

    def cancelProgressLR(self):
        self.progres_bar_LR.stopProgress()
        self.worker_LR.stop()


    def threadResultLR(self, result_tuple):
        self.progres_bar_LR.stopProgress()
        self.thread_LR.quit()
        self.worker_LR.deleteLater()

        self.conj_LR1 = result_tuple[0]
        self.action_table_LR = result_tuple[1]
        self.go_to_table_LR = result_tuple[2]
        self.edges_LR = result_tuple[3]

        tables.AnalysisWindowBottomUp(self.traductions, self.data["states"], self.action_table_LR, self.go_to_table_LR,
                                        self.conj_LR1, self.edges_LR, self.grammar.terminals, self.grammar.non_terminals,
                                        self.ext_grammar.initial_token, self.ext_grammar.productions, main_window, "LALR", self)

        # Enable options if possible
        conclicts_lr = bu.is_bottom_up(self.action_table_LALR)
        is_lr = conclicts_lr == 0
        if is_lr:
            self.log_window.add_information(self.traductions["mensajeExitoLR1"])
        else:
            self.log_window.add_information(self.traductions["mensajeErrorLR1"])
            self.log_window.add_information(self.traductions["etiqEstadisticas6"] + str(conclicts_lr))

        self.parse_LR_input_action.setEnabled(is_lr)
        self.save_LR_table_action.setEnabled(is_lr)

    def save_json(self, data):
        file_route, _ = QFileDialog.getSaveFileName(self, self.traductions["tituloGuardarComo"])
        if file_route:
            with open(file_route, 'w') as file:
                json.dump(data, file, indent=4)

    def save_LL1_table(self):
        data = {str(k): v if v != ["error"] else [""] for k, v in self.table_LL1.items()}
        self.save_json(data)

    def save_SLR_table(self):
        action_data = {str(k): v if v != ["error"] else [""] for k, v in self.action_table_SLR.items()}
        go_to_data = {str(k): v if v != ["error"] else [""] for k, v in self.go_to_table_SLR.items()}
        data = {
            "action table": action_data,
            "go_to table": go_to_data,
        }
        self.save_json(data)

    def save_LALR_table(self):
        action_data = {str(k): v if v != ["error"] else [""] for k, v in self.action_table_LALR.items()}
        go_to_data = {str(k): v if v != ["error"] else [""] for k, v in self.go_to_table_LALR.items()}
        data = {
            "action table": action_data,
            "go_to table": go_to_data,
        }
        self.save_json(data)

    def save_LR_table(self):
        action_data = {str(k): v if v != ["error"] else [""] for k, v in self.action_table_LR.items()}
        go_to_data = {str(k): v if v != ["error"] else [""] for k, v in self.go_to_table_LR.items()}
        data = {
            "action table": action_data,
            "go_to table": go_to_data,
        }
        self.save_json(data)

    def parse_LL1_input(self):
        self.log_window.add_information(self.traductions["mensajeSimulandoLL1"])
        ll1_input_window = utils.InputGrammarWindow(self.traductions, "LL1", self.grammar, self.table_LL1, parent=self)
        ll1_input_window.show()

    def parse_SLR_input(self):
        self.log_window.add_information(self.traductions["mensajeSimulandoSLR1"])
        input_window = utils.InputGrammarWindow(self.traductions, "SLR1", self.grammar, self.action_table_SLR, self.go_to_table_SLR, self)
        input_window.show()

    def parse_LALR_input(self):
        self.log_window.add_information(self.traductions["mensajeSimulandoLALR1"])
        input_window = utils.InputGrammarWindow(self.traductions, "LALR", self.grammar, self.action_table_LALR, self.go_to_table_LALR, self)
        input_window.show()

    def parse_LR_input(self):
        self.log_window.add_information(self.traductions["mensajeSimulandoLR1"])
        input_window = utils.InputGrammarWindow(self.traductions, "LR", self.grammar, self.action_table_LR, self.go_to_table_LR, self)
        input_window.show()

    def show_grammar(self):
        pattern = re.compile(r'''(?P<quote>['"]).*?(?P=quote)''')
        text = f"%start {self.grammar.initial_token}\n"
        non_character_terminals = set()
        for token in self.grammar.terminals:
            if not pattern.fullmatch(token):
                non_character_terminals.add(token)

        if non_character_terminals:
            text += "%token " + " ".join(non_character_terminals) + "\n"

        text += f"%%\n\n"

        for token, prods_token in self.grammar.productions.items():
            text += token + ": "
            spacing = " " * int(self.tabs)
            for index, prod in enumerate(prods_token):
                if prod is not None:
                    text += "  ".join(prod)
                if index != len(self.grammar.productions[token]) - 1:
                    text += "\n" + spacing + "| "
            text += "\n;\n\n"
        self.text_grammar.setPlainText(text)

    def show_compact_grammar(self):
        pattern = re.compile(r'''(?P<quote>['"]).*?(?P=quote)''')
        text = f"%start {self.grammar.initial_token}\n"
        non_character_terminals = set()
        for token in self.grammar.terminals:
            if not pattern.fullmatch(token):
                non_character_terminals.add(token)

        if non_character_terminals:
            text += "%token " + " ".join(non_character_terminals) + "\n"

        text += f"%%\n\n"
        for token, prods_token in self.grammar.productions.items():
            text += token + ": "
            for index, prod in enumerate(prods_token):
                if prod is not None:
                    text += "  ".join(prod)
                if index != len(self.grammar.productions[token]) - 1:
                    text += "| "
            text += ";\n"

        self.text_grammar.setPlainText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()
    sys.exit()
