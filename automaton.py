"""
Filename:
Author: Laura González Pizarro
Description: Adapted form
"""
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause


import math

from PyQt5.QtCore import (QEasingCurve, QLineF,
                          QParallelAnimationGroup, QPointF,
                          QPropertyAnimation, QRectF, Qt)
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF, QFont
from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsObject, QGraphicsScene, QGraphicsView,
                             QStyleOptionGraphicsItem, QWidget, QMainWindow, QDesktopWidget, QPlainTextEdit)

import networkx as nx


class NodeText(QMainWindow):
    def __init__(self, name, text, parent=None):
        super().__init__(parent)
        self._name = name
        self._text = text
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self._name)
        self.setGeometry(0, 0, 200, 120)

        # Center window to the middle of the screen
        screen = QDesktopWidget().availableGeometry()
        window_size = self.frameGeometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

        self.text_edit = QPlainTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(self._text)


class Node(QGraphicsObject):

    """A QGraphicsItem representing node in a graph"""

    def __init__(self, name: str, content, window, parent=None):
        """Node constructor

        Args:
            name (str): Node label
        """
        super().__init__(parent)
        self._name = name
        self._content = content
        self._window = window
        self._edges = []
        self._color = "#00afb9"
        self._radius = 30
        self._rect = QRectF(0, 0, self._radius * 2, self._radius * 2)

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

        self.setAcceptHoverEvents(True)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.show_message_box()

    def show_message_box(self):
        text = ""
        if len(self._content[0]) == 2:
            for token, prod in self._content:
                text += "{} → {}".format(token, " ".join(str(x) for x in prod)) + "\n"
        else:
            for token, prod, terminal in self._content:
                text += "{} → {}".format(token, " ".join(str(x) for x in prod)) + " ," + str(terminal) + "\n"
        node_text_window = NodeText(f"Node Label: {self._name}", text, self._window)
        node_text_window.show()



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
    def __init__(self, source: Node, dest: Node, label, double_arrow=False, parent: QGraphicsItem = None):
        """Edge constructor

        Args:
            source (Node): source node
            dest (Node): destination node
        """
        super().__init__(parent)
        self._source = source
        self._dest = dest
        self._label = label
        self.double_arrow = double_arrow

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

        if self._label:
            if self.double_arrow:
                label_point = QPointF(
                    (2 * self._line.p1().x() + self._line.p2().x()) / 3,
                    (2 * self._line.p1().y() + self._line.p2().y()) / 3
                )
            else:
                label_point = QPointF(
                    (self._line.p1().x() + self._line.p2().x()) / 2,
                    (self._line.p1().y() + self._line.p2().y()) / 2
                )

            painter.setPen(QPen(QColor("#9c9c9c")))
            painter.setFont(QFont(painter.font().family(), 15))
            painter.drawText(label_point, self._label)


    def _draw_self_arrow(self, painter: QPainter):
        """Draw arrow arc to itself

        Args:
            painter (QPainter)
        """
        painter.setBrush(QBrush(QColor(self._color)))

        rect = QRectF(self._line.p1().x() - 60, self._line.p1().y() - 10, 60, 60)
        painter.drawArc(rect, 19 * -220, 17 * 225)

        angle = math.pi
        dest_arrow_p1 = (rect.topLeft() + rect.topRight())/2 - QPointF(
            math.sin(angle - math.pi / 3) * self._arrow_size,
            math.cos(angle - math.pi / 3) * self._arrow_size - 2,
        )

        dest_arrow_p2 = (rect.topLeft() + rect.topRight())/2 - QPointF(
            math.sin(angle - math.pi + math.pi / 3) * self._arrow_size,
            math.cos(angle - math.pi + math.pi / 3) * self._arrow_size - 2,
        )

        arrow_head = QPolygonF()
        arrow_head.clear()
        arrow_head.append(dest_arrow_p1)
        arrow_head.append(dest_arrow_p2)
        arrow_head.append((rect.topLeft() + rect.topRight())/2 + QPointF(0, 2))
        painter.drawPolygon(arrow_head)

        if self._label:
            label_point = (rect.topLeft() + rect.bottomLeft()) / 2 + QPointF(-20, 0) # Position to write text
            painter.setPen(QPen(QColor("#9c9c9c")))
            painter.setFont(QFont(painter.font().family(), 15))
            painter.drawText(label_point, self._label)


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

            if self._source != self._dest:
                self._draw_arrow(painter, self._line.p1(), self._arrow_target())
            else:
                self._draw_self_arrow(painter)


class GraphView(QGraphicsView):
    def __init__(self, graph: nx.DiGraph, nodes, edges, window, parent=None):
        """GraphView constructor

        This widget can display a directed graph

        Args:
            graph (nx.DiGraph): a networkx directed graph
        """
        super().__init__(parent)
        self._graph = graph
        self._nodes = nodes
        self._edges = edges
        self._window = window
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        # Used to add space between nodes
        self._graph_scale = 250

        # Map node name to Node object {str=>Node}
        self._nodes_map = {}

        # List of networkx layout function
        self._nx_layout = nx.kamada_kawai_layout
        self._load_graph()
        self.set_nx_layout()

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
            item = Node(node, self._nodes[int(node)], self._window)
            self.scene().addItem(item)
            self._nodes_map[node] = item

        # Add edges
        for a, b in self._graph.edges:
            source = self._nodes_map[a]
            dest = self._nodes_map[b]
            label = self._edges[a, b]
            if (b, a) in self._graph.edges:
                self.scene().addItem(Edge(source, dest, label, True))
            else:
                self.scene().addItem(Edge(source, dest, label))

class AutomatonWindow(QMainWindow):
    def __init__(self, traductions, nodes, edges, window, type, parent=None):
        super().__init__(parent)
        self.traductions = traductions
        self.nodes = nodes
        self.edges = edges
        self._window = window
        self.type = type
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.traductions["tituloAutomataGramatica"] + self.type)
        self.setGeometry(0, 0, 650, 550)

        self.graph = nx.DiGraph()
        self.graph.add_edges_from(list(self.edges.keys()))

        self.view = GraphView(self.graph, self.nodes, self.edges, self._window, self)
        self.setCentralWidget(self.view)

        screen = QDesktopWidget().availableGeometry()   # TODO VER DONDE LO PONGO
        window_size = self.frameGeometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
