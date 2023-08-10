# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause


import math
import sys
import simulacion as sim



from PyQt5.QtCore import (QEasingCurve, QLineF,
                            QParallelAnimationGroup, QPointF,
                            QPropertyAnimation, QRectF, Qt)

from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF, QPalette

from PyQt5.QtWidgets import (QApplication, QComboBox, QGraphicsItem,
                             QGraphicsObject, QGraphicsScene, QGraphicsView,
                             QStyleOptionGraphicsItem, QVBoxLayout, QWidget, QInputDialog, QPushButton, QMainWindow)

import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout



class Node(QGraphicsObject):

    """A QGraphicsItem representing node in a graph"""

    def __init__(self, name: str, terminal=False, parent=None):
        """Node constructor

        Args:
            name (str): Node label
        """
        super().__init__(parent)
        self._name = name
        self._edges = []
        if terminal:
            self._color = "#f07167"
        else:
            self._color = "#00afb9"
        self._radius = 30
        self._rect = QRectF(0, 0, self._radius * 2, self._radius * 2)

        #self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)

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
    def __init__(self, source: Node, dest: Node, parent: QGraphicsItem = None):
        """Edge constructor

        Args:
            source (Node): source node
            dest (Node): destination node
        """
        super().__init__(parent)
        self._source = source
        self._dest = dest

        self._tickness = 2 # TODO: poner un color que se vea bien tanto sobre blanco como sobre negro
        self._color = "#d6ccc2"

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
            self._arrow_target()


class GraphView(QGraphicsView):
    def __init__(self, graph: nx.DiGraph, start_token, parent=None):
        """GraphView constructor

        This widget can display a directed graph

        Args:
            graph (nx.DiGraph): a networkx directed graph
        """
        super().__init__()
        self._graph = graph
        self._scene = QGraphicsScene()
        self.setScene(self._scene)

        # Used to add space between nodes
        self._graph_scale = 2

        # Map node name to Node object {str=>Node}
        self._nodes_map = {}

        self._load_graph(start_token)
        self.set_nx_layout()


    def set_nx_layout(self):

        positions = graphviz_layout(self._graph.reverse(copy=True), prog='dot')

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


    def _load_graph(self, start_token):
        """Load graph into QGraphicsScene using Node class and Edge class"""

        self.scene().clear()
        self._nodes_map.clear()

        # Add start token
        item = Node(start_token)
        self.scene().addItem(item)
        self._nodes_map[start_token] = item


class MainWindow(QMainWindow):
    def __init__(self, start_token="S", parent=None):
        super().__init__(parent)
        self.node_name = start_token
        self.initUI()

    def initUI(self):
        self.setGeometry(400, 200, 450, 150)
        self.setWindowTitle('Simulación arbol de sintaxis')
        self.graph = nx.DiGraph()
        self.view = GraphView(self.graph, self.node_name, self)
        self.setCentralWidget(self.view)  # Agrega el GraphView como área central

        
    def add_node_dialog(self):
        nombres = ["A", "B"]

        self.graph.add_node(1, name="A")
        self.graph.add_node(2, name="A")

        item = Node("A")
        self.view.scene().addItem(item)
        self.view._nodes_map[1] = item

        source = self.view._nodes_map["S"]
        dest = self.view._nodes_map[1]
        self.view.scene().addItem(Edge(source, dest))

        self.graph.add_edge("S", 1)

        item = Node("A")
        self.view.scene().addItem(item)
        self.view._nodes_map[2] = item

        source = self.view._nodes_map["S"]
        dest = self.view._nodes_map[2]
        self.view.scene().addItem(Edge(source, dest))

        self.graph.add_edge("S", 2)

        self.view.set_nx_layout()

    def delete_node_dialog(self):
        self.graph.remove_node(2)

        self.view.scene().removeItem(self.view._nodes_map[2])
        self.view.set_nx_layout()

    def add_more_node(self):
        self.graph.add_node(3, name="a")

        item = Node("a", terminal=True)
        self.view.scene().addItem(item)
        self.view._nodes_map[3] = item

        source = self.view._nodes_map[1]
        dest = self.view._nodes_map[3]
        self.view.scene().addItem(Edge(source, dest))

        self.graph.add_edge(1, 3)

        self.view.set_nx_layout()
    def add_node(self, index, name, parent):
        # Create parent
        self.graph.add_node(index, name=name)
        item = Node(name)
        self.view.scene().addItem(item)
        self.view._nodes_map[index] = item

        # Create edge
        source = self.view._nodes_map[parent]
        dest = self.view._nodes_map[index]
        self.view.scene().addItem(Edge(source, dest))
        self.graph.add_edge(parent, index)          # Connect to parent

        self.view.set_nx_layout()

    def delete_node(self, iter):
        self.graph.remove_node(iter)

        self.view.scene().removeItem(self.view._nodes_map[iter])
        self.view.set_nx_layout()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MainWindow()
    widget.show()
    widget.resize(800, 600)

    sys.exit(app.exec())

