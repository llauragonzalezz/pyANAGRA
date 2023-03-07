import sys

from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QAction, QCheckBox, QWidgetAction, \
    QPlainTextEdit, QLabel, QHBoxLayout, QStatusBar, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Crear la barra de menú
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)


        # Crear los menús
        gramaticaMenu = QMenu("Gramática", self)
        editarMenu = QMenu("Editar", self)
        buscarMenu = QMenu("Buscar", self)
        textMenu = QMenu("Texto", self)
        ayudaMenu = QMenu("Ayuda", self)

        # Agregar los menús a la barra de menú
        menubar.addMenu(gramaticaMenu)
        menubar.addMenu(editarMenu)
        menubar.addMenu(buscarMenu)
        menubar.addMenu(textMenu)
        menubar.addMenu(ayudaMenu)

        # Opciones de menú al menú gramatica
        nuevoAction = QAction("Nuevo", self)
        nuevoAction.setShortcut(QKeySequence.New)
        abrirAction = QAction("Abrir", self)
        abrirAction.setShortcut(QKeySequence.Open)
        editarAction = QAction("Editar", self)
        #editarAction.setShortcut(QKeySequence.) TODO NO EXISTE EDITAR
        editarAction.setEnabled(False)  # Deshabilitar la acción
        cerrarAction = QAction("Cerrar", self)
        cerrarAction.setShortcut(QKeySequence.Close)
        guardarAction = QAction("Guardar", self)
        guardarAction.setShortcut(QKeySequence.Save)
        guardarAction.setEnabled(False)  # Deshabilitar la acción
        guardarComoAction = QAction("Guardar como...", self)
        guardarComoAction.setShortcut(QKeySequence.SaveAs)
        salirAction = QAction("Salir", self)
        salirAction.setShortcut(QKeySequence.Quit)

        # Opciones de menú al menú editar
        cortarAction = QAction("Cortar", self)
        cortarAction.setShortcut(QKeySequence.Cut)
        copiarAction = QAction("Copiar", self)
        copiarAction.setShortcut(QKeySequence.Copy)
        pegarAction = QAction("Pegar", self)
        pegarAction.setShortcut(QKeySequence.Paste)
        borrarAction = QAction("Borrar", self)
        seleccionarTodoAction = QAction("Seleccionar todo", self)
        seleccionarTodoAction.setShortcut(QKeySequence.SelectAll)
        aceptarGramaticaAction = QAction("Aceptar gramática", self)
        rechazarGramaticaAction = QAction("Rechazar gramática", self)
        rechazarGramaticaAction.setEnabled(False)  # Deshabilitar la acción

        # Opciones de menú al menú buscar
        buscarAction = QAction("Buscar", self)
        buscarAction.setShortcut(QKeySequence.Find)
        reemplazarAction = QAction("Reemplazar", self)
        reemplazarAction.setShortcut(QKeySequence.Replace)
        buscarDeNuevoAction = QAction("Buscar de nuevo", self)
        buscarDeNuevoAction.setEnabled(False)  # Deshabilitar la acción
        #buscarDeNuevoAction.setShortcut(QKeySequence.FindNext)  TODO NO SE CUAL ES, SHIFT+B NO ES NADA
        irALineaAction = QAction("Ir a linea...", self)

        # Opciones de menú al menú buscar
        idiomaSubmenu = QMenu("Idioma", self)

        idiomaEnglish = QCheckBox("English", self)
        widgetEnglish = QWidgetAction(self)
        widgetEnglish.setDefaultWidget(idiomaEnglish)

        idiomaCastellano = QCheckBox("Castellano", self)
        widgetCastellano = QWidgetAction(self)
        widgetCastellano.setDefaultWidget(idiomaCastellano)

        idiomaSubmenu.setContentsMargins(15, 0, 0, 0)
        idiomaSubmenu.addAction(widgetEnglish)
        idiomaSubmenu.addAction(widgetCastellano)
        guardarPreferenciasAction = QAction("Guardar preferencias", self)

        # Opciones de menú al menú ayuda
        sobreAction = QAction("Sobre...", self)

        # Agregar las opciones de menú al menú grmática
        gramaticaMenu.addAction(nuevoAction)
        gramaticaMenu.addAction(abrirAction)
        gramaticaMenu.addAction(editarAction)
        gramaticaMenu.addAction(cerrarAction)
        gramaticaMenu.addAction(guardarAction)
        gramaticaMenu.addAction(guardarComoAction)
        gramaticaMenu.addSeparator() # Línea de separación
        gramaticaMenu.addAction(salirAction)

        # Agregar las opciones de menú al menú editar
        editarMenu.addAction(cortarAction)
        editarMenu.addAction(copiarAction)
        editarMenu.addAction(pegarAction)
        editarMenu.addAction(borrarAction)
        editarMenu.addAction(seleccionarTodoAction)
        editarMenu.addSeparator() # Línea de separación
        editarMenu.addAction(aceptarGramaticaAction)
        editarMenu.addAction(rechazarGramaticaAction)

        # Agregar las opciones de menú al menú buscar
        buscarMenu.addAction(buscarAction)
        buscarMenu.addAction(reemplazarAction)
        buscarMenu.addAction(buscarDeNuevoAction)
        buscarMenu.addSeparator()  # Línea de separación
        buscarMenu.addAction(irALineaAction)

        # Agregar las opciones de menú al menú buscar
        textMenu.addMenu(idiomaSubmenu)
        textMenu.addAction(guardarPreferenciasAction)

        # Agregar las opciones de menú al menú ayuda
        ayudaMenu.addAction(sobreAction)

        # Agregar un área de edición en el centro de la ventana
        self.textEdit = QPlainTextEdit(self)
        self.setCentralWidget(self.textEdit)




if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MainWindow()
    ventana.show()
    sys.exit(app.exec_())
