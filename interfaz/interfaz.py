import os
import sys

from PyQt5.QtGui import QKeySequence, QClipboard, QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QCheckBox, QWidgetAction, \
    QPlainTextEdit, QMessageBox, QFileDialog, QStatusBar, QLabel, qApp

import bisonlex
import bisonparse
from ply import *

import operacionesTransformacion as ot
import conjuntos
class NewApplication:
    def __init__(self):
        super().__init__(sys.argv)


class MainWindow(QMainWindow):

    def pestania_gramatica(self):
        gramaticaMenu = QMenu("Gramática", self)
        self.menubar.addMenu(gramaticaMenu)

        # Opciones de menú al menú gramatica

        nuevoAction = QAction("Nuevo", self)
        nuevoAction.setShortcut(QKeySequence.New)
        nuevoAction.triggered.connect(self.abrir_nueva_aplicacion)

        abrirAction = QAction("Abrir", self)
        abrirAction.setShortcut(QKeySequence.Open)
        abrirAction.triggered.connect(self.abrir_fichero)

        editarAction = QAction("Editar", self)
        # editarAction.setShortcut(QKeySequence.) TODO NO EXISTE EDITAR
        editarAction.setEnabled(False)  # Deshabilitar la acción

        cerrarAction = QAction("Cerrar", self)
        cerrarAction.setShortcut(QKeySequence.Close)

        guardarAction = QAction("Guardar", self)
        guardarAction.setShortcut(QKeySequence.Save)
        guardarAction.setEnabled(False)  # Deshabilitar la acción

        guardarComoAction = QAction("Guardar como...", self)
        guardarComoAction.setShortcut(QKeySequence.SaveAs)
        guardarComoAction.triggered.connect(self.guardar_como)


        salirAction = QAction("Salir", self)
        salirAction.setShortcut(QKeySequence.Quit)

        # Agregar las opciones de menú al menú grmática
        gramaticaMenu.addAction(nuevoAction)
        gramaticaMenu.addAction(abrirAction)
        gramaticaMenu.addAction(editarAction)
        gramaticaMenu.addAction(cerrarAction)
        gramaticaMenu.addAction(guardarAction)
        gramaticaMenu.addAction(guardarComoAction)
        gramaticaMenu.addSeparator()  # Línea de separación
        gramaticaMenu.addAction(salirAction)
    def pestania_editar(self):
        editarMenu = QMenu("Editar", self)
        self.menubar.addMenu(editarMenu)

        # Opciones de menú al menú editar
        cortarAction = QAction("Cortar", self)
        cortarAction.setShortcut(QKeySequence.Cut)
        cortarAction.triggered.connect(self.cortar)

        copiarAction = QAction("Copiar", self)
        copiarAction.setShortcut(QKeySequence.Copy)
        copiarAction.triggered.connect(self.copiar)

        pegarAction = QAction("Pegar", self)
        pegarAction.setShortcut(QKeySequence.Paste)
        pegarAction.triggered.connect(self.pegar)

        borrarAction = QAction("Borrar", self)

        seleccionarTodoAction = QAction("Seleccionar todo", self)
        seleccionarTodoAction.setShortcut(QKeySequence.SelectAll)
        seleccionarTodoAction.triggered.connect(self.seleccionar_todo)

        aceptarGramaticaAction = QAction("Aceptar gramática", self)
        aceptarGramaticaAction.triggered.connect(self.aceptar_gramatica)

        rechazarGramaticaAction = QAction("Rechazar gramática", self)
        rechazarGramaticaAction.setEnabled(False)  # Deshabilitar la acción

        # Agregar las opciones de menú al menú editar
        editarMenu.addAction(cortarAction)
        editarMenu.addAction(copiarAction)
        editarMenu.addAction(pegarAction)
        editarMenu.addAction(borrarAction)
        editarMenu.addAction(seleccionarTodoAction)
        editarMenu.addSeparator()  # Línea de separación
        editarMenu.addAction(aceptarGramaticaAction)
        editarMenu.addAction(rechazarGramaticaAction)

    def pestania_buscar(self):
        buscarMenu = QMenu("Buscar", self)
        self.menubar.addMenu(buscarMenu)

        # Opciones de menú al menú buscar
        buscarAction = QAction("Buscar", self)
        buscarAction.setShortcut(QKeySequence.Find)
        reemplazarAction = QAction("Reemplazar", self)
        reemplazarAction.setShortcut(QKeySequence.Replace)
        buscarDeNuevoAction = QAction("Buscar de nuevo", self)
        buscarDeNuevoAction.setEnabled(False)  # Deshabilitar la acción
        # buscarDeNuevoAction.setShortcut(QKeySequence.FindNext)  TODO NO SE CUAL ES, SHIFT+B NO ES NADA
        irALineaAction = QAction("Ir a linea...", self)

        # Agregar las opciones de menú al menú buscar
        buscarMenu.addAction(buscarAction)
        buscarMenu.addAction(reemplazarAction)
        buscarMenu.addAction(buscarDeNuevoAction)
        buscarMenu.addSeparator()  # Línea de separación
        buscarMenu.addAction(irALineaAction)

    def pestania_texto(self):
        textMenu = QMenu("Texto", self)
        self.menubar.addMenu(textMenu)

        # Opciones de menú al menú text
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
        textMenu.addMenu(idiomaSubmenu)
        textMenu.addAction(guardarPreferenciasAction)

    def pestania_ayuda(self):
        ayudaMenu = QMenu("Ayuda", self)
        self.menubar.addMenu(ayudaMenu)

        # Opciones de menú al menú ayuda
        sobreAction = QAction("Sobre...", self)
        sobreAction.triggered.connect(self.mostrar_informacion)

        # Agregar las opciones de menú al menú ayuda
        ayudaMenu.addAction(sobreAction)

    def pestania_herramientas(self):
        herramientasMenu = QMenu("Herramientas", self)
        self.menubar.addMenu(herramientasMenu)

        # Opciones de menú al menú herramientas
        conjuntoPrimeroAction = QAction("Calcular conjunto PRIMERO", self)
        conjuntoPrimeroAction.triggered.connect(self.calcular_conjunto_primero)

        conjuntoSiguierneAction = QAction("Calcular conjunto PRIMERO", self)
        conjuntoSiguierneAction.triggered.connect(self.calcular_conjunto_siguiente)

        conjuntoPrimeroFraseAction = QAction("Calcular conjunto PRIMERO de forma frase", self)
        conjuntoPrimeroFraseAction.triggered.connect(self.calcular_conjunto_primero_frase)


        # Agregar las opciones de menú al menú herramientas
        herramientasMenu.addAction(conjuntoPrimeroAction)
        herramientasMenu.addAction(conjuntoSiguierneAction)
        herramientasMenu.addAction(conjuntoPrimeroFraseAction)

    def pestania_transformaciones(self):
        transformacionesMenu = QMenu("Transformaciones", self)
        self.menubar.addMenu(transformacionesMenu)

        # Opciones de menú al menú transformaciones
        factorizacionIzquierdaAction = QAction("Factorización a izquierda", self)
        factorizacionIzquierdaAction.triggered.connect(self.transformacion_factorizacion_izquierda)

        eliminacionNoDerivablesAction = QAction("Eliminación de no terminales no derivables", self)
        eliminacionNoDerivablesAction.triggered.connect(self.transformacion_no_derivables)

        eliminacionRecursividadIzqAction = QAction("Eliminación de recursividad a izquierda", self)
        eliminacionRecursividadIzqAction.triggered.connect(self.transformacion_recursividad_izquierda)

        eliminacionNoAlcanzablesAction = QAction("Eliminación de símbolos no alcanzables", self)
        eliminacionNoAlcanzablesAction.triggered.connect(self.transformacion_no_alcanzables)

        eliminacionProduccionesEpsAction = QAction("Eliminación de producciones epsilon", self)
        eliminacionProduccionesEpsAction.triggered.connect(self.transformacion_producciones_epsilon)

        eliminacionCiclosAction = QAction("Eliminación de ciclos", self)
        eliminacionCiclosAction.triggered.connect(self.transformacion_eliminacion_ciclos)

        # Agregar las opciones de menú al menú transformaciones
        transformacionesMenu.addAction(factorizacionIzquierdaAction)
        transformacionesMenu.addAction(eliminacionNoDerivablesAction)
        transformacionesMenu.addAction(eliminacionRecursividadIzqAction)
        transformacionesMenu.addAction(eliminacionNoAlcanzablesAction)
        transformacionesMenu.addAction(eliminacionProduccionesEpsAction)
        transformacionesMenu.addAction(eliminacionCiclosAction)

    def pestania_parse(self):
        parseMenu = QMenu("Parse", self)
        self.menubar.addMenu(parseMenu)

        # Opciones de menú al menú parse
        parsearGramaticaLL1Action = QAction("Analizar gramática LL(1)", self)
        parsearTableLL1Action = QAction("Parsear tabla LL(1)", self)

        # Agregar las opciones de menú al menú parse
        parseMenu.addAction(parsearGramaticaLL1Action)
        parseMenu.addAction(parsearTableLL1Action)

    def pestania_simular(self):
        simularMenu = QMenu("Simular", self)
        self.menubar.addMenu(simularMenu)

        # Opciones de menú al menú simulacion
        parsearLL1Action = QAction("Analizar entrada LL(1)", self)
        parsearEntradaAction = QAction("Parsear entrada", self)

        # Agregar las opciones de menú al menú simulacion
        simularMenu.addAction(parsearLL1Action)
        simularMenu.addSeparator()
        simularMenu.addAction(parsearEntradaAction)

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

        # Barra modo
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.modo_label = QLabel()
        self.linea_label = QLabel()
        self.columna_label = QLabel()

        self.statusBar.addWidget(self.modo_label)
        self.statusBar.addPermanentWidget(self.linea_label)
        self.statusBar.addPermanentWidget(self.columna_label)

        self.modo_label.setText(f"Modo: escritura")

        self.actualizar_linea_columna()

        self.token_inicial = ""
        self.tokens_terminales = set()
        self.tokens_no_terminales = set()
        self.producciones = dict()

    def actualizar_linea_columna(self):
        cursor = self.textEdit.textCursor()
        linea = cursor.blockNumber() + 1
        columna = cursor.columnNumber() + 1
        self.linea_label.setText(f"Línea: {linea}")
        self.columna_label.setText(f"Columna: {columna}")

    def abrir_nueva_aplicacion(self):       # TODO COMPROBAR QUE FUNCIONA EN WINDOWS
        python_path = sys.executable
        os.system(python_path + " " + os.path.abspath(__file__))

    def abrir_fichero(self):
        dialogo = QFileDialog(self, "Abrir archivo")
        dialogo.setFileMode(QFileDialog.ExistingFile)

        # Mostrar el diálogo para que el usuario seleccione un archivo
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
        self.pestania_gramatica()
        self.pestania_buscar()
        self.pestania_texto()

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

    def cambiar_idioma(self):
        # Mostramos una ventana de mensaje con un pequeño texto
        QMessageBox.information(self, "Cambio idioma", "Los cambios se realizaran la siguiente vez que se inicie Anagra")

    def calcular_conjunto_primero(self):
        primero = conjuntos.conjunto_primero(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        print()

    def calcular_conjunto_siguiente(self):
        siguiente = conjuntos.conjunto_siguiente(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        print()

    def calcular_conjunto_primero_frase(self):
        print()

    def transformacion_factorizacion_izquierda(self):
        self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones = ot.factorizacion_a_izquierda(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()

    def transformacion_no_derivables(self):
        self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones = ot.eliminacion_no_terminales(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()

    def transformacion_recursividad_izquierda(self):
        self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones = ot.eliminar_recursividad_izquierda(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()

    def transformacion_no_alcanzables(self):
        self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones = ot.eliminacion_no_accesibles(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()

    def transformacion_producciones_epsilon(self):
        (self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones) = ot.eliminacion_producciones_epsilon(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()
    def transformacion_eliminacion_ciclos(self):
        self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones = ot.eliminacion_ciclos(self.token_inicial, self.tokens_terminales, self.tokens_no_terminales, self.producciones)
        self.mostrar_gramatica()

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec_())
