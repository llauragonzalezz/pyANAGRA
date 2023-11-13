import copy
import json
import os
import re
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QClipboard, QTextCursor, QTextCharFormat, QColor, QTextDocument, QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QCheckBox, QWidgetAction, \
    QPlainTextEdit, QMessageBox, QFileDialog, QStatusBar, QLabel, qApp, QVBoxLayout, QPushButton, QWidget, \
    QDesktopWidget, QInputDialog, QTextEdit, QFontDialog, QColorDialog, QLineEdit

import LALR
import LL1
import LR
import SLR
import bisonlex
import bisonparse
from ply import *

import operacionesTransformacion as ot
import conjuntos as conj
import conjuntos_tablas as conj_tab
import simulacion as sim


def center_window(window):
    screen = QDesktopWidget().availableGeometry()
    window_size = window.frameGeometry()
    x = (screen.width() - window_size.width()) // 2
    y = (screen.height() - window_size.height()) // 2
    window.move(x, y)

class InformationLog(QMainWindow):
    def __init__(self, type, parent=None):
        super().__init__(parent)
        self.type = type
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Log")
        self.setGeometry(0, 0, 400, 200)
        # Center window to the middle of the screen
        center_window(self)

        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setReadOnly(True)

        self.setCentralWidget(self.text_edit)


    def add_information(self, text):
        self.text_edit.appendPlainText(text)

class VentanaInputGramatica(QMainWindow):
    def __init__(self, traductions, type, parent=None):
        self.traductions = traductions
        super().__init__(parent)
        self.type = type
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Input")
        self.setGeometry(0, 0, 400, 200)
        # Center window to the middle of the screen
        center_window(self)

        layout = QVBoxLayout()

        label = QLabel("Input:")
        layout.addWidget(label)

        self.text_edit = QPlainTextEdit()
        layout.addWidget(self.text_edit)

        boton_aceptar = QPushButton(self.traductions["aceptar"], self)
        boton_aceptar.clicked.connect(self.accept)
        layout.addWidget(boton_aceptar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def accept(self):
        texto = self.text_edit.toPlainText()
        self.close()
        if self.type == "LL1":
            tabla, error = LL1.simulate(ventana.table_LL1, ventana.start_token, ventana.terminal_tokens, texto + " $")
            nueva_ventana = sim.VentanaSimulacion(self.traductions, tabla, error, ventana.start_token,
                                                  ventana.terminal_tokens, ventana.non_terminal_tokens, self)

        elif self.type == "SLR1":
            tabla, error = SLR.simulate(ventana.action_table_SLR, ventana.go_to_table_SLR, texto + " $")
            nueva_ventana = sim.VentanaSimulacionSLR(self.traductions, tabla, error, ventana.terminal_tokens,
                                                     ventana.non_terminal_tokens, self)

        elif self.type == "LALR":
            tabla, error = SLR.simulate(ventana.action_table_LALR, ventana.go_to_table_LALR, texto + " $")
            nueva_ventana = sim.VentanaSimulacionSLR(self.traductions, tabla, error, ventana.terminal_tokens,
                                                     ventana.non_terminal_tokens, self)

        elif self.type == "LR":
            tabla, error = SLR.simulate(ventana.action_table_LR, ventana.go_to_table_LR, texto + " $")
            nueva_ventana = sim.VentanaSimulacionSLR(self.traductions, tabla, error, ventana.terminal_tokens,
                                                     ventana.non_terminal_tokens, self)

        nueva_ventana.show()


class FindWindow(QMainWindow):
    def __init__(self, traductions, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.setGeometry(0, 0, 200, 100)
        center_window(self)

        self.setWindowTitle(self.traductions["menuBuscar"])
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.label = QLabel(self.traductions["menuBuscar"]+":")
        self.text_input = QLineEdit()
        layout.addWidget(self.label)
        layout.addWidget(self.text_input)

        self.ok_button = QPushButton(self.traductions["aceptar"])
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)
        self.setCentralWidget(central_widget)

    def accept(self):
        search_word = self.text_input.text()
        text = ventana.text_grammar.toPlainText()
        if search_word in text:
            options = QTextDocument.FindWholeWords | QTextDocument.FindCaseSensitively
            cursor = QTextCursor(self.text_grammar.document())
            selections = []

            while not cursor.isNull():
                cursor = self.text_grammar.document().find(search_word, cursor, options)
                if not cursor.isNull():
                    sel = QTextEdit.ExtraSelection()
                    sel.format.setBackground(QColor("green"))  # Cambiar el color de fondo a verde
                    sel.cursor = cursor
                    selections.append(sel)

            self.text_grammar.setExtraSelections(selections)

        else: # fixme poner mensaje desde traductions
            QMessageBox.information(self, 'Mensaje', f'La palabra "{search_word}" no se encontró en el texto.')

class RemplaceWindow(QMainWindow):
    def __init__(self, traductions, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.setGeometry(0, 0, 200, 100)
        center_window(self)

        self.setWindowTitle(self.traductions["tituloReemplazar"])
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.label1 = QLabel(self.traductions["etiqTexto"])
        self.text_input1 = QLineEdit()
        layout.addWidget(self.label1)
        layout.addWidget(self.text_input1)

        self.label2 = QLabel(self.traductions["etiqTextoReemplazar"])
        self.text_input2 = QLineEdit()
        layout.addWidget(self.label2)
        layout.addWidget(self.text_input2)

        self.ok_button = QPushButton(self.traductions["aceptar"])
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setCentralWidget(central_widget)

    def accept(self):
        old = self.text_input1.text()
        new = self.text_input2.text()
        text = ventana.text_grammar.toPlainText()

        if old in text:
            options = QTextDocument.FindWholeWords | QTextDocument.FindCaseSensitively
            cursor = QTextCursor(ventana.text_grammar.document())
            selections = []

            while not cursor.isNull():
                cursor = ventana.text_grammar.document().find(old, cursor, options)
                if not cursor.isNull():
                    cursor.insertText(new)

            ventana.text_grammar.setExtraSelections(selections)
            self.close()

        elif old: # fixme igual que en buscar
            QMessageBox.information(self, 'Error', f'La palabra "{old}" no se encontró en el texto.')

class FirstSetSentenceWindow(QMainWindow):
    def __init__(self, traductions, parent=None):
        super().__init__(parent)
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

    def accept(self):
        elements = re.findall(r'("[^"]*"|\'[^\']*\'|\S+)', self.text_input1.text())
        first_set_sentence = conj.calculate_first_set_sentence(elements, ventana.terminal_tokens,
                                                               ventana.non_terminal_tokens, ventana.productions)
        text = " , ".join([str(x) if x is not None else 'ε' for x in first_set_sentence])
        self.text_input2.setText(text)


class MainWindow(QMainWindow):

    def __init__(self, start_token="", terminal_tokens=None, non_terminal_tokens=None, productions=None, parent=None):
        super().__init__(parent)

        if terminal_tokens is None:
            terminal_tokens = set()
        if non_terminal_tokens is None:
            non_terminal_tokens = set()
        if productions is None:
            productions = dict()

        self.start_token = start_token
        self.terminal_tokens = terminal_tokens
        self.non_terminal_tokens = non_terminal_tokens
        self.productions = productions

        self.table = dict()
        self.file = False

        self.table_LL1 = {}
        self.conj_LR0 = self.action_table_SLR = self.go_to_table_SLR = self.edges_SLR = {}
        self.conj_LALR = self.action_table_LALR = self.go_to_table_LALR = self.edges_LALR = {}
        self.conj_LR1 = self.action_table_LR = self.go_to_table_LR = self.edges_LR = {}
        self.log_window = InformationLog(self)

        self.setWindowTitle("ANAGRA")
        self.setGeometry(0, 0, 800, 600)
        # Center window to the middle of the screen
        center_window(self)

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

        if self.start_token != "":
            self.menu_gramaticas()
            self.show_compact_grammar()
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


    def pestania_gramatica(self, gramatica=False):
        grammar_menu = QMenu(self.traductions["menuGramatica"], self)
        self.menubar.addMenu(grammar_menu)

        # Options for grammar menu
        new_action = QAction(self.traductions["submenuNuevo"], self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_app)
        grammar_menu.addAction(new_action)

        open_action = QAction(self.traductions["submenuAbrir"], self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setEnabled(not gramatica)  # Enable/Disable action
        open_action.triggered.connect(self.open_file)
        grammar_menu.addAction(open_action)

        edit_action = QAction(self.traductions["submenuEditar"], self)
        edit_action.setEnabled(gramatica)  # Enable/Disable action
        edit_action.triggered.connect(self.edit_file)
        grammar_menu.addAction(edit_action)

        save_action = QAction(self.traductions["submenuGuardar"], self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setEnabled(gramatica)  # Enable/Disable action
        save_action.triggered.connect(self.save_file)
        grammar_menu.addAction(save_action)

        save_as_action = QAction(self.traductions["submenuGuardarComo"], self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        grammar_menu.addAction(save_as_action)

        grammar_menu.addSeparator()

        exit_action = QAction(self.traductions["submenuSalir"], self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.exit)
        grammar_menu.addAction(exit_action)

    def pestania_editar(self, gramatica=False):
        edit_menu = QMenu(self.traductions["menuEdicion"], self)
        self.menubar.addMenu(edit_menu)

        # Opciones de menú al menú editar
        cut_action = QAction(self.traductions["submenuCortar"], self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction(self.traductions["submenuCopiar"], self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction(self.traductions["submenuPegar"], self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)

        delete_action = QAction(self.traductions["submenuBorrar"], self)
        delete_action.triggered.connect(self.delete)
        edit_menu.addAction(delete_action)

        seleccionar_todo_action = QAction(self.traductions["submenuSeleccionarTodo"], self)
        seleccionar_todo_action.setShortcut(QKeySequence.SelectAll)
        seleccionar_todo_action.triggered.connect(self.select_all)
        edit_menu.addAction(seleccionar_todo_action)

        edit_menu.addSeparator()  # Línea de separación

        accept_grammar_action = QAction(self.traductions["submenuAceptarGramatica"], self)
        accept_grammar_action.triggered.connect(self.accept_grammar)
        accept_grammar_action.setEnabled(not gramatica)  # Enable/Disable action
        edit_menu.addAction(accept_grammar_action)

    def pestania_buscar(self):
        find_menu = QMenu(self.traductions["menuBuscar"], self)
        self.menubar.addMenu(find_menu)

        # Options Find menu
        find_action = QAction(self.traductions["menuBuscar"], self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.find)
        find_menu.addAction(find_action)

        remplace_action = QAction(self.traductions["submenuReemplazar"], self)
        remplace_action.setShortcut(QKeySequence.Replace)
        remplace_action.triggered.connect(self.remplace)
        find_menu.addAction(remplace_action)

    def pestania_texto(self, gramatica=False):
        text_menu = QMenu(self.traductions["menuTexto"], self)
        self.menubar.addMenu(text_menu)

        # Opciones de menú al menú text
        font_action = QAction(self.traductions["submenuFuente"], self)
        font_action.triggered.connect(self.change_font)

        color_action = QAction(self.traductions["submenuColor"], self)
        color_action.triggered.connect(self.change_colour)

        tab_action = QAction(self.traductions["submenuTabulador"], self)
        tab_action.triggered.connect(self.change_tab)

        extended_action = QAction(self.traductions["submenuExtendido"], self)
        extended_action.triggered.connect(self.show_grammar)
        extended_action.setEnabled(gramatica)  # Enable/Disable action

        compact_action = QAction(self.traductions["submenuCompacto"], self)
        compact_action.triggered.connect(self.show_compact_grammar)
        compact_action.setEnabled(gramatica)  # Enable/Disable action

        idiomaSubmenu = QMenu(self.traductions["submenuIdioma"], self)

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

        idiomaSubmenu.setContentsMargins(15, 0, 0, 0)
        idiomaSubmenu.addAction(widgetEnglish)
        idiomaSubmenu.addAction(widgetCastellano)
        guardarPreferenciasAction = QAction(self.traductions["submenuGuardarPreferenc"], self) # json
        guardarPreferenciasAction.triggered.connect(self.save_configuration)

        # Agregar las opciones de menú al menú text
        text_menu.addAction(font_action)
        text_menu.addAction(color_action)
        text_menu.addAction(tab_action)
        text_menu.addSeparator()  # Línea de separación
        text_menu.addAction(extended_action)
        text_menu.addAction(compact_action)
        text_menu.addSeparator()  # Línea de separación
        text_menu.addMenu(idiomaSubmenu)
        text_menu.addAction(guardarPreferenciasAction)

    def pestania_ayuda(self):
        help_menu = QMenu(self.traductions["menuAyuda"], self)
        self.menubar.addMenu(help_menu)

        # Opciones de menú al menú ayuda
        information_action = QAction(self.traductions["submenuInformacion"], self)
        information_action.triggered.connect(self.show_log)
        help_menu.addAction(information_action)

        about_action = QAction(self.traductions["submenuAcercaDe"], self)
        about_action.triggered.connect(self.show_information) # TODO poner enlace al repositiorio git
        help_menu.addAction(about_action)

    def pestania_herramientas(self):
        tools_menu = QMenu(self.traductions["menuHerramientas"], self)
        self.menubar.addMenu(tools_menu)

        # Opciones de menú al menú herramientas
        first_set_action = QAction(self.traductions["submenuConjuntoPRI"], self)
        first_set_action.triggered.connect(self.calcular_conjunto_primero)

        follow_set_action = QAction(self.traductions["submenuConjuntoSIG"], self)
        follow_set_action.triggered.connect(self.calcular_conjunto_siguiente)

        conjunto_primero_frase_action = QAction(self.traductions["submenuPRIFormaFrase"], self)  # TODO: mirar que es
        conjunto_primero_frase_action.triggered.connect(self.calcular_conjunto_primero_frase)

        # Agregar las opciones de menú al menú herramientas
        tools_menu.addAction(first_set_action)
        tools_menu.addAction(follow_set_action)
        tools_menu.addAction(conjunto_primero_frase_action)

    def pestania_transformaciones(self):
        transformations_menu = QMenu(self.traductions["menuTransformaciones"], self)
        self.menubar.addMenu(transformations_menu)

        left_factoring_action = QAction(self.traductions["submenuFactorizacionIzq"], self)
        left_factoring_action.triggered.connect(self.left_factoring)
        transformations_menu.addAction(left_factoring_action)

        eliminacion_no_derivables_action = QAction(self.traductions["submenuNoDerivables"], self)
        eliminacion_no_derivables_action.triggered.connect(self.removal_underivable_non_terminals)
        transformations_menu.addAction(eliminacion_no_derivables_action)

        removal_left_recursion_action = QAction(self.traductions["submenuRecursividadIzq"], self)
        removal_left_recursion_action.triggered.connect(self.removal_left_recursion)
        transformations_menu.addAction(removal_left_recursion_action)

        eliminacion_no_alcanzables_action = QAction(self.traductions["submenuNoAccesibles"], self)
        eliminacion_no_alcanzables_action.triggered.connect(self.transformacion_no_alcanzables)
        transformations_menu.addAction(eliminacion_no_alcanzables_action)

        removal_eps_prod_action = QAction(self.traductions["submenuAnulables"], self)
        removal_eps_prod_action.triggered.connect(self.removal_eps_prod)
        transformations_menu.addAction(removal_eps_prod_action)

        removal_unit_prod_action = QAction(self.traductions["submenuCiclos"], self)
        removal_unit_prod_action.triggered.connect(self.removal_unit_prod)
        transformations_menu.addAction(removal_unit_prod_action)

        chomsky_normal_form_action = QAction(self.traductions["submenuFNChomsky"], self)
        chomsky_normal_form_action.triggered.connect(self.chomsky_normal_form)
        transformations_menu.addAction(chomsky_normal_form_action)

        greibach_normal_form_action = QAction(self.traductions["submenuFNGreibach"], self)
        greibach_normal_form_action.triggered.connect(self.greibach_normal_form)
        transformations_menu.addAction(greibach_normal_form_action)

    def pestania_parse(self):
        parse_menu = QMenu(self.traductions["menuAnalizar"], self)
        self.menubar.addMenu(parse_menu)

        parse_LL1_grammar_action = QAction(self.traductions["submenuAnalizarLL1"], self)
        parse_LL1_grammar_action.triggered.connect(self.parse_LL1_grammar)
        parse_menu.addAction(parse_LL1_grammar_action)

        parse_SLR_grammar_action = QAction(self.traductions["submenuAnalizarSLR1"], self)
        parse_SLR_grammar_action.triggered.connect(self.parse_SLR_grammar)
        parse_menu.addAction(parse_SLR_grammar_action)

        parse_LALR_grammar_action = QAction(self.traductions["submenuAnalizarLALR1"], self)
        parse_LALR_grammar_action.triggered.connect(self.parse_LALR_grammar)
        parse_menu.addAction(parse_LALR_grammar_action)

        parse_LR_grammar_action = QAction(self.traductions["submenuAnalizarLR1"], self)
        parse_LR_grammar_action.triggered.connect(self.parse_LR_grammar)
        parse_menu.addAction(parse_LR_grammar_action)


    def pestania_simular(self):
        simular_menu = QMenu(self.traductions["menuSimular"], self)
        self.menubar.addMenu(simular_menu)

        self.parse_LL1_input_action = QAction(self.traductions["submenuSimularLL1"], self)
        self.parse_LL1_input_action.triggered.connect(self.parse_LL1_input)
        self.parse_LL1_input_action.setEnabled(False)  # Enable/Disable action
        simular_menu.addAction(self.parse_LL1_input_action)

        self.parse_SLR_input_action = QAction(self.traductions["submenuSimularSLR1"], self)
        self.parse_SLR_input_action.triggered.connect(self.parse_SLR_input)
        self.parse_SLR_input_action.setEnabled(False)  # Enable/Disable action
        simular_menu.addAction(self.parse_SLR_input_action)

        self.parse_LALR_input_action = QAction(self.traductions["submenuSimularLALR1"], self)
        self.parse_LALR_input_action.triggered.connect(self.parse_LALR_input)
        self.parse_LALR_input_action.setEnabled(False)  # Enable/Disable action
        simular_menu.addAction(self.parse_LALR_input_action)

        self.parse_LR_input_action = QAction(self.traductions["submenuSimularLR1"], self)
        self.parse_LR_input_action.triggered.connect(self.parse_LR_input)
        self.parse_LR_input_action.setEnabled(False)  # Enable/Disable action
        simular_menu.addAction(self.parse_LR_input_action)


    def menu_inicial(self):
        self.pestania_gramatica()
        self.pestania_editar()
        self.pestania_buscar()
        self.pestania_texto()
        self.pestania_ayuda()

        self.text_grammar.setReadOnly(False)  # Enable writting mode
        self.mode_label.setText(self.traductions["escritura"])

    def menu_gramaticas(self):
        self.menubar.clear()
        self.pestania_gramatica(True)
        self.pestania_buscar()
        self.pestania_texto(True)

        self.pestania_herramientas()
        self.pestania_transformaciones()
        self.pestania_parse()
        self.pestania_simular()
        self.pestania_ayuda()

        self.text_grammar.setReadOnly(True)  # Disable writting mode
        self.mode_label.setText(self.traductions["lectura"])


    #def closeEvent(self, event): # FIXME descomentame por favor
    #    self.exit()


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
            grammar = yacc.parse(text)
            self.start_token = grammar[0]
            self.terminal_tokens = grammar[1]
            self.non_terminal_tokens = grammar[2]
            self.productions = grammar[3]

            self.menu_gramaticas()
            self.log_window.add_information(self.traductions["mensajeGramaticaExito"])

        except SyntaxError as e:
            self.log_window.add_information(self.traductions["mensajeGramaticaFracaso"])
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Critical)
            error_message.setWindowTitle("Error")
            error_message.setText(str(e))
            error_message.setStandardButtons(QMessageBox.Ok)
            error_message.exec_()

    def new_app(self):  # TODO COMPROBAR QUE FUNCIONA EN WINDOWS
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
        bisonparse.tokens_terminales = set()
        bisonparse.tokens_no_terminales = set()
        bisonparse.producciones = dict()

        self.start_token = ""
        self.terminal_tokens = set()
        self.non_terminal_tokens = set()
        self.productions = dict()
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
        if self.changes or not self.text_grammar.isReadOnly():
            confirm_dialog = QMessageBox(self)
            confirm_dialog.setWindowTitle(self.traductions["mensajeSalida1"])
            confirm_dialog.setText(self.traductions["mensajeSalida1"] + self.traductions["mensajeSalida2"] )
            confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)

            result = confirm_dialog.exec_()
            if result == QMessageBox.Yes:
                QApplication.quit()


    def accept_grammar(self):
        text = self.text_grammar.toPlainText()
        self.yacc_parse_grammar(text)

    def find(self):
        find_window = FindWindow(self)
        find_window.show()

    def remplace(self):
        remplace_window = RemplaceWindow(self)
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

    def show_log(self):  # TODO
        self.log_window.show()


    def show_information(self):  # TODO
        mensaje = QMessageBox()
        mensaje.setWindowTitle(self.traductions["tituloCambioIdioma"]) # fixme cual pongo

        label_izquierda = QLabel(mensaje)
        pixmap_izquierda = QPixmap("uz.png").scaled(150, 150, aspectRatioMode=Qt.KeepAspectRatio)
        mensaje.setIconPixmap(pixmap_izquierda)

        label_derecha = QLabel(mensaje)
        pixmap_derecha = QPixmap("uz.png").scaled(150, 150, aspectRatioMode=Qt.KeepAspectRatio)
        label_derecha.setPixmap(pixmap_derecha)

        message = self.traductions["mensajeAcercaDe1"] + "\n  " + \
                  self.traductions["mensajeAcercaDe2"] + "\n\n" + \
                  self.traductions["mensajeAcercaDe3"] + "\n" + \
                  self.traductions["mensajeAcercaDe4"]
        mensaje.setText(message)

        # Agregar widgets directamente al contenedor principal del QMessageBox
        mensaje.layout().addWidget(label_izquierda, 0, 0, alignment=Qt.AlignLeft)
        mensaje.layout().addWidget(label_derecha, 1, 0, alignment=Qt.AlignLeft)

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

    def change_tab(self):  # TODO cambiar y ver qué hago
        spaces, ok = QInputDialog.getText(self, self.traductions["submenuTabulador"], self.traductions["mensajeTabulador"])
        if ok:
            if spaces.isdigit() and int(spaces) > 0:
                self.tabs = int(spaces)
                self.changes = True
                self.data["tabs"] = spaces
            else: # mensaje de error
                error_message = QMessageBox()
                error_message.setIcon(QMessageBox.Critical)
                error_message.setWindowTitle("Error")
                error_message.setText("error ") # FIXME poner mensaje de error


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

                self.changes = True
                self.data["english"] = english

            else:
                if english:
                    self.english_checkbox.setChecked(False)
                else:
                    self.spanish_checkbox.setChecked(False)
        elif english:
            self.english_checkbox.setChecked(True)
        else:
            self.spanish_checkbox.setChecked(True)

    def save_configuration(self):
        if self.changes:
            with open('locales/config.json', 'w') as archivo:
                json.dump(self.data, archivo, indent=4)


    def calcular_conjunto_primero(self):
        self.log_window.add_information(self.traductions["mensajeConjuntoPRI"])
        first_set = conj.calculate_first_set(self.terminal_tokens, self.non_terminal_tokens, self.productions)
        first_set_window = conj_tab.FirstSet(self.traductions, first_set, self)
        first_set_window.show()

    def calcular_conjunto_siguiente(self):
        self.log_window.add_information(self.traductions["mensajeConjuntoSIG"])
        follow_set = conj.calculate_follow_set(self.start_token, self.terminal_tokens, self.non_terminal_tokens,
                                               self.productions)
        follow_set_window = conj_tab.FollowSet(self.traductions, follow_set, self)
        follow_set_window.show()

    def calcular_conjunto_primero_frase(self):
        first_set_sentence_window = FirstSetSentenceWindow(self.traductions, self)
        first_set_sentence_window.show()

    def left_factoring(self):
        self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuFactorizacionIzq"])
        self.log_window.add_information(self.traductions["mensajeTransformacion"])
        non_terminal_tokens, productions = ot.left_factoring(self.non_terminal_tokens.copy(),
                                                             copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def removal_underivable_non_terminals(self):
        self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuNoDerivables"])
        self.log_window.add_information(self.traductions["mensajeTransformacion"])
        non_terminal_tokens, productions = ot.removal_underivable_non_terminals(self.start_token,
                                                                                self.terminal_tokens.copy(),
                                                                                self.non_terminal_tokens.copy(),
                                                                                copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()
        if productions[self.start_token] == [[]]:     # fixme comentario
            QMessageBox.information(self, self.traductions["mensajeAtencion"], "La gramática original y la transformada generan el lenguaje vacío")


    def removal_left_recursion(self):
        self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuRecursividadIzq"])
        self.log_window.add_information(self.traductions["mensajeTransformacion"])
        non_terminal_tokens, productions, _ = ot.removal_left_recursion(self.start_token,
                                                                        self.non_terminal_tokens.copy(),
                                                                        copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def transformacion_no_alcanzables(self):
        self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuNoAccesibles"])
        self.log_window.add_information(self.traductions["mensajeTransformacion"])
        terminal_tokens, non_terminal_tokens, productions = ot.removal_unreachable_terminals(self.start_token,
                                                                                             self.terminal_tokens.copy(),
                                                                                             self.non_terminal_tokens.copy(),
                                                                                             copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def removal_eps_prod(self):
        self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuAnulables"])
        self.log_window.add_information(self.traductions["mensajeTransformacion"])
        productions = ot.removal_epsilon_productions(self.terminal_tokens, self.non_terminal_tokens.copy(),
                                                      copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, self.non_terminal_tokens, productions, self)
        new_window.show()

    def removal_unit_prod(self):
        self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuCiclos"])
        self.log_window.add_information(self.traductions["mensajeTransformacion"])
        productions = ot.removal_cycles(self.terminal_tokens.copy(), self.non_terminal_tokens.copy(),
                                        copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, self.non_terminal_tokens, productions, self)
        new_window.show()

    def chomsky_normal_form(self):
        self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuFNChomsky"])
        self.log_window.add_information(self.traductions["mensajeTransformacion"])
        non_terminal_tokens, productions = ot.chomsky_normal_form(self.start_token, self.terminal_tokens.copy(),
                                                                  self.non_terminal_tokens.copy(), copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def greibach_normal_form(self):
        self.log_window.add_information(self.traductions["mensajeAplicando"] + self.traductions["submenuFNGreibach"])
        self.log_window.add_information(self.traductions["mensajeTransformacion"])
        non_terminal_tokens, productions = ot.greibach_normal_form(self.start_token, self.non_terminal_tokens.copy(),
                                                                   copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def parse_LL1_grammar(self):
        if not self.table_LL1:
            self.log_window.add_information(self.traductions["mensajeAnalizandoLL1"])
            self.table_LL1 = LL1.calculate_table(self.start_token, self.terminal_tokens, self.non_terminal_tokens,
                                                 self.productions)

            # Enable options if possible
            conclicts_ll1 = LL1.is_ll1(self.table_LL1, self.terminal_tokens, self.non_terminal_tokens)
            is_ll1 = conclicts_ll1 == 0
            if is_ll1:
                self.log_window.add_information(self.traductions["mensajeExitoLL1a"])
            else:
                self.log_window.add_information(self.traductions["mensajeErrorLL1a"])
                self.log_window.add_information(self.traductions["etiqEstadisticas4"] + str(conclicts_ll1))

            self.parse_LL1_input_action.setEnabled(is_ll1)

        analysis_table_window = conj_tab.AnalysisTableLL1(self.traductions, self.table_LL1, self)
        analysis_table_window.show()

    def parse_SLR_grammar(self):
        if not (self.conj_LR0 and self.action_table_SLR and self.go_to_table_SLR and self.edges_SLR):
            self.log_window.add_information(self.traductions["mensajeAnalizandoSLR1"])
            self.token_inicial_ampliado, self.tokens_no_terminales_ampliados, self.producciones_ampliados = SLR.extend_grammar(self.start_token, self.non_terminal_tokens.copy(), copy.deepcopy(self.productions))
            self.conj_LR0 = SLR.conj_LR0(self.token_inicial_ampliado, self.tokens_no_terminales_ampliados, self.producciones_ampliados)
            self.action_table_SLR = SLR.action_table(self.conj_LR0, self.token_inicial_ampliado, self.terminal_tokens, self.tokens_no_terminales_ampliados, self.producciones_ampliados)
            self.go_to_table_SLR = SLR.go_to_table(self.conj_LR0, self.tokens_no_terminales_ampliados, self.producciones_ampliados)
            self.edges_SLR = SLR.create_automaton(self.conj_LR0, self.terminal_tokens, self.non_terminal_tokens, self.productions)

            # Enable options if possible
            conclicts_slr1 = SLR.is_slr1(self.action_table_SLR)
            is_slr1 = conclicts_slr1 == 0
            if is_slr1:
                self.log_window.add_information(self.traductions["mensajeExitoSLR1"])
            else:
                self.log_window.add_information(self.traductions["mensajeErrorSLR1"])
                self.log_window.add_information(self.traductions["etiqEstadisticas6"] + str(conclicts_slr1))

            self.parse_SLR_input_action.setEnabled(is_slr1)

        conj_tab.AnalysisTableSLR1(self.traductions, self.action_table_SLR, self.go_to_table_SLR, self.conj_LR0, self.edges_SLR,
                                   self.terminal_tokens, self.non_terminal_tokens, self.token_inicial_ampliado,
                                   self.producciones_ampliados, ventana, "SLR(1)", self)


    def parse_LALR_grammar(self):
        if not (self.conj_LALR and self.action_table_LALR and self.go_to_table_LALR and self.edges_LALR):
            self.log_window.add_information(self.traductions["mensajeAnalizandoLALR1"])
            first_set = conj.calculate_first_set(self.terminal_tokens, self.non_terminal_tokens, self.productions)
            self.token_inicial_ampliado, self.tokens_no_terminales_ampliados, self.producciones_ampliados = LR.extend_grammar(self.start_token, self.non_terminal_tokens.copy(), copy.deepcopy(self.productions))
            self.conj_LALR = LALR.conj_LR1(first_set, self.token_inicial_ampliado, self.terminal_tokens | {'$'}, self.non_terminal_tokens, self.producciones_ampliados)
            self.action_table_LALR = LALR.action_table(first_set, self.conj_LALR, self.token_inicial_ampliado, self.terminal_tokens | {'$'},
                                                   self.non_terminal_tokens, self.producciones_ampliados)
            self.go_to_table_LALR = LALR.go_to_table(first_set, self.conj_LALR, self.terminal_tokens | {'$'},
                                                     self.non_terminal_tokens, self.producciones_ampliados)
            self.edges_LALR = LALR.create_automaton(first_set, self.conj_LALR, self.terminal_tokens | {'$'},
                                                    self.non_terminal_tokens, self.producciones_ampliados)

            # Enable options if possible
            conclicts_lalr = SLR.is_slr1(self.action_table_LALR)
            is_lalr = conclicts_lalr == 0
            if is_lalr:
                self.log_window.add_information(self.traductions["mensajeExitoLALR1"])
            else:
                self.log_window.add_information(self.traductions["mensajeErrorLALR1"])
                self.log_window.add_information(self.traductions["etiqEstadisticas6"] + str(conclicts_lalr))

            self.parse_LALR_input_action.setEnabled(is_lalr)

        conj_tab.AnalysisTableSLR1(self.traductions, self.action_table_LALR, self.go_to_table_LALR, self.conj_LALR, self.edges_LALR,
                                   self.terminal_tokens, self.non_terminal_tokens, self.token_inicial_ampliado,
                                   self.producciones_ampliados, ventana, "LALR", self)

    def parse_LR_grammar(self):
        if not (self.conj_LR1 and self.action_table_LR and self.go_to_table_LR and self.edges_LR):
            self.log_window.add_information(self.traductions["mensajeAnalizandoLR1"])
            first_set = conj.calculate_first_set(self.terminal_tokens, self.non_terminal_tokens, self.productions)
            self.token_inicial_ampliado, self.tokens_no_terminales_ampliados, self.producciones_ampliados = LR.extend_grammar(self.start_token, self.non_terminal_tokens.copy(), copy.deepcopy(self.productions))
            self.conj_LR1 = LR.conj_LR1(first_set, self.token_inicial_ampliado, self.terminal_tokens | {'$'}, self.non_terminal_tokens, self.producciones_ampliados)
            self.action_table_LR = LR.action_table(first_set, self.conj_LR1, self.token_inicial_ampliado, self.terminal_tokens | {'$'}, self.non_terminal_tokens, self.producciones_ampliados)
            self.go_to_table_LR = LR.go_to_table(first_set, self.conj_LR1, self.terminal_tokens | {'$'}, self.non_terminal_tokens, self.producciones_ampliados)
            self.edges_LR = LR.create_automaton(first_set, self.conj_LR1, self.terminal_tokens | {'$'}, self.non_terminal_tokens, self.producciones_ampliados)

            # Enable options if possible
            conclicts_lr = SLR.is_slr1(self.action_table_LR)
            is_lr = conclicts_lr == 0
            if is_lr:
                self.log_window.add_information(self.traductions["mensajeExitoLR1"])
            else:
                self.log_window.add_information(self.traductions["mensajeErrorLR1"])
                self.log_window.add_information(self.traductions["etiqEstadisticas6"] + str(conclicts_lr))

            self.parse_LR_input_action.setEnabled(is_lr)

        conj_tab.AnalysisTableSLR1(self.traductions, self.action_table_LR, self.go_to_table_LR, self.conj_LR1, self.edges_LR,
                                   self.terminal_tokens, self.non_terminal_tokens, self.token_inicial_ampliado,
                                   self.producciones_ampliados, ventana, "LR",self)

    def parse_LL1_input(self):
        self.log_window.add_information(self.traductions["mensajeSimulandoLL1"])
        ll1_input_window = VentanaInputGramatica(self.traductions, "LL1", self)
        ll1_input_window.show()

    def parse_SLR_input(self):
        self.log_window.add_information(self.traductions["mensajeSimulandoSLR1"])
        input_window = VentanaInputGramatica(self.traductions, "SLR1", self)
        input_window.show()

    def parse_LALR_input(self):
        self.log_window.add_information(self.traductions["mensajeSimulandoLALR1"])
        input_window = VentanaInputGramatica(self.traductions, "LALR", self)
        input_window.show()

    def parse_LR_input(self):
        self.log_window.add_information(self.traductions["mensajeSimulandoLR1"])
        input_window = VentanaInputGramatica(self.traductions, "LR", self)
        input_window.show()

    def show_grammar(self):
        pattern = re.compile(r'''(?P<quote>['"]).*?(?P=quote)''')
        text = f"%start {self.start_token}\n"
        non_character_terminal_tokens = set()
        for token in self.terminal_tokens:
            if not pattern.fullmatch(token):
                non_character_terminal_tokens.add(token)

        if non_character_terminal_tokens:
            text += "%token " + " ".join(non_character_terminal_tokens) + "\n"

        text += f"%%\n\n"

        for token, prods_token in self.productions.items():
            text += token + ": "
            spacing = "\t" * self.tabs
            for index, prod in enumerate(prods_token):
                if prod is not None:
                    text += "  ".join(prod)
                if index != len(self.productions[token]) - 1:
                    text += "\n" + spacing + "| "
            text += "\n;\n\n"
        self.text_grammar.setPlainText(text)

    def show_compact_grammar(self):
        pattern = re.compile(r'''(?P<quote>['"]).*?(?P=quote)''')
        text = f"%start {self.start_token}\n"
        non_character_terminal_tokens = set()
        for token in self.terminal_tokens:
            if not pattern.fullmatch(token):
                non_character_terminal_tokens.add(token)

        if non_character_terminal_tokens:
            text += "%token " + " ".join(non_character_terminal_tokens) + "\n"

        text += f"%%\n\n"
        for token, prods_token in self.productions.items():
            text += token + ": "
            for index, prod in enumerate(prods_token):
                if prod is not None:
                    text += "  ".join(prod)
                if index != len(self.productions[token]) - 1:
                    text += "| "
            text += ";\n"

        self.text_grammar.setPlainText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    app.exec_()
    sys.exit()
