import copy
import json
import os
import re
import sys

from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QKeySequence, QClipboard, QTextCursor, QTextCharFormat, QColor, QTextDocument, QFont
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
    def __init__(self, type, parent=None):
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

        boton_aceptar = QPushButton("Aceptar", self)
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
            nueva_ventana = sim.VentanaSimulacion(tabla, error, ventana.start_token, ventana.terminal_tokens,
                                                  ventana.non_terminal_tokens, self)

        elif self.type == "SLR1":
            tabla, error = SLR.simulate(ventana.action_table_SLR, ventana.go_to_table_SLR, texto + " $")
            nueva_ventana = sim.VentanaSimulacionSLR(tabla, error, ventana.terminal_tokens, ventana.non_terminal_tokens, self)

        elif self.type == "LALR":
            tabla, error = SLR.simulate(ventana.action_table_LALR, ventana.go_to_table_LALR, texto + " $")
            nueva_ventana = sim.VentanaSimulacionSLR(tabla, error, ventana.terminal_tokens, ventana.non_terminal_tokens, self)

        elif self.type == "LR":
            tabla, error = SLR.simulate(ventana.action_table_LR, ventana.go_to_table_LR, texto + " $")
            nueva_ventana = sim.VentanaSimulacionSLR(tabla, error, ventana.terminal_tokens, ventana.non_terminal_tokens, self)

        nueva_ventana.show()


class FindWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, 200, 100)
        center_window(self)

        self.setWindowTitle('Buscar')
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.label = QLabel("Buscar:")
        self.text_input = QLineEdit()
        layout.addWidget(self.label)
        layout.addWidget(self.text_input)

        self.ok_button = QPushButton("OK")
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

        else:
            QMessageBox.information(self, 'Mensaje', f'La palabra "{search_word}" no se encontró en el texto.')

class RemplaceWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, 200, 100)
        center_window(self)

        self.setWindowTitle('Remplazar')
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.label1 = QLabel("Buscar:")
        self.text_input1 = QLineEdit()
        layout.addWidget(self.label1)
        layout.addWidget(self.text_input1)

        self.label2 = QLabel("Remplazar por:")
        self.text_input2 = QLineEdit()
        layout.addWidget(self.label2)
        layout.addWidget(self.text_input2)

        self.ok_button = QPushButton("OK")
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

        elif old:
            QMessageBox.information(self, 'Mensaje', f'La palabra "{old}" no se encontró en el texto.')

class FirstSetSentenceWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, 300, 100)
        center_window(self)

        self.setWindowTitle('Conjunto PRIMERO forma frase')
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.label1 = QLabel("Forma frase:")
        self.text_input1 = QLineEdit()
        layout.addWidget(self.label1)
        layout.addWidget(self.text_input1)

        self.label2 = QLabel("Conjunto PRIMERO forma frase:")
        self.text_input2 = QLineEdit()
        self.text_input2.setReadOnly(True)  # Disable
        layout.addWidget(self.label2)
        layout.addWidget(self.text_input2)

        self.ok_button = QPushButton("Calcular")
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

        self.setWindowTitle("Anagra")
        self.setGeometry(0, 0, 800, 600)
        # Center window to the middle of the screen
        center_window(self)

        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.text_grammar = QPlainTextEdit(self)
        self.text_grammar.cursorPositionChanged.connect(self.update_row_column)
        self.setCentralWidget(self.text_grammar)
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
        config_file = open('config.json')
        data = json.load(config_file)

        font_text_grammar = QFont()
        font_text_grammar.setFamily(data["family"])
        font_text_grammar.setPointSize(data["point_size"])
        font_text_grammar.setBold(data["bold"])
        font_text_grammar.setItalic(data["italic"])
        font_text_grammar.setUnderline(data["underline"])
        color = data["color"]
        self.text_grammar.setFont(font_text_grammar)
        self.text_grammar.setStyleSheet(f"color: {color};")
        self.tabs = data["tabs"]
        self.states = data["states"]
        self.english = data["english"]

        translator = QTranslator()
        if data["english"]:
            translator.load("english.qm")
        else:
            translator.load("castellano.qm")
        app.installTranslator(translator)

    def pestania_gramatica(self, gramatica=False):
        grammar_menu = QMenu("Gramática", self)
        self.menubar.addMenu(grammar_menu)

        # Options for grammar menu
        new_action = QAction("Nuevo", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_app)
        grammar_menu.addAction(new_action)

        open_action = QAction("Abrir", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setEnabled(not gramatica)  # Enable/Disable action
        open_action.triggered.connect(self.open_file)
        grammar_menu.addAction(open_action)

        edit_action = QAction("Editar", self)
        edit_action.setEnabled(gramatica)  # Enable/Disable action
        edit_action.triggered.connect(self.edit_file)
        grammar_menu.addAction(edit_action)

        save_action = QAction("Guardar", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setEnabled(gramatica)  # Enable/Disable action
        save_action.triggered.connect(self.save_file)
        grammar_menu.addAction(save_action)

        save_as_action = QAction("Guardar como...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        grammar_menu.addAction(save_as_action)

        grammar_menu.addSeparator()

        exit_action = QAction("Salir", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.exit)
        grammar_menu.addAction(exit_action)

    def pestania_editar(self, gramatica=False):
        edit_menu = QMenu("Editar", self)
        self.menubar.addMenu(edit_menu)

        # Opciones de menú al menú editar
        cut_action = QAction("Cortar", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("Copiar", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Pegar", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)

        delete_action = QAction("Borrar", self)
        delete_action.triggered.connect(self.delete)
        edit_menu.addAction(delete_action)

        seleccionar_todo_action = QAction("Seleccionar todo", self)
        seleccionar_todo_action.setShortcut(QKeySequence.SelectAll)
        seleccionar_todo_action.triggered.connect(self.select_all)
        edit_menu.addAction(seleccionar_todo_action)

        edit_menu.addSeparator()  # Línea de separación

        accept_grammar_action = QAction("Aceptar gramática", self)
        accept_grammar_action.triggered.connect(self.accept_grammar)
        accept_grammar_action.setEnabled(not gramatica)  # Enable/Disable action
        edit_menu.addAction(accept_grammar_action)

    def pestania_buscar(self):
        find_menu = QMenu("Buscar", self)
        self.menubar.addMenu(find_menu)

        # Options Find menu
        find_action = QAction("Buscar", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.find)
        find_menu.addAction(find_action)

        remplace_action = QAction("Reemplazar", self)
        remplace_action.setShortcut(QKeySequence.Replace)
        remplace_action.triggered.connect(self.remplace)
        find_menu.addAction(remplace_action)

    def pestania_texto(self, gramatica=False):
        text_menu = QMenu("Texto", self)
        self.menubar.addMenu(text_menu)

        # Opciones de menú al menú text
        font_action = QAction("Fuente", self)
        font_action.triggered.connect(self.change_font)

        color_action = QAction("Color", self)
        color_action.triggered.connect(self.change_colour)

        tab_action = QAction("Tab", self)
        tab_action.triggered.connect(self.change_tab)

        extended_action = QAction("Extended", self)
        extended_action.triggered.connect(self.show_grammar)
        extended_action.setEnabled(gramatica)  # Enable/Disable action

        compact_action = QAction("Compact", self)
        compact_action.triggered.connect(self.show_compact_grammar)
        compact_action.setEnabled(gramatica)  # Enable/Disable action

        idiomaSubmenu = QMenu("Idioma", self)

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
        guardarPreferenciasAction = QAction("Guardar preferencias", self) # json

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
        help_menu = QMenu("Ayuda", self)
        self.menubar.addMenu(help_menu)

        # Opciones de menú al menú ayuda
        information_action = QAction("Información", self)
        information_action.triggered.connect(self.show_log)  # TODO poner enlace al repositiorio git
        help_menu.addAction(information_action)

        about_action = QAction("Sobre...", self)
        about_action.triggered.connect(self.show_information) # TODO poner enlace al repositiorio git
        help_menu.addAction(about_action)

    def pestania_herramientas(self):
        tools_menu = QMenu("Herramientas", self)
        self.menubar.addMenu(tools_menu)

        # Opciones de menú al menú herramientas
        first_set_action = QAction("Calcular conjunto PRIMERO", self)
        first_set_action.triggered.connect(self.calcular_conjunto_primero)

        follow_set_action = QAction("Calcular conjunto SIGUIENTE", self)
        follow_set_action.triggered.connect(self.calcular_conjunto_siguiente)

        conjunto_primero_frase_action = QAction("Calcular conjunto PRIMERO de forma de frase", self)  # TODO: mirar que es
        conjunto_primero_frase_action.triggered.connect(self.calcular_conjunto_primero_frase)

        # Agregar las opciones de menú al menú herramientas
        tools_menu.addAction(first_set_action)
        tools_menu.addAction(follow_set_action)
        tools_menu.addAction(conjunto_primero_frase_action)

    def pestania_transformaciones(self):
        transformations_menu = QMenu("Transformaciones", self)
        self.menubar.addMenu(transformations_menu)

        left_factoring_action = QAction("Factorización a izquierda", self)
        left_factoring_action.triggered.connect(self.left_factoring)
        transformations_menu.addAction(left_factoring_action)

        eliminacion_no_derivables_action = QAction("Eliminación de no terminales no derivables", self)
        eliminacion_no_derivables_action.triggered.connect(self.transformacion_no_derivables)
        transformations_menu.addAction(eliminacion_no_derivables_action)

        eliminating_left_recursion_action = QAction("Eliminación de recursividad a izquierda", self)
        eliminating_left_recursion_action.triggered.connect(self.eliminating_left_recursion)
        transformations_menu.addAction(eliminating_left_recursion_action)

        eliminacion_no_alcanzables_action = QAction("Eliminación de símbolos no alcanzables", self)
        eliminacion_no_alcanzables_action.triggered.connect(self.transformacion_no_alcanzables)
        transformations_menu.addAction(eliminacion_no_alcanzables_action)

        eliminating_eps_prod_action = QAction("Eliminación de producciones epsilon", self)
        eliminating_eps_prod_action.triggered.connect(self.eliminating_eps_prod)
        transformations_menu.addAction(eliminating_eps_prod_action)

        eliminating_unit_prod_action = QAction("Eliminación de ciclos", self)
        eliminating_unit_prod_action.triggered.connect(self.eliminating_unit_prod)
        transformations_menu.addAction(eliminating_unit_prod_action)

        chomsky_normal_form_action = QAction("Forma nomral de Chomsky", self)
        chomsky_normal_form_action.triggered.connect(self.chomsky_normal_form)
        transformations_menu.addAction(chomsky_normal_form_action)

        greibach_normal_form_action = QAction("Forma nomral de Greibach", self)
        greibach_normal_form_action.triggered.connect(self.greibach_normal_form)
        transformations_menu.addAction(greibach_normal_form_action)

    def pestania_parse(self):
        parse_menu = QMenu("Parse", self)
        self.menubar.addMenu(parse_menu)

        parse_LL1_grammar_action = QAction("Analizar gramática LL(1)", self)
        parse_LL1_grammar_action.triggered.connect(self.parse_LL1_grammar)
        parse_menu.addAction(parse_LL1_grammar_action)

        parse_SLR_grammar_action = QAction("Analizar gramática SLR(1)", self)
        parse_SLR_grammar_action.triggered.connect(self.parse_SLR_grammar)
        parse_menu.addAction(parse_SLR_grammar_action)

        parse_LALR_grammar_action = QAction("Analizar gramática LALR", self)
        parse_LALR_grammar_action.triggered.connect(self.parse_LALR_grammar)
        parse_menu.addAction(parse_LALR_grammar_action)

        parse_LR_grammar_action = QAction("Analizar gramática LR", self)
        parse_LR_grammar_action.triggered.connect(self.parse_LR_grammar)
        parse_menu.addAction(parse_LR_grammar_action)


    def pestania_simular(self):
        simular_menu = QMenu("Simular", self)
        self.menubar.addMenu(simular_menu)

        self.parse_LL1_input_action = QAction("Analizar entrada LL(1)", self)
        self.parse_LL1_input_action.triggered.connect(self.parse_LL1_input)
        self.parse_LL1_input_action.setEnabled(False)  # Enable/Disable action
        simular_menu.addAction(self.parse_LL1_input_action)

        self.parse_SLR_input_action = QAction("Analizar entrada SLR", self)
        self.parse_SLR_input_action.triggered.connect(self.parse_SLR_input)
        self.parse_SLR_input_action.setEnabled(False)  # Enable/Disable action
        simular_menu.addAction(self.parse_SLR_input_action)

        self.parse_LALR_input_action = QAction("Analizar entrada LALR", self)
        self.parse_LALR_input_action.triggered.connect(self.parse_LALR_input)
        self.parse_LALR_input_action.setEnabled(False)  # Enable/Disable action
        simular_menu.addAction(self.parse_LALR_input_action)

        self.parse_LR_input_action = QAction("Analizar entrada LR", self)
        self.parse_LR_input_action.triggered.connect(self.parse_LR_input)
        self.parse_LR_input_action.setEnabled(False)  # Enable/Disable action
        simular_menu.addAction(self.parse_LR_input_action)


    def menu_inicial(self):
        self.pestania_gramatica()
        self.pestania_editar()
        self.pestania_buscar()
        self.pestania_texto()
        self.pestania_ayuda()

        self.text_grammar.setReadOnly(False)  # Activamos modo escritura
        self.mode_label.setText(f"Modo: escritura")

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

        self.text_grammar.setReadOnly(True)  # Activamos modo lectura
        self.mode_label.setText(f"Modo: lectura")


    #def closeEvent(self, event): # FIXME
    #    self.exit()


    def update_row_column(self):
        cursor = self.text_grammar.textCursor()
        row = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.row_label.setText(f"Línea: {row}")
        self.column_label.setText(f"Columna: {col}")
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
            self.log_window.add_information("Gramatica analizada con exito.")

        except SyntaxError as e:
            self.log_window.add_information("Gramatica analizada sin exito.")
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Critical)
            error_message.setWindowTitle("Error")
            error_message.setText(str(e))
            error_message.setStandardButtons(QMessageBox.Ok)
            error_message.exec_()

    def new_app(self):  # TODO COMPROBAR QUE FUNCIONA EN WINDOWS
        self.log_window.add_information("Abriendo nueva ventana")
        python_path = sys.executable
        os.system(python_path + " " + os.path.abspath(__file__) + " &")

    def open_file(self):
        dialogo = QFileDialog(self, "Abrir archivo")
        dialogo.setFileMode(QFileDialog.ExistingFile)

        if dialogo.exec_() == QFileDialog.Accepted:
            # Obtenemos la ruta del archivo
            self.file = dialogo.selectedFiles()[0]
            text = open(self.file).read()
            self.log_window.add_information("Abriendo el fichero " + self.file)
            self.log_window.add_information("Fichero abierto")

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
            file = QFileDialog.getSaveFileName(self, 'Guardar fichero')[0]
            if not file:
                return

        file = open(file, 'w')
        texto = self.text_grammar.toPlainText()
        file.write(texto)
        file.close()
        self.log_window.add_information("Guardada la gramática en el fichero " + file)

    def save_file_as(self):
        file, _ = QFileDialog.getSaveFileName(self, 'Guardar fichero como')
        if file:
            fichero = open(file, 'w')
            texto = self.text_grammar.toPlainText()
            fichero.write(texto)
            fichero.close()
            self.log_window.add_information("Guardada la gramática en el fichero " + file)

    def exit(self):
        confirm_dialog = QMessageBox(self)
        confirm_dialog.setWindowTitle("¿Desea salir de la aplicación?")
        confirm_dialog.setText("¿Desea salir de la aplicación? (Se perderán todos los datos no guardados)")
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
        message = "ANAGRA 3.0: Herramienta para el estudio de gramaticas\n  " \
                  " libres de contexto y técnicas de analisis sintáctico \n\n" \
                  "Realizado por: Laura González Pizarro \n" \
                  "Dirigido por: Joaquín Ezpeleta Mateo"
        QMessageBox.information(self, 'About...', message)

    def change_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.text_grammar.setFont(font)
            # FIXME CAMBIAR JSON

    def change_colour(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_grammar.setStyleSheet(f"color: {color.name()};")
            # FIXME CAMBIAR JSON


    def change_tab(self):  # TODO cambiar y ver qué hago
        spaces, ok = QInputDialog.getText(self, 'Tabulador', 'Espacios del tabulador:')
        if ok:
            print(spaces)
            # FIXME CAMBIAR JSON


    def cambiar_idioma(self, english):
        if (not english and self.english_checkbox.isChecked()) or (english and self.spanish_checkbox.isChecked()):
            confirm_dialog = QMessageBox(self)
            confirm_dialog.setWindowTitle("Cambio idioma")
            confirm_dialog.setText("Desea cambiar de idioma (los cambios se realizaran la siguiente vez que se inicie ANAGRA)")
            confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            result = confirm_dialog.exec_()
            if result == QMessageBox.Yes:
                if english:
                    self.english_checkbox.setChecked(True)
                    self.spanish_checkbox.setChecked(False)
                else:
                    self.english_checkbox.setChecked(False)
                    self.spanish_checkbox.setChecked(True)
            else:
                if english:
                    self.english_checkbox.setChecked(False)
                else:
                    self.spanish_checkbox.setChecked(False)
        elif english:
            self.english_checkbox.setChecked(True)
        else:
            self.spanish_checkbox.setChecked(True)

    def calcular_conjunto_primero(self):
        self.log_window.add_information("Calculando el Conjunto PRIMERO...")
        first_set = conj.calculate_first_set(self.terminal_tokens, self.non_terminal_tokens, self.productions)
        first_set_window = conj_tab.FirstSet(first_set, self)
        first_set_window.show()

    def calcular_conjunto_siguiente(self):
        self.log_window.add_information("Calculando el Conjunto SIGUIENTE...")
        follow_set = conj.calculate_follow_set(self.start_token, self.terminal_tokens, self.non_terminal_tokens,
                                               self.productions)
        follow_set_window = conj_tab.FollowSet(follow_set, self)
        follow_set_window.show()

    def calcular_conjunto_primero_frase(self):
        first_set_sentence_window = FirstSetSentenceWindow(self)
        first_set_sentence_window.show()

    def left_factoring(self):
        self.log_window.add_information("APLICANDO TRANSFORMACIÓN: Factorizacion a izquierda")
        self.log_window.add_information("TRANSFORMACION APLICADA. Abierta nueva ventana con la gramatica equivalente.")
        non_terminal_tokens, productions = ot.factorizacion_izquierda(self.non_terminal_tokens.copy(),
                                                                      copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def transformacion_no_derivables(self):
        self.log_window.add_information("APLICANDO TRANSFORMACIÓN: Eliminación de los NO terminales que no derivan nada.")
        self.log_window.add_information("TRANSFORMACION APLICADA. Abierta nueva ventana con la gramatica equivalente.")
        non_terminal_tokens, productions = ot.eliminacion_simolos_no_termibales(self.start_token,
                                                                                self.terminal_tokens.copy(),
                                                                                self.non_terminal_tokens.copy(),
                                                                                copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()
        if self.start_token in productions:     # todo no se que habia que comprobar
            QMessageBox.information(self, "ATENCIÓN!!", "La gramática original y la transformada reconocen la palabra vacía")


    def eliminating_left_recursion(self):
        self.log_window.add_information("APLICANDO TRANSFORMACIÓN: Eliminación de la recursividad a izquierda.")
        self.log_window.add_information("TRANSFORMACION APLICADA. Abierta nueva ventana con la gramatica equivalente.")
        non_terminal_tokens, productions, _ = ot.eliminar_recursividad_izquierda(self.start_token,
                                                                                 self.non_terminal_tokens.copy(),
                                                                                 copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def transformacion_no_alcanzables(self):  # TODO COMPROBAR SI EL LENGUAGE ES VACIO O NO JIIJIJ
        self.log_window.add_information("APLICANDO TRANSFORMACIÓN: Eliminación de los NO terminales no accesibles.")
        self.log_window.add_information("TRANSFORMACION APLICADA. Abierta nueva ventana con la gramatica equivalente.")
        terminal_tokens, non_terminal_tokens, productions = ot.eliminacion_simbolos_inutiles(self.start_token,
                                                                                             self.terminal_tokens.copy(),
                                                                                             self.non_terminal_tokens.copy(),
                                                                                             copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def eliminating_eps_prod(self):
        self.log_window.add_information("APLICANDO TRANSFORMACIÓN: Eliminación producciones epsilon")
        self.log_window.add_information("TRANSFORMACION APLICADA. Abierta nueva ventana con la gramatica equivalente.")
        productions = ot.eliminacion_producciones_epsilon(self.start_token, self.terminal_tokens,
                                                          self.non_terminal_tokens.copy(),
                                                          copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, self.non_terminal_tokens, productions, self)
        new_window.show()

    def eliminating_unit_prod(self):
        self.log_window.add_information("APLICANDO TRANSFORMACIÓN: Eliminación de Ciclos.")
        self.log_window.add_information("TRANSFORMACION APLICADA. Abierta nueva ventana con la gramatica equivalente.")
        productions = ot.eliminacion_producciones_unitarias(self.terminal_tokens.copy(),
                                                            self.non_terminal_tokens.copy(),
                                                            copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, self.non_terminal_tokens, productions, self)
        new_window.show()

    def chomsky_normal_form(self):
        self.log_window.add_information("APLICANDO TRANSFORMACIÓN: Forma normal de Chomsky")
        self.log_window.add_information("TRANSFORMACION APLICADA. Abierta nueva ventana con la gramatica equivalente.")
        productions = ot.forma_normal_chomsky(self.start_token, self.terminal_tokens.copy(),
                                              self.non_terminal_tokens.copy(), copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, self.non_terminal_tokens, productions, self)
        new_window.show()

    def greibach_normal_form(self):
        self.log_window.add_information("APLICANDO TRANSFORMACIÓN: Forma normal de Greibach")
        self.log_window.add_information("TRANSFORMACION APLICADA. Abierta nueva ventana con la gramatica equivalente.")
        non_terminal_tokens, productions = ot.forma_normal_greibach(self.start_token, self.non_terminal_tokens.copy(),
                                                                    copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def parse_LL1_grammar(self):
        if not self.table_LL1:
            self.log_window.add_information("Analizando la gramática para ver si es de tipo LL(1).")
            self.table_LL1 = LL1.calculate_table(self.start_token, self.terminal_tokens, self.non_terminal_tokens,
                                                 self.productions)

            # Enable options if possible
            conclicts_ll1 = LL1.is_ll1(self.table_LL1, self.terminal_tokens, self.non_terminal_tokens)
            is_ll1 = conclicts_ll1 == 0
            if is_ll1:
                self.log_window.add_information("CORRECTO: La gramática es de tipo LL(1).")
            else:
                self.log_window.add_information("ERROR: La gramática no es de tipo LL(1).")
                self.log_window.add_information("Numero Celdas en Conflicto: " + str(conclicts_ll1))

            self.parse_LL1_input_action.setEnabled(is_ll1)

        analysis_table_window = conj_tab.AnalysisTableLL1(self.table_LL1, self)
        analysis_table_window.show()

    def parse_SLR_grammar(self):
        if not (self.conj_LR0 and self.action_table_SLR and self.go_to_table_SLR and self.edges_SLR):
            self.log_window.add_information("Analizando la gramática para ver si es de tipo SLR(1).")
            self.token_inicial_ampliado, self.tokens_no_terminales_ampliados, self.producciones_ampliados = SLR.extend_grammar(self.start_token, self.non_terminal_tokens.copy(), copy.deepcopy(self.productions))
            self.conj_LR0 = SLR.conj_LR0(self.token_inicial_ampliado, self.tokens_no_terminales_ampliados, self.producciones_ampliados)
            self.action_table_SLR = SLR.action_table(self.conj_LR0, self.token_inicial_ampliado, self.terminal_tokens, self.tokens_no_terminales_ampliados, self.producciones_ampliados)
            self.go_to_table_SLR = SLR.go_to_table(self.conj_LR0, self.tokens_no_terminales_ampliados, self.producciones_ampliados)
            self.edges_SLR = SLR.create_automaton(self.conj_LR0, self.terminal_tokens, self.non_terminal_tokens, self.productions)

            # Enable options if possible
            conclicts_slr1 = SLR.is_slr1(self.action_table_SLR)
            is_slr1 = conclicts_slr1 == 0
            if is_slr1:
                self.log_window.add_information("CORRECTO: La gramática es de tipo SLR(1).")
            else:
                self.log_window.add_information("ERROR: La gramática no es de tipo SLR(1).")
                self.log_window.add_information("Numero Celdas en Conflicto en la Tabla ACCION: " + str(conclicts_slr1))
                self.log_window.add_information("Numero Celdas en Conflicto en la Tabla IR A:")

            self.parse_SLR_input_action.setEnabled(is_slr1)

        conj_tab.AnalysisTableSLR1(self.action_table_SLR, self.go_to_table_SLR, self.conj_LR0, self.edges_SLR,
                                   self.terminal_tokens, self.non_terminal_tokens, self.token_inicial_ampliado,
                                   self.producciones_ampliados, ventana, "SLR(1)", self)


    def parse_LALR_grammar(self):
        if not (self.conj_LALR and self.action_table_LALR and self.go_to_table_LALR and self.edges_LALR):
            self.log_window.add_information("Analizando la gramática para ver si es de tipo LALR.")
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
                self.log_window.add_information("CORRECTO: La gramática es de tipo LALR.")
            else:
                self.log_window.add_information("ERROR: La gramática no es de tipo LALR.")
                self.log_window.add_information("Numero Celdas en Conflicto en la Tabla ACCION: " + str(conclicts_lalr))
                self.log_window.add_information("Numero Celdas en Conflicto en la Tabla IR A:")

            self.parse_LALR_input_action.setEnabled(is_lalr)

        conj_tab.AnalysisTableSLR1(self.action_table_LALR, self.go_to_table_LALR, self.conj_LALR, self.edges_LALR,
                                   self.terminal_tokens, self.non_terminal_tokens, self.token_inicial_ampliado,
                                   self.producciones_ampliados, ventana, "LALR", self)

    def parse_LR_grammar(self):
        if not (self.conj_LR1 and self.action_table_LR and self.go_to_table_LR and self.edges_LR):
            self.log_window.add_information("Analizando la gramática para ver si es de tipo LR(1).")
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
                self.log_window.add_information("CORRECTO: La gramática es de tipo LR(1).")
            else:
                self.log_window.add_information("ERROR: La gramática no es de tipo LR(1).")
                self.log_window.add_information("Numero Celdas en Conflicto en la Tabla ACCION: " + str(conclicts_lr))
                self.log_window.add_information("Numero Celdas en Conflicto en la Tabla IR A:")

            self.parse_LR_input_action.setEnabled(is_lr)

        conj_tab.AnalysisTableSLR1(self.action_table_LR, self.go_to_table_LR, self.conj_LR1, self.edges_LR,
                                   self.terminal_tokens, self.non_terminal_tokens, self.token_inicial_ampliado,
                                   self.producciones_ampliados, ventana, "LR",self)

    def parse_LL1_input(self):
        self.log_window.add_information("Simulando analizador sintáctico LL(1) asociado a la gramática.")
        ll1_input_window = VentanaInputGramatica("LL1", self)
        ll1_input_window.show()

    def parse_SLR_input(self):
        self.log_window.add_information("Simulando analizador sintáctico SLR(1) asociado a la gramática.")
        input_window = VentanaInputGramatica("SLR1", self)
        input_window.show()

    def parse_LALR_input(self):
        self.log_window.add_information("Simulando analizador sintáctico LALR asociado a la gramática.")
        input_window = VentanaInputGramatica("LALR", self)
        input_window.show()

    def parse_LR_input(self):
        self.log_window.add_information("Simulando analizador sintáctico LR(1) asociado a la gramática.")
        input_window = VentanaInputGramatica("LR", self)
        input_window.show()

    def show_grammar(self):
        text = f"%start {self.start_token}\n%%\n\n"
        for token, prods_token in self.productions.items():
            text += token + ": "
            spacing = " " * (len(token) + 2)
            for index, prod in enumerate(prods_token):
                if prod is not None:
                    for token_prod in prod:
                        text += token_prod + "  "
                if index != len(self.productions[token]) - 1:
                    text += "\n" + spacing + "| "
            text += "\n;\n\n"
        text += "%%"
        self.text_grammar.setPlainText(text)

    def show_compact_grammar(self):
        text = f"%start {self.start_token}\n%%\n"
        for token, prods_token in self.productions.items():
            text += token + ": "
            for index, prod in enumerate(prods_token):
                if prod is not None:
                    for token_prod in prod:
                        text += token_prod + "  "
                if index != len(self.productions[token]) - 1:
                    text += "| "
            text += ";\n"
        text += "%%"
        self.text_grammar.setPlainText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    app.exec_()
    sys.exit()
