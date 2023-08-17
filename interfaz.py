import copy
import os
import sys

from PyQt5.QtGui import QKeySequence, QClipboard, QTextCursor, QTextCharFormat, QColor, QTextDocument
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QCheckBox, QWidgetAction, \
    QPlainTextEdit, QMessageBox, QFileDialog, QStatusBar, QLabel, qApp, QVBoxLayout, \
    QPushButton, QWidget, QComboBox, QHBoxLayout, QDesktopWidget, QInputDialog, QTextEdit, QFontDialog, QColorDialog

import LL1
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


class VentanaInputGramatica(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        tabla = LL1.simulate(ventana.table, ventana.start_token, ventana.terminal_tokens, texto + "$")
        nueva_ventana = sim.VentanaSimulacion(tabla, ventana.start_token, ventana.terminal_tokens,
                                              ventana.non_terminal_tokens, self)
        nueva_ventana.show()


class VentanaInput(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
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

        row_layout = QHBoxLayout()
        self.checkbox_dibujar_arbol = QCheckBox("Dibujar árbol")
        row_layout.addWidget(self.checkbox_dibujar_arbol)

        label_gramatica = QLabel("Gramática:")
        row_layout.addWidget(label_gramatica)

        self.dropdown_gramatica = QComboBox()
        self.dropdown_gramatica.addItems(["Opción 1", "Opción 2", "Opción 3"])
        row_layout.addWidget(self.dropdown_gramatica)

        layout.addLayout(row_layout)
        boton_aceptar = QPushButton("Aceptar", self)
        boton_aceptar.clicked.connect(self.accept)
        layout.addWidget(boton_aceptar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def accept(self):
        self.texto = self.text_edit.toPlainText()
        self.dibujar_arbol = self.checkbox_dibujar_arbol.isChecked()
        self.opcion_gramatica = self.dropdown_gramatica.currentText()
        print("Texto ingresado:", self.texto)
        print("Dibujar árbol:", self.dibujar_arbol)
        print("Opción de Gramática seleccionada:", self.opcion_gramatica)
        self.close()


class RemplaceWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, 450, 150)
        center_window(self)

        self.setWindowTitle('Remplazar')
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.label1 = QLabel("Texto 1:")
        self.text_input1 = QPlainTextEdit()
        layout.addWidget(self.label1)
        layout.addWidget(self.text_input1)

        self.label2 = QLabel("Texto 2:")
        self.text_input2 = QPlainTextEdit()
        layout.addWidget(self.label2)
        layout.addWidget(self.text_input2)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        # Establecer el widget principal y el
        self.setCentralWidget(central_widget)

    def accept(self):
        old = self.text_input1.toPlainText()
        new = self.text_input2.toPlainText()
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

        else:
            self.close()
            message_box = QMessageBox()
            message_box.setWindowTitle("Mensaje")
            message_box.setText(f'La palabra "{old}" no se encontró en el texto.')
            message_box.setIcon(QMessageBox.Critical)
            message_box.exec_()


class MainWindow(QMainWindow):
    def pestania_gramatica(self, gramatica=False):
        grammar_menu = QMenu("Gramática", self)
        self.menubar.addMenu(grammar_menu)

        # Options grammar menu
        new_action = QAction("Nuevo", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_app)
        grammar_menu.addAction(new_action)

        open_action = QAction("Abrir", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setEnabled(not self.file)  # Enable/Disable action
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

        # Agregar las opciones de menú al menú grmática
        grammar_menu.addSeparator()

        exit_action = QAction("Salir", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.exit)
        grammar_menu.addAction(exit_action)

    def pestania_editar(self, gramatica=False):
        editar_menu = QMenu("Editar", self)
        self.menubar.addMenu(editar_menu)

        # Opciones de menú al menú editar
        cut_action = QAction("Cortar", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.cut)
        editar_menu.addAction(cut_action)

        copiar_action = QAction("Copiar", self)
        copiar_action.setShortcut(QKeySequence.Copy)
        copiar_action.triggered.connect(self.copy)
        editar_menu.addAction(copiar_action)

        pegar_action = QAction("Pegar", self)
        pegar_action.setShortcut(QKeySequence.Paste)
        pegar_action.triggered.connect(self.paste)
        editar_menu.addAction(pegar_action)

        borrar_action = QAction("Borrar", self)
        editar_menu.addAction(borrar_action)

        seleccionar_todo_action = QAction("Seleccionar todo", self)
        seleccionar_todo_action.setShortcut(QKeySequence.SelectAll)
        seleccionar_todo_action.triggered.connect(self.select_all)
        editar_menu.addAction(seleccionar_todo_action)

        editar_menu.addSeparator()  # Línea de separación

        aceptar_gramatica_action = QAction("Aceptar gramática", self)
        aceptar_gramatica_action.triggered.connect(self.accept_grammar)
        aceptar_gramatica_action.setEnabled(not gramatica)  # Enable/Disable action
        editar_menu.addAction(aceptar_gramatica_action)

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
        font_action.triggered.connect(self.cambiar_fuente)

        color_action = QAction("Color", self)
        color_action.triggered.connect(self.cambiar_color)

        tab_action = QAction("Tab", self)
        tab_action.triggered.connect(self.cambiar_tab)

        extended_action = QAction("Extended", self)
        extended_action.triggered.connect(self.show_grammar)
        extended_action.setEnabled(gramatica)  # Enable/Disable action

        compact_action = QAction("Compact", self)
        compact_action.triggered.connect(self.show_compact_grammar)
        compact_action.setEnabled(gramatica)  # Enable/Disable action

        idiomaSubmenu = QMenu("Idioma", self)

        idiomaEnglish = QCheckBox("English", self)
        idiomaEnglish.stateChanged.connect(self.cambiar_idioma)
        widgetEnglish = QWidgetAction(self)
        widgetEnglish.setDefaultWidget(idiomaEnglish)

        idiomaCastellano = QCheckBox("Castellano", self)
        idiomaCastellano.stateChanged.connect(self.cambiar_idioma)
        widgetCastellano = QWidgetAction(self)
        widgetCastellano.setDefaultWidget(idiomaCastellano)

        idiomaSubmenu.setContentsMargins(15, 0, 0, 0)
        idiomaSubmenu.addAction(widgetEnglish)
        idiomaSubmenu.addAction(widgetCastellano)
        guardarPreferenciasAction = QAction("Guardar preferencias", self)

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
        about_action = QAction("Sobre...", self)
        about_action.triggered.connect(self.show_information)
        help_menu.addAction(about_action)

    def pestania_herramientas(self):
        tools_menu = QMenu("Herramientas", self)
        self.menubar.addMenu(tools_menu)

        # Opciones de menú al menú herramientas
        first_set_action = QAction("Calcular conjunto PRIMERO", self)
        first_set_action.triggered.connect(self.calcular_conjunto_primero)

        follow_set_action = QAction("Calcular conjunto SIGUIENTE", self)
        follow_set_action.triggered.connect(self.calcular_conjunto_siguiente)

        conjunto_primero_frase_action = QAction("Analisis", self)  # TODO: mirar que es
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

        self.show_LL1_table_action = QAction("Mostrar tabla LL(1)", self)
        self.show_LL1_table_action.triggered.connect(self.show_LL1_table)
        self.show_LL1_table_action.setEnabled(False)  # Enable/Disable action
        parse_menu.addAction(self.show_LL1_table_action)

        parse_SLR_grammar_action = QAction("Analizar gramática SLR", self)
        parse_SLR_grammar_action.triggered.connect(self.parse_SLR_grammar)
        parse_menu.addAction(parse_SLR_grammar_action)

        self.show_SLR_table_action = QAction("Mostrar tabla SLR", self)
        self.show_SLR_table_action.triggered.connect(self.show_SLR_table)
        self.show_SLR_table_action.setEnabled(False)  # Enable/Disable action
        parse_menu.addAction(self.show_SLR_table_action)

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

        simular_menu.addSeparator()

        self.parse_input_action = QAction("Analizar entrada", self)
        self.parse_input_action.triggered.connect(self.parse_input)
        self.parse_input_action.setEnabled(False)  # Enable/Disable action
        simular_menu.addAction(self.parse_input_action)

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

        self.setWindowTitle("Anagra")
        self.setGeometry(0, 0, 800, 600)
        # Center window to the middle of the screen
        center_window(self)

        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.text_grammar = QPlainTextEdit(self)
        self.text_grammar.cursorPositionChanged.connect(self.update_row_column)
        self.setCentralWidget(self.text_grammar)

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
            self.text_grammar.setReadOnly(False)  # Activamos modo lectura
            self.mode_label.setText(f"Modo: escritura")

        self.update_row_column()

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
        try:
            grammar = yacc.parse(text)
            self.start_token = grammar[0]
            self.terminal_tokens = grammar[1]
            self.non_terminal_tokens = grammar[2]
            self.productions = grammar[3]

            self.menu_gramaticas()
            self.text_grammar.setPlainText(text)

        except SyntaxError as e:
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
        dialogo = QFileDialog(self, "Abrir archivo")
        dialogo.setFileMode(QFileDialog.ExistingFile)

        if dialogo.exec_() == QFileDialog.Accepted:
            # Obtenemos la ruta del archivo
            self.file = dialogo.selectedFiles()[0]
            text = open(self.file).read()
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
        self.file = False

        self.menubar.clear()
        self.menu_inicial()

    def save_file(self):
        if self.file:
            file = self.file
        else:
            file = QFileDialog.getSaveFileName(self, 'Guardar fichero')[0]
            if not file:
                return

        file = open(file, 'w')
        texto = self.text_grammar.toPlainText()
        file.write(texto)
        file.close()

    def save_file_as(self):
        name_fich, _ = QFileDialog.getSaveFileName(self, 'Guardar fichero como')
        if name_fich:
            fichero = open(name_fich, 'w')
            texto = self.text_grammar.toPlainText()
            fichero.write(texto)
            fichero.close()

    def exit(self):
        confirm_dialog = QMessageBox(self)
        confirm_dialog.setWindowTitle("¿Desea salir de la aplicación?")
        confirm_dialog.setText("¿Desea salir de la aplicación? (Se perderán todos los datos no guardados)")
        confirm_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)

        result = confirm_dialog.exec_()
        if result == QMessageBox.Yes:
            QApplication.quit()

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

    def accept_grammar(self):
        text = self.text_grammar.toPlainText()
        self.yacc_parse_grammar(text)

    def find(self):  # TODO
        text = self.text_grammar.toPlainText()
        search_word, ok = QInputDialog.getText(self, 'Buscar Palabra', 'Ingrese la palabra a buscar:')
        if ok and search_word:
            if search_word in text:
                options = QTextDocument.FindWholeWords | QTextDocument.FindCaseSensitively
                cursor = QTextCursor(self.text_grammar.document())
                selections = []

                while not cursor.isNull():
                    cursor = self.text_grammar.document().find(search_word, cursor, options)
                    if not cursor.isNull():
                        sel = QTextEdit.ExtraSelection()
                        sel.format.setBackground(QColor("green"))  # Cambiar el color de fondo a amarillo
                        sel.cursor = cursor
                        selections.append(sel)

                self.text_grammar.setExtraSelections(selections)

            else:
                message_box = QMessageBox()
                message_box.setWindowTitle("Mensaje")
                message_box.setText(f'La palabra "{search_word}" no se encontró en el texto.')
                message_box.setIcon(QMessageBox.Warning)
                message_box.exec_()

    def remplace(self):  # TODO
        remplace_window = RemplaceWindow(self)
        remplace_window.show()

    def cut(self):
        clipboard = qApp.clipboard()
        texto = self.text_grammar.textCursor().selectedText()  # Obtenemos el texto seleccionado
        clipboard.setText(texto)  # Lo guardamos en el clipboard
        self.text_grammar.textCursor().removeSelectedText()  # Borramos el texto seleccionado

    def copy(self):
        clipboard = qApp.clipboard()
        text = self.text_grammar.textCursor().selectedText()  # Obtenemos el texto seleccionado
        clipboard.setText(text)  # Lo guardamos en el portapapeles

    def paste(self):
        clipboard = qApp.clipboard()
        text = clipboard.text(QClipboard.Clipboard)  # Obtenemos el texto del portapapeles
        self.text_grammar.textCursor().insertText(text)  # Lo pegamos

    def erease(self):
        self.text_grammar.textCursor().removeSelectedText()  # Borramos el texto seleccionado

    def select_all(self):
        cursor = self.text_grammar.textCursor()
        cursor.select(QTextCursor.Document)
        self.text_grammar.setTextCursor(cursor)

    def show_information(self):  # TODO
        message = "ANAGRA 3.0: Herramienta para el estudio de gramaticas\n   libres de contexto y técnicas de analisis sintáctico \n\nRealizado por: Laura González Pizarro \nDirigido por: Joaquín Ezpeleta Mateo"
        QMessageBox.information(self, 'About...', message)

    def cambiar_fuente(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.text_grammar.setFont(font)

    def cambiar_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_grammar.setStyleSheet(f"color: {color.name()};")

    def cambiar_tab(self):  # TODO
        spaces, ok = QInputDialog.getText(self, 'Tabulador', 'Espacios del tabulador:')
        if ok:
            print(spaces)

    def cambiar_idioma(self):
        # Mostramos una ventana de mensaje con un pequeño texto
        QMessageBox.information(self, "Cambio idioma",
                                "Los cambios se realizaran la siguiente vez que se inicie Anagra")

    def calcular_conjunto_primero(self):
        first_set = conj.calculate_first_set(self.terminal_tokens, self.non_terminal_tokens, self.productions)
        first_set_window = conj_tab.FirstSet(first_set, self)
        first_set_window.show()

    def calcular_conjunto_siguiente(self):
        follow_set = conj.calculate_follow_set(self.start_token, self.terminal_tokens, self.non_terminal_tokens,
                                               self.productions)
        follow_set_window = conj_tab.FollowSet(follow_set, self)
        follow_set_window.show()

    def calcular_conjunto_primero_frase(self):
        self.table = conj.calculate_table(self.start_token, self.terminal_tokens, self.non_terminal_tokens,
                                          self.productions)
        table = {index: elem for index, elem in enumerate(self.table)}
        simulation_window = conj_tab.SimulationTable(table, self)
        simulation_window.show()

    def left_factoring(self):
        non_terminal_tokens, productions = ot.factorizacion_izquierda(self.non_terminal_tokens.copy(),
                                                                      copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def transformacion_no_derivables(self):
        non_terminal_tokens, productions = ot.eliminacion_simolos_no_termibales(self.start_token,
                                                                                self.terminal_tokens.copy(),
                                                                                self.non_terminal_tokens.copy(),
                                                                                copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def eliminating_left_recursion(self):
        non_terminal_tokens, productions, _ = ot.eliminar_recursividad_izquierda(self.start_token,
                                                                                 self.non_terminal_tokens.copy(),
                                                                                 copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def transformacion_no_alcanzables(self):  # TODO COMPROBAR SI EL LENGUAGE ES VACIO O NO JIIJIJ
        terminal_tokens, non_terminal_tokens, productions = ot.eliminacion_simbolos_inutiles(self.start_token,
                                                                                             self.terminal_tokens.copy(),
                                                                                             self.non_terminal_tokens.copy(),
                                                                                             copy.deepcopy(
                                                                                                 self.productions))
        new_window = MainWindow(self.start_token, terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def eliminating_eps_prod(self):
        productions = ot.eliminacion_producciones_epsilon(self.start_token, self.non_terminal_tokens.copy(),
                                                          copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, self.non_terminal_tokens, productions, self)
        new_window.show()

    def eliminating_unit_prod(self):
        productions = ot.eliminacion_producciones_unitarias(self.terminal_tokens.copy(),
                                                            self.non_terminal_tokens.copy(),
                                                            copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, self.non_terminal_tokens, productions, self)
        new_window.show()

    def chomsky_normal_form(self):
        productions = ot.forma_normal_chomsky(self.start_token, self.terminal_tokens.copy(),
                                              self.non_terminal_tokens.copy(), copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, self.non_terminal_tokens, productions, self)
        new_window.show()

    def greibach_normal_form(self):
        non_terminal_tokens, productions = ot.forma_normal_greibach(self.start_token, self.non_terminal_tokens.copy(),
                                                                    copy.deepcopy(self.productions))
        new_window = MainWindow(self.start_token, self.terminal_tokens, non_terminal_tokens, productions, self)
        new_window.show()

    def parse_LL1_grammar(self):
        self.table = conj.calculate_table(self.start_token, self.terminal_tokens, self.non_terminal_tokens,
                                          self.productions)

        # Enable options if possible
        conclicts_ll1 = LL1.is_ll1(self.table, self.terminal_tokens, self.non_terminal_tokens)
        is_ll1 = conclicts_ll1 == 0
        self.parse_LL1_input_action.setEnabled(is_ll1)
        self.parse_input_action.setEnabled(is_ll1)
        self.show_LL1_table_action.setEnabled(is_ll1)

        analysis_table_window = conj_tab.AnalysisTable(self.table, self)
        analysis_table_window.show()

    def show_LL1_table(self):
        analysis_table_window = conj_tab.AnalysisTable(self.table, self)
        analysis_table_window.show()

    def parse_SLR_grammar(self):
        SLR.ampliar_gramatica(self.start_token, self.non_terminal_tokens, self.productions)

    def show_SLR_table(self):
        print()

    def parse_LL1_input(self):
        ll1_input_window = VentanaInputGramatica(self)
        ll1_input_window.show()

    def parse_SLR_input(self):
        print()

    def parse_input(self):
        input_window = VentanaInput(self)
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
