# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause


import math
import sys

from PyQt5.QtCore import (QEasingCurve, QLineF,
                            QParallelAnimationGroup, QPointF,
                            QPropertyAnimation, QRectF, Qt)
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF, QFont, QPalette
from PyQt5.QtWidgets import (QApplication, QComboBox, QGraphicsItem,
                             QGraphicsObject, QGraphicsScene, QGraphicsView,
                             QStyleOptionGraphicsItem, QVBoxLayout, QWidget, QMainWindow, QDesktopWidget, QMessageBox)

import networkx as nx



class Node(QGraphicsObject):

    """A QGraphicsItem representing node in a graph"""

    def __init__(self, name: str, parent=None):
        """Node constructor

        Args:
            name (str): Node label
        """
        super().__init__(parent)
        self._name = name
        self._edges = []
        self._color = "#00afb9"
        self._radius = 30
        self._rect = QRectF(0, 0, self._radius * 2, self._radius * 2)

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self.setAcceptHoverEvents(True)

    # def hoverEnterEvent(self, event):
    #    self.setCursor(Qt.PointingHandCursor)

    # def hoverLeaveEvent(self, event):
    #    self.setCursor(Qt.ArrowCursor)

    # def mousePressEvent(self, event):
    #    if event.button() == Qt.LeftButton:
    #        self.show_message_box()

    def show_message_box(self): # TODO CAMBIAR A UNA VENTANA QUE TENGA LA INFO PARA QUE SEA ASINCRONO :)
        msg_box = QMessageBox()
        msg_box.setWindowTitle(f"Node Label: {self._name}")
        msg_box.setText("hola")
        msg_box.exec_()

    def boundingRect(self) -> QRectF:
        """Override from QGraphicsItem

        Returns:
            QRect: Return node bounding rect
        """
        return self._rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        """Override from QGraphicsItem

        Draw node

        Args:
            painter (QPainter)
            option (QStyleOptionGraphicsItem)
        """
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(
            QPen(
                QColor(self._color).darker(),
                2,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin,
            )
        )
        painter.setBrush(QBrush(QColor(self._color)))
        painter.drawEllipse(self.boundingRect())
        painter.setPen(QPen(QColor("white")))
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self._name)

    def add_edge(self, edge):
        """Add an edge to this node

        Args:
            edge (Edge)
        """
        self._edges.append(edge)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        """Override from QGraphicsItem

        Args:
            change (QGraphicsItem.GraphicsItemChange)
            value (Any)

        Returns:
            Any
        """
        if change == QGraphicsItem.ItemPositionHasChanged:
            for edge in self._edges:
                edge.adjust()

        return super().itemChange(change, value)


class Edge(QGraphicsItem):
    def __init__(self, source: Node, dest: Node, label = "", parent: QGraphicsItem = None):
        """Edge constructor

        Args:
            source (Node): source node
            dest (Node): destination node
        """
        super().__init__(parent)
        self._source = source
        self._dest = dest
        self._label = label

        self._tickness = 2
        self._color = QColor("#00afb9").darker()
        self._arrow_size = 10

        self._source.add_edge(self)
        self._dest.add_edge(self)

        self._line = QLineF()
        self.setZValue(-1)
        self.adjust()

    def boundingRect(self) -> QRectF:
        """Override from QGraphicsItem

        Returns:
            QRect: Return node bounding rect
        """
        return (
            QRectF(self._line.p1(), self._line.p2())
            .normalized()
            .adjusted(
                -self._tickness - self._arrow_size,
                -self._tickness - self._arrow_size,
                self._tickness + self._arrow_size,
                self._tickness + self._arrow_size,
            )
        )

    def adjust(self):
        """
        Update edge position from source and destination node.
        This method is called from Node::itemChange
        """
        self.prepareGeometryChange()
        self._line = QLineF(
            self._source.pos() + self._source.boundingRect().center(),
            self._dest.pos() + self._dest.boundingRect().center(),
        )

    def _draw_arrow(self, painter: QPainter, start: QPointF, end: QPointF):
        """Draw arrow from start point to end point.

        Args:
            painter (QPainter)
            start (QPointF): start position
            end (QPointF): end position
        """
        painter.setBrush(QBrush(QColor(self._color)))

        line = QLineF(end, start)

        angle = math.atan2(-line.dy(), line.dx())
        arrow_p1 = line.p1() + QPointF(
            math.sin(angle + math.pi / 3) * self._arrow_size,
            math.cos(angle + math.pi / 3) * self._arrow_size,
        )
        arrow_p2 = line.p1() + QPointF(
            math.sin(angle + math.pi - math.pi / 3) * self._arrow_size,
            math.cos(angle + math.pi - math.pi / 3) * self._arrow_size,
        )

        arrow_head = QPolygonF()
        arrow_head.clear()
        arrow_head.append(line.p1())
        arrow_head.append(arrow_p1)
        arrow_head.append(arrow_p2)
        painter.drawLine(line)
        painter.drawPolygon(arrow_head)

    def _arrow_target(self) -> QPointF:
        """Calculate the position of the arrow taking into account the size of the destination node

        Returns:
            QPointF
        """
        target = self._line.p1()
        center = self._line.p2()
        radius = self._dest._radius
        vector = target - center
        length = math.sqrt(vector.x() ** 2 + vector.y() ** 2)
        if length == 0:
            return target
        normal = vector / length
        target = QPointF(center.x() + (normal.x() * radius), center.y() + (normal.y() * radius))

        return target

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget=None):
        """Override from QGraphicsItem

        Draw Edge. This method is called from Edge.adjust()

        Args:
            painter (QPainter)
            option (QStyleOptionGraphicsItem)
        """

        if self._source and self._dest:
            painter.setRenderHints(QPainter.Antialiasing)

            painter.setPen(
                QPen(
                    QColor(self._color),
                    self._tickness,
                    Qt.SolidLine,
                    Qt.RoundCap,
                    Qt.RoundJoin,
                )
            )
            painter.drawLine(self._line)
            self._draw_arrow(painter, self._line.p1(), self._arrow_target())

            if self._label:
                middle_point = QPointF(
                    (self._line.p1().x() + self._line.p2().x()) / 2,
                    (self._line.p1().y() + self._line.p2().y()) / 2
                )

                painter.setPen(QPen(QColor("#9c9c9c")))
                painter.setFont(QFont(painter.font().family(), 15)) # TODO, cambiamo el tamaño de letra?
                painter.drawText(middle_point, self._label)

            self._arrow_target()


class GraphView(QGraphicsView):
    def __init__(self, graph: nx.DiGraph, edges, parent=None):
        """GraphView constructor

        This widget can display a directed graph

        Args:
            graph (nx.DiGraph): a networkx directed graph
        """
        super().__init__()
        self._graph = graph
        self._edges = edges
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        # Used to add space between nodes
        self._graph_scale = 250

        # Map node name to Node object {str=>Node}
        self._nodes_map = {}

        # List of networkx layout function
        self._nx_layout = nx.kamada_kawai_layout # TODO preguntar si le gusta mas este o circular_layout
        self._load_graph()
        self.set_nx_layout()
        # self._nx_layout = {
        #    "circular": nx.circular_layout,
        #    "planar": nx.planar_layout,
        #    "random": nx.random_layout,
        #    "shell_layout": nx.shell_layout,
        #    "kamada_kawai_layout": nx.kamada_kawai_layout,
        #    "spring_layout": nx.spring_layout,
        #    "spiral_layout": nx.spiral_layout,
        #}

    def set_nx_layout(self):
        """Set networkx layout and start animation

        Args:
            name (str): Layout name
        """

        # Compute node position from layout function
        positions = self._nx_layout(self._graph)

        # Change position of all nodes using an animation
        self.animations = QParallelAnimationGroup()
        for node, pos in positions.items():
            x, y = pos
            x *= self._graph_scale
            y *= self._graph_scale
            item = self._nodes_map[node]

            animation = QPropertyAnimation(item, b"pos")
            animation.setDuration(1000)
            animation.setEndValue(QPointF(x, y))
            animation.setEasingCurve(QEasingCurve.OutExpo)
            self.animations.addAnimation(animation)

        self.animations.start()


    def _load_graph(self):
        """Load graph into QGraphicsScene using Node class and Edge class"""

        self.scene().clear()
        self._nodes_map.clear()

        # Add nodes
        for node in self._graph:
            item = Node(node)
            self.scene().addItem(item)
            self._nodes_map[node] = item

        # Add edges
        for a, b in self._graph.edges:
            source = self._nodes_map[a]
            dest = self._nodes_map[b]
            label = self._edges[a, b]
            self.scene().addItem(Edge(source, dest, label))


class AutomatonWindow(QMainWindow):
    def __init__(self, edges, parent=None):
        super().__init__(parent)
        self.edges = edges
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Automata gramática')
        self.setGeometry(0, 0, 650, 550)

        self.graph = nx.DiGraph()
        self.graph.add_edges_from(list(self.edges.keys()))

        self.view = GraphView(self.graph, self.edges, self)
        self.setCentralWidget(self.view)

        screen = QDesktopWidget().availableGeometry()   # TODO VER DONDE LO PONGO
        window_size = self.frameGeometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)



if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Create a networkx graph

    widget = AutomatonWindow({('0', '2'): 'T', ('0', '3'): "'('", ('0', '1'): 'E', ('0', '4'): 'id', ('1', '5'): "'+'", ('3', '2'): 'T', ('3', '3'): "'('", ('3', '6'): 'E', ('3', '4'): 'id', ('5', '7'): 'T', ('5', '3'): "'('", ('5', '4'): 'id', ('6', '5'): "'+'", ('6', '8'): "')'"})
    widget.show()
    sys.exit(app.exec())