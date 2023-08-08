import os
import sys

from PyQt5.QtGui import QKeySequence, QClipboard, QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QCheckBox, QWidgetAction, \
    QPlainTextEdit, QMessageBox, QFileDialog, QStatusBar, QLabel, qApp, QVBoxLayout, \
    QPushButton, QWidget, QComboBox, QHBoxLayout

import LL1 
import bisonlex
import bisonparse
from ply import *

import operacionesTransformacion as ot
import conjuntos as conj
import conjuntos_tablas as conj_tab
import simulacion as sim


class NewApplication:
    def __init__(self):
        super().__init__(sys.argv)


class VentanaInputGramatica(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Input")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()

        label = QLabel("Input:")
        layout.addWidget(label)

        self.text_edit = QPlainTextEdit()
        layout.addWidget(self.text_edit)

        boton_aceptar = QPushButton("Aceptar", self)
        boton_aceptar.clicked.connect(self.aceptar)
        layout.addWidget(boton_aceptar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def aceptar(self):
        # Aquí puedes obtener el texto ingresado en el QPlainTextEdit
        texto = self.text_edit.toPlainText()
        print("Texto ingresado:", texto)
        self.close()
        # todo generar entrada
        tabla = LL1.simulate(ventana.tabla, ventana.token_inicial, ventana.tokens_terminales, texto+"$")
        print(tabla)
        nueva_ventana = sim.VentanaSimulacion(tabla, self)
        nueva_ventana.show()


class VentanaInput(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Input")
        self.setGeometry(200, 200, 400, 200)

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
        boton_aceptar.clicked.connect(self.aceptar)
        layout.addWidget(boton_aceptar)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def aceptar(self):
        self.texto = self.text_edit.toPlainText()
        self.dibujar_arbol = self.checkbox_dibujar_arbol.isChecked()
        self.opcion_gramatica = self.dropdown_gramatica.currentText()
        print("Texto ingresado:", self.texto)
        print("Dibujar árbol:", self.dibujar_arbol)
        print("Opción de Gramática seleccionada:", self.opcion_gramatica)
        self.close()
        # TODO LLAMAR A LA SIMULACIÓN DE LA PILA Y CREACIÓN DEL ARBOL


class MainWindow(QMainWindow):
    def pestania_gramatica(self, gramatica=False):
        gramaticaMenu = QMenu("Gramática", self)
        self.menubar.addMenu(gramaticaMenu)

        # Opciones de menú al menú gramatica

        nuevo_action = QAction("Nuevo", self)
        nuevo_action.setShortcut(QKeySequence.New)
        nuevo_action.triggered.connect(self.abrir_nueva_aplicacion)

        abrir_action = QAction("Abrir", self)
        abrir_action.setShortcut(QKeySequence.Open)
        abrir_action.triggered.connect(self.abrir_fichero)

        editar_action = QAction("Editar", self)
        # editar_action.setShortcut(QKeySequence.) TODO NO EXISTE EDITAR
        editar_action.setEnabled(gramatica)  # Deshabilitar la acción

        cerrar_action = QAction("Cerrar", self)
        cerrar_action.setShortcut(QKeySequence.Close)

        guardar_action = QAction("Guardar", self)
        guardar_action.setShortcut(QKeySequence.Save)
        guardar_action.setEnabled(gramatica)  # Deshabilitar la acción

        guardar_como_action = QAction("Guardar como...", self)
        guardar_como_action.setShortcut(QKeySequence.SaveAs)
        guardar_como_action.triggered.connect(self.guardar_como)

        salirAction = QAction("Salir", self)
        salirAction.setShortcut(QKeySequence.Quit)

        # Agregar las opciones de menú al menú grmática
        gramaticaMenu.addAction(nuevo_action)
        gramaticaMenu.addAction(abrir_action)
        gramaticaMenu.addAction(editar_action)
        gramaticaMenu.addAction(cerrar_action)
        gramaticaMenu.addAction(guardar_action)
        gramaticaMenu.addAction(guardar_como_action)
        gramaticaMenu.addSeparator()  # Línea de separación
        gramaticaMenu.addAction(salirAction)
    def pestania_editar(self):
        editar_menu = QMenu("Editar", self)
        self.menubar.addMenu(editar_menu)

        # Opciones de menú al menú editar
        cortar_action = QAction("Cortar", self)
        cortar_action.setShortcut(QKeySequence.Cut)
        cortar_action.triggered.connect(self.cortar)

        copiar_action = QAction("Copiar", self)
        copiar_action.setShortcut(QKeySequence.Copy)
        copiar_action.triggered.connect(self.copiar)

        pegar_action = QAction("Pegar", self)
        pegar_action.setShortcut(QKeySequence.Paste)
        pegar_action.triggered.connect(self.pegar)

        borrar_action = QAction("Borrar", self)

        seleccionar_todo_action = QAction("Seleccionar todo", self)
        seleccionar_todo_action.setShortcut(QKeySequence.SelectAll)
        seleccionar_todo_action.triggered.connect(self.seleccionar_todo)

        aceptar_gramatica_action = QAction("Aceptar gramática", self)
        aceptar_gramatica_action.triggered.connect(self.aceptar_gramatica)

        rechazarGramaticaAction = QAction("Rechazar gramática", self)
        rechazarGramaticaAction.setEnabled(False)  # Deshabilitar la acción

        # Agregar las opciones de menú al menú editar
        editar_menu.addAction(cortar_action)
        editar_menu.addAction(copiar_action)
        editar_menu.addAction(pegar_action)
        editar_menu.addAction(borrar_action)
        editar_menu.addAction(seleccionar_todo_action)
        editar_menu.addSeparator()  # Línea de separación
        editar_menu.addAction(aceptar_gramatica_action)
        editar_menu.addAction(rechazarGramaticaAction)

    def pestania_buscar(self):
        buscar_menu = QMenu("Buscar", self)
        self.menubar.addMenu(buscar_menu)

        # Opciones de menú al menú buscar
        buscar_action = QAction("Buscar", self)
        buscar_action.setShortcut(QKeySequence.Find)
        reemplazar_action = QAction("Reemplazar", self)
        reemplazar_action.setShortcut(QKeySequence.Replace)
        buscar_de_nuevo_action = QAction("Buscar de nuevo", self)
        buscar_de_nuevo_action.setEnabled(False)  # Deshabilitar la acción
        # buscar_de_nuevo_action.setShortcut(QKeySequence.FindNext)  TODO NO SE CUAL ES, SHIFT+B NO ES NADA
        irALineaAction = QAction("Ir a linea...", self)

        # Agregar las opciones de menú al menú buscar
        buscar_menu.addAction(buscar_action)
        buscar_menu.addAction(reemplazar_action)
        buscar_menu.addAction(buscar_de_nuevo_action)
        buscar_menu.addSeparator()  # Línea de separación
        buscar_menu.addAction(irALineaAction)

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
        extended_action.triggered.connect(self.mostrar_gramatica)
        extended_action.setEnabled(gramatica)  # Deshabilitar la acción

        compact_action = QAction("Compact", self)
        compact_action.triggered.connect(self.mostrar_gramatica_compacta)
        compact_action.setEnabled(gramatica)  # Deshabilitar la acción

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
        ayuda_menu = QMenu("Ayuda", self)
        self.menubar.addMenu(ayuda_menu)

        # Opciones de menú al menú ayuda
        sobre_action = QAction("Sobre...", self)
        sobre_action.triggered.connect(self.mostrar_informacion)

        # Agregar las opciones de menú al menú ayuda
        ayuda_menu.addAction(sobre_action)

    def pestania_herramientas(self):
        herramientas_menu = QMenu("Herramientas", self)
        self.menubar.addMenu(herramientas_menu)

        # Opciones de menú al menú herramientas
        conjunto_primero_action = QAction("Calcular conjunto PRIMERO", self)
        conjunto_primero_action.triggered.connect(self.calcular_conjunto_primero)

        conjunto_siguiente_action = QAction("Calcular conjunto SIGUIENTE", self)
        conjunto_siguiente_action.triggered.connect(self.calcular_conjunto_siguiente)

        conjunto_primero_frase_action = QAction("Analisis", self) # TODO: mirar que es
        conjunto_primero_frase_action.triggered.connect(self.calcular_conjunto_primero_frase)

        # Agregar las opciones de menú al menú herramientas
        herramientas_menu.addAction(conjunto_primero_action)
        herramientas_menu.addAction(conjunto_siguiente_action)
        herramientas_menu.addAction(conjunto_primero_frase_action)

    def pestania_transformaciones(self):
        transformaciones_menu = QMenu("Transformaciones", self)
        self.menubar.addMenu(transformaciones_menu)

        # Opciones de menú al menú transformaciones
        factorizacion_izquierda_action = QAction("Factorización a izquierda", self)
        factorizacion_izquierda_action.triggered.connect(self.transformacion_factorizacion_izquierda)

        eliminacion_no_derivables_action = QAction("Eliminación de no terminales no derivables", self)
        eliminacion_no_derivables_action.triggered.connect(self.transformacion_no_derivables)

        eliminacion_recursividad_izq_action = QAction("Eliminación de recursividad a izquierda", self)
        eliminacion_recursividad_izq_action.triggered.connect(self.transformacion_recursividad_izquierda)

        eliminacion_no_alcanzables_action = QAction("Eliminación de símbolos no alcanzables", self)
        eliminacion_no_alcanzables_action.triggered.connect(self.transformacion_no_alcanzables)

        eliminacion_producciones_eps_action = QAction("Eliminación de producciones epsilon", self)
        eliminacion_producciones_eps_action.triggered.connect(self.transformacion_producciones_epsilon)

        eliminacion_ciclos_action = QAction("Eliminación de ciclos", self)
        eliminacion_ciclos_action.triggered.connect(self.transformacion_eliminacion_ciclos)

        forma_normal_chomsky = QAction("Forma nomral de Chomsky", self)
        forma_normal_chomsky.triggered.connect(self.forma_normal_chomsky)

        forma_normal_greibach = QAction("Forma nomral de Greibach", self)
        forma_normal_greibach.triggered.connect(self.forma_normal_greibach)

        # Agregar las opciones de menú al menú transformaciones
        transformaciones_menu.addAction(factorizacion_izquierda_action)
        transformaciones_menu.addAction(eliminacion_no_derivables_action)
        transformaciones_menu.addAction(eliminacion_recursividad_izq_action)
        transformaciones_menu.addAction(eliminacion_no_alcanzables_action)
        transformaciones_menu.addAction(eliminacion_producciones_eps_action)
        transformaciones_menu.addAction(eliminacion_ciclos_action)
        transformaciones_menu.addAction(forma_normal_chomsky)
        transformaciones_menu.addAction(forma_normal_greibach)

    def pestania_parse(self):
        parseMenu = QMenu("Parse", self)
        self.menubar.addMenu(parseMenu)

        # Opciones de menú al menú parse
        parsearGramaticaLL1Action = QAction("Analizar gramática LL(1)", self)
        parsearGramaticaLL1Action.triggered.connect(self.parsear_gramatica_LL1)

        self.mostrarTableLL1Action = QAction("Mostrar tabla LL(1)", self)
        self.mostrarTableLL1Action.triggered.connect(self.mostrar_tabla_LL1)

        self.mostrarTableLL1Action.setEnabled(False)  # Deshabilitar la acción
        # Agregar las opciones de menú al menú parse
        parseMenu.addAction(parsearGramaticaLL1Action)
        parseMenu.addAction(self.mostrarTableLL1Action)


    def pestania_simular(self):
        simularMenu = QMenu("Simular", self)
        self.menubar.addMenu(simularMenu)

        # Opciones de menú al menú simulacion
        self.parsearLL1Action = QAction("Analizar entrada LL(1)", self)
        self.parsearLL1Action.triggered.connect(self.parsear_entrada_LL1)
        self.parsearLL1Action.setEnabled(False)  # Deshabilitar la acción

        self.parsearEntradaAction = QAction("Analizar entrada", self)
        self.parsearEntradaAction.triggered.connect(self.parsear_entrada)
        self.parsearEntradaAction.setEnabled(False)  # Deshabilitar la acción

        # Agregar las opciones de menú al menú simulacion
        simularMenu.addAction(self.parsearLL1Action)
        simularMenu.addSeparator()
        simularMenu.addAction(self.parsearEntradaAction)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Anagra")
        self.setGeometry(200, 200, 800, 600)

        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)

        self.pestania_gramatica()
        self.pestania_editar()
        self.pestania_buscar()
        self.pestania_texto()
        self.pestania_ayuda()

        self.textEdit = QPlainTextEdit(self)
        self.textEdit.cursorPositionChanged.connect(self.actualizar_linea_columna)
        self.setCentralWidget(self.textEdit)

        # Barra modo, linea y columna del cursor
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.modo_label = QLabel()
        self.linea_label = QLabel()
        self.columna_label = QLabel()

        self.statusBar.addWidget(self.modo_label)
        self.statusBar.addPermanentWidget(self.linea_label)
        self.statusBar.addPermanentWidget(self.columna_label)

        if len(sys.argv) > 1 and sys.argv[1] == "-f":
            self.menu_gramaticas()
            fichero = open(sys.argv[2]).read()
            gramatica = yacc.parse(fichero)
            self.token_inicial = gramatica[0]
            self.tokens_terminales = gramatica[1]
            self.tokens_no_terminales = gramatica[2]
            self.producciones = gramatica[3]

            self.textEdit.setPlainText(fichero)  # Escribimos el fichero
            self.textEdit.setReadOnly(True)      # Activamos modo lectura
            self.modo_label.setText(f"Modo: lectura")
            os.remove("ficheroANAGRA_temporal.txt")
        elif len(sys.argv) > 1 and sys.argv[1] == "-i":
            self.menu_gramaticas()
            gramatica = yacc.parse(sys.argv[2])
            self.token_inicial = gramatica[0]
            self.tokens_terminales = gramatica[1]
            self.tokens_no_terminales = gramatica[2]
            self.producciones = gramatica[3]

            self.textEdit.setPlainText(sys.argv[2])  # Escribimos el fichero
            self.textEdit.setReadOnly(True)  # Activamos modo lectura
            self.modo_label.setText(f"Modo: lectura")

        else:
            self.modo_label.setText(f"Modo: escritura")

        self.actualizar_linea_columna()

        self.token_inicial = ""
        self.tokens_terminales = set()
        self.tokens_no_terminales = set()
        self.producciones = dict()
        self.tabla = dict()

    def actualizar_linea_columna(self):
        cursor = self.textEdit.textCursor()
        linea = cursor.blockNumber() + 1
        columna = cursor.columnNumber() + 1
        self.linea_label.setText(f"Línea: {linea}")
        self.columna_label.setText(f"Columna: {columna}")

    def abrir_nueva_aplicacion(self):       # TODO COMPROBAR QUE FUNCIONA EN WINDOWS
        python_path = sys.executable
        os.system(python_path + " " + os.path.abspath(__file__) + " &")

    def abrir_nueva_aplicacion_texto(self, texto):       # TODO COMPROBAR QUE FUNCIONA EN WINDOWS
        fichero = open("ficheroANAGRA_temporal.txt", "w")
        fichero.write(texto)
        fichero.close()
        python_path = sys.executable
        os.system(python_path + " " + os.path.abspath(__file__) + " -f ficheroANAGRA_temporal.txt &")
        print("hola")

    def abrir_nueva_aplicacion_input(self, texto):       # TODO COMPROBAR QUE FUNCIONA EN WINDOWS
        python_path = sys.executable
        os.system(python_path + " " + os.path.abspath(__file__) + " -f ficheroANAGRA_temporal.txt " + texto + "&")
        print("hola")

    def abrir_fichero(self):
        dialogo = QFileDialog(self, "Abrir archivo")
        dialogo.setFileMode(QFileDialog.ExistingFile)

        if dialogo.exec_() == QFileDialog.Accepted:
            self.menu_gramaticas()
            # Obtenemos la ruta del archivo
            ruta_archivo = dialogo.selectedFiles()[0]
            fichero = open(ruta_archivo).read()
            gramatica = yacc.parse(fichero)
            self.token_inicial = gramatica[0]
            self.tokens_terminales = gramatica[1]
            self.tokens_no_terminales = gramatica[2]
            self.producciones = gramatica[3]

            self.textEdit.setPlainText(fichero)  # Escribimos el fichero
            self.textEdit.setReadOnly(True)      # Activamos modo lectura
            self.modo_label.setText(f"Modo: lectura")


    def guardar(self):
        print()

    def guardar_como(self):
        nombFich = QFileDialog.getSaveFileName(self, 'Guardar fichero')[0]
        fichero = open(nombFich, 'w')
        texto = self.textEdit.toPlainText()
        fichero.write(texto)
        fichero.close()

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

    def aceptar_gramatica(self):
        self.menu_gramaticas()

        texto = self.textEdit.toPlainText()
        gramatica = yacc.parse(texto)
        self.token_inicial = gramatica[0]
        self.tokens_terminales = gramatica[1]
        self.tokens_no_terminales = gramatica[2]
        self.producciones = gramatica[3]

        self.textEdit.setReadOnly(True)     # Activamos modo lectura
        self.modo_label.setText(f"Modo: lectura")

    def rechazar_gramatica(self):
        print()

    def cortar(self):
        portapapeles = qApp.clipboard()
        texto = self.textEdit.textCursor().selectedText()  # Obtenemos el texto seleccionado
        portapapeles.setText(texto)                        # Lo guardamos en el portapapeles
        self.textEdit.textCursor().removeSelectedText()    # Borramos el texto seleccionado

    def copiar(self):
        portapapeles = qApp.clipboard()
        texto = self.textEdit.textCursor().selectedText()  # Obtenemos el texto seleccionado
        portapapeles.setText(texto)                        # Lo guardamos en el portapapeles

    def pegar(self):
        portapapeles = qApp.clipboard()
        texto = portapapeles.text(QClipboard.Clipboard)     # Obtenemos el texto del portapapeles
        self.textEdit.textCursor().insertText(texto)        # Lo pegamos

    def borrar(self):
        self.textEdit.textCursor().removeSelectedText()    # Borramos el texto seleccionado

    def seleccionar_todo(self):
        cursor = self.textEdit.textCursor()
        cursor.select(QTextCursor.Document)
        self.textEdit.setTextCursor(cursor)

    def buscar(self):
        print()

    def reemplazar(self):
        print()

    def buscar_de_nuevo(self):
        print()

    def ir_a_linea(self):
        print()

    def mostrar_informacion(self):
        msgBox = QMessageBox()
        msgBox.setText("Realizado por: Laura González Pizarro")
        msgBox.setText("Dirigido por: Joaquín Ezpeleta Mateo")
        msgBox.exec()

    def cambiar_fuente(self):
        print()

    def cambiar_color(self):
        print()

    def cambiar_tab(self):
        print()

    def cambiar_idioma(self):
        # Mostramos una ventana de mensaje con un pequeño texto
        QMessageBox.information(self, "Cambio idioma", "Los cambios se realizaran la siguiente vez que se inicie Anagra")

    def calcular_conjunto_primero(self):
        primero = conj.conjunto_primero(self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        nueva_ventana = conj_tab.ConjuntoPrimero(primero, self)
        nueva_ventana.show()

    def calcular_conjunto_siguiente(self): # TODO POONER LA FECHA PARA QUE NO HAYA POSIBLES CONFLICTOS
        siguiente = conj.conjunto_siguiente(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        nueva_ventana = conj_tab.ConjuntoSiguiente(siguiente, self)
        nueva_ventana.show()

    def calcular_conjunto_primero_frase(self):
        self.tabla = conj.construccion_tabla(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        tabla = {index: elemento for index, elemento in enumerate(self.tabla)}
        nueva_ventana = conj_tab.TablaSimulacion(tabla, self)
        nueva_ventana.show()

    def transformacion_factorizacion_izquierda(self):
        self.tokens_no_terminales, self.producciones = ot.factorizacion_izquierda(self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()

    def transformacion_no_derivables(self):
        self.tokens_no_terminales, self.producciones = ot.eliminacion_simolos_no_termibales(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()
        ot.gramatica_no_vacia(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)

    def transformacion_recursividad_izquierda(self):
        self.tokens_no_terminales, self.producciones, _ = ot.eliminar_recursividad_izquierda(self.token_inicial, self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()

    def transformacion_no_alcanzables(self):
        self.tokens_terminales, self.tokens_no_terminales,  self.producciones = ot.eliminacion_simbolos_inutiles(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()

    def transformacion_producciones_epsilon(self):
        self.producciones = ot.eliminacion_producciones_epsilon(self.token_inicial, self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()

    def transformacion_eliminacion_ciclos(self):
        self.producciones = ot.eliminacion_producciones_unitarias(self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()

    def forma_normal_chomsky(self):
        self.producciones = ot.forma_normal_chomsky(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()

    def forma_normal_greibach(self):
        self.tokens_no_terminales, self.producciones = ot.forma_normal_greibach(self.token_inicial, self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()
        self.abrir_nueva_aplicacion_texto()

    def parsear_gramatica_LL1(self):
        self.tabla = conj.construccion_tabla(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales,
                                             self.producciones)

        self.parsearLL1Action.setEnabled(True)      # Habilitar la acción
        self.parsearEntradaAction.setEnabled(True)  # Habilitar la acción
        self.mostrarTableLL1Action.setEnabled(True) # Habilitar la acción

        nueva_ventana = conj_tab.TablaAnalisis(self.tabla, self)
        nueva_ventana.show()

    def mostrar_tabla_LL1(self):
        nueva_ventana = conj_tab.TablaAnalisis(self.tabla, self)
        nueva_ventana.show()

    def parsear_entrada_LL1(self):
        nueva_ventana = VentanaInputGramatica(self)
        nueva_ventana.show()

    def parsear_entrada(self):
        nueva_ventana = VentanaInput(self)
        nueva_ventana.show()

    def mostrar_gramatica(self):
        texto = f"%start {self.token_inicial}\n%%\n\n"
        for token, producciones_token in self.producciones.items():
            texto += token + ": "
            espacios = " " * (len(token) + 2)
            for indice, produccion in enumerate(producciones_token):
                if produccion is not None:
                    for token_produccion in produccion:
                        texto += token_produccion + "  "
                if indice != len(self.producciones[token]) - 1:
                    texto += "\n" + espacios + "| "
            texto += "\n;\n\n"
        texto += "%%"
        self.textEdit.setPlainText(texto)

    def mostrar_gramatica_compacta(self):
        texto = f"%start {self.token_inicial}\n%%\n"
        for token, producciones_token in self.producciones.items():
            texto += token + ": "
            for indice, produccion in enumerate(producciones_token):
                if produccion is not None:
                    for token_produccion in produccion:
                        texto += token_produccion + "  "
                if indice != len(self.producciones[token]) - 1:
                    texto += "| "
            texto += ";\n"
        texto += "%%"
        self.textEdit.setPlainText(texto)

    def escribir_gramatica(self, token_inicial, producciones):
        texto = f"%start {token_inicial}\n%%\n\n"
        for token, producciones_token in producciones.items():
            texto += token + ": "
            espacios = " " * (len(token) + 2)
            for indice, produccion in enumerate(producciones_token):
                if produccion is not None:
                    for token_produccion in produccion:
                        texto += token_produccion + "  "
                if indice != len(producciones[token]) - 1:
                    texto += "\n" + espacios + "| "
            texto += "\n;\n\n"
        texto += "%%"
        return texto



if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    app.exec_()
    sys.exit()
