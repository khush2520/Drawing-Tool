import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class Shape:
    def __init__(self, shape_type, start_point, end_point, color):
        self.shape_type = shape_type
        self.start_point = start_point
        self.end_point = end_point
        self.color = color

class EditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.color_button = QPushButton("Change Color")
        self.color_button.clicked.connect(self.chooseColor)
        layout.addWidget(self.color_button)

        self.corner_button = None
        for item in parent.scene.selectedItems():
            if isinstance(item, QGraphicsRectItem):
                self.corner_combo = QComboBox()
                self.corner_combo.addItems(["Select Corner Style", "Sharp", "Curved"])
                self.corner_combo.currentIndexChanged.connect(self.handleCornerStyleChange)
                layout.addWidget(self.corner_combo)
                break

        self.setLayout(layout)

    def chooseColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            items = self.parent().scene.selectedItems()
            for item in items:
                if item.isSelected():
                    pen = item.pen()
                    pen.setColor(color)
                    item.setPen(pen)

    def handleCornerStyleChange(self, index):
        if index == 1:  # Sharp
            self.corner_style = "Sharp"
        elif index == 2:  # Curved
            self.corner_style = "Curved"
        else:
            self.corner_style = None

class GraphicsScene(QGraphicsScene):
    def __init__(self):
        super().__init__(0, 0, 400, 400)
        self.setBackgroundBrush(Qt.GlobalColor.white)
        self.startPoint = None
        self.endPoint = None
        self.drawingShape = None
        self.temporaryShape = None  # Add this line to store the temporary shape

    def mousePressEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.drawingShape:
                self.startPoint = event.scenePos()
                self.endPoint = self.startPoint
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.drawingShape:
                self.endPoint = event.scenePos()
                self.updateTemporaryShape()  # Call this method to update the temporary shape
            else:
                super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.drawingShape:
                self.endPoint = event.scenePos()
                self.drawShape()
                self.startPoint = None
                self.endPoint = None
                self.removeItem(self.temporaryShape)  # Remove the temporary shape after drawing
                self.temporaryShape = None
            else:
                super().mouseReleaseEvent(event)

    def updateTemporaryShape(self):
        if self.temporaryShape:
            self.removeItem(self.temporaryShape)

        if self.drawingShape == "Line":
            self.temporaryShape = QGraphicsLineItem(self.startPoint.x(), self.startPoint.y(), self.endPoint.x(), self.endPoint.y())
        elif self.drawingShape == "Rectangle":
            self.temporaryShape = QGraphicsRectItem(self.startPoint.x(), self.startPoint.y(), abs(self.endPoint.x() - self.startPoint.x()), abs(self.endPoint.y() - self.startPoint.y()))
        # elif self.drawingShape == "Ellipse":
        #     self.temporaryShape = QGraphicsEllipseItem((self.startPoint.x() + self.endPoint.x()) // 2, (self.startPoint.y() + self.endPoint.y()) // 2, abs(self.endPoint.x() - self.startPoint.x()), abs(self.endPoint.y() - self.startPoint.y()))

        if self.temporaryShape:
            self.addItem(self.temporaryShape)
            self.temporaryShape.setPen(QPen(Qt.GlobalColor.black, 2, Qt.PenStyle.DashLine))

    # Rest of the code remains the same
# class GraphicsScene(QGraphicsScene):
#     def __init__(self):
#         super().__init__(0, 0, 400, 400)
#         self.startPoint = None
#         self.endPoint = None
#         self.drawingShape = None

    # def mousePressEvent(self, event):
    #     if event.buttons() & Qt.MouseButton.LeftButton:
    #         if self.drawingShape:
    #             self.startPoint = event.scenePos()
    #             self.endPoint = self.startPoint
    #         else:
    #             super().mousePressEvent(event)

    # def mouseMoveEvent(self, event):
    #     if event.buttons() & Qt.MouseButton.LeftButton:
    #         if self.drawingShape:
    #             self.endPoint = event.scenePos()
    #             self.update()
    #         else:
    #             super().mouseMoveEvent(event)

    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.MouseButton.LeftButton:
    #         if self.drawingShape:
    #             self.endPoint = event.scenePos()
    #             self.drawShape()
    #             self.startPoint = None
    #             self.endPoint = None
    #         else:
    #             super().mouseReleaseEvent(event)

    def drawShape(self):
        if self.startPoint and self.endPoint:
            color = Qt.GlobalColor.black  # Default color
            shape = Shape(self.drawingShape, self.startPoint, self.endPoint, color)
            if shape.shape_type == "Line":
                line = QGraphicsLineItem(self.startPoint.x(),
                                         self.startPoint.y(),
                                         self.endPoint.x(),
                                         self.endPoint.y())
                line_pen = QPen(Qt.GlobalColor.black)
                line_pen.setWidth(2)
                line.setPen(line_pen)
                self.addItem(line)
                line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            elif shape.shape_type == "Rectangle":
                rect = QGraphicsRectItem(shape.start_point.x(),
                                         shape.start_point.y(),
                                         abs(shape.end_point.x() - shape.start_point.x()),
                                         abs(shape.end_point.y() - shape.start_point.y()))
                rect_pen = QPen(Qt.GlobalColor.black)
                rect_pen.setWidth(2)
                rect.setPen(rect_pen)
                self.addItem(rect)
                rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            # elif shape.shape_type == "Ellipse":
            #     ellipse = QGraphicsEllipseItem((shape.start_point.x() + shape.end_point.x()) // 2,
            #                                    (shape.start_point.y() + shape.end_point.y()) // 2,
            #                                    abs(shape.end_point.x() - shape.start_point.x()),
            #                                    abs(shape.end_point.y() - shape.start_point.y()))
            #     ellipse_brush = QBrush(Qt.GlobalColor.blue)
            #     ellipse.setBrush(ellipse_brush)
            #     ellipse_pen = QPen(Qt.GlobalColor.green)
            #     ellipse_pen.setWidth(5)
            #     ellipse.setPen(ellipse_pen)
            #     self.addItem(ellipse)
            #     ellipse.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            #     ellipse.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            else:
                pass


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.scene = GraphicsScene()

        self.setWindowTitle("Drawing App")

        vbox = QVBoxLayout()

        line_button = QPushButton(QIcon("line_icon.png"), "Line", self)
        line_button.clicked.connect(lambda: self.setDrawingShape("Line"))
        vbox.addWidget(line_button)

        rectangle_button = QPushButton(QIcon("rectangle_icon.png"), "Rectangle", self)
        rectangle_button.clicked.connect(lambda: self.setDrawingShape("Rectangle"))
        vbox.addWidget(rectangle_button)

        # ellipse_button = QPushButton(QIcon("ellipse_icon.png"), "Ellipse", self)
        # ellipse_button.clicked.connect(lambda: self.setDrawingShape("Ellipse"))
        # vbox.addWidget(ellipse_button)

        move_button = QPushButton(QIcon("move_icon.png"), "Select", self)
        move_button.clicked.connect(lambda: self.setDrawingShape(None))
        vbox.addWidget(move_button)



        up = QPushButton("Up")
        up.clicked.connect(self.up)
        vbox.addWidget(up)

        down = QPushButton("Down")
        down.clicked.connect(self.down)
        vbox.addWidget(down)

        group_button = QPushButton("Group")
        group_button.clicked.connect(self.groupSelectedShapes)
        vbox.addWidget(group_button)

        ungroup_button = QPushButton("Ungroup")
        ungroup_button.clicked.connect(self.ungroupSelectedShapes)
        vbox.addWidget(ungroup_button)

        rotate = QSlider()
        rotate.setRange(0, 360)
        rotate.valueChanged.connect(self.rotate)
        vbox.addWidget(rotate)

        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(self.copySelectedShape)
        vbox.addWidget(copy_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.deleteSelectedShape)
        vbox.addWidget(delete_button)

        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit)
        vbox.addWidget(edit_button)

        view = QGraphicsView(self.scene)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)

        hbox = QHBoxLayout(self)
        hbox.addLayout(vbox)
        hbox.addWidget(view)

        self.setLayout(hbox)

    def up(self):
        items = self.scene.selectedItems()
        for item in items:
            z = item.zValue()
            item.setZValue(z + 1)

    def down(self):
        items = self.scene.selectedItems()
        for item in items:
            z = item.zValue()
            item.setZValue(z - 1)

    def rotate(self, value):
        items = self.scene.selectedItems()
        for item in items:
            item.setRotation(value)

    def setDrawingShape(self, shape):
        self.scene.drawingShape = shape

    def copySelectedShape(self):
        items = self.scene.selectedItems()
        for item in items:
            if isinstance(item, QGraphicsLineItem):
                line = item
                new_line = QGraphicsLineItem(line.line().x1(), line.line().y1(), line.line().x2(), line.line().y2())
                new_line.setPen(line.pen())
                new_line.setPos(line.pos() + QPointF(20, 20))
                new_line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                new_line.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                self.scene.addItem(new_line)
            elif isinstance(item, QGraphicsRectItem):
                rect = item
                new_rect = QGraphicsRectItem(rect.rect())
                new_rect.setBrush(rect.brush())
                new_rect.setPen(rect.pen())
                new_rect.setPos(rect.pos() + QPointF(20, 20))
                new_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                new_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                self.scene.addItem(new_rect)
            elif isinstance(item, QGraphicsItemGroup):
                group = item
                new_group = QGraphicsItemGroup()

                for child in group.childItems():
                    if isinstance(child, QGraphicsLineItem):
                        line = child
                        new_line = QGraphicsLineItem(line.line().x1(), line.line().y1(), line.line().x2(), line.line().y2())
                        new_line.setPen(line.pen())
                        new_line.setPos(line.pos())
                        new_group.addToGroup(new_line)
                    elif isinstance(child, QGraphicsRectItem):
                        rect = child
                        new_rect = QGraphicsRectItem(rect.rect())
                        new_rect.setBrush(rect.brush())
                        new_rect.setPen(rect.pen())
                        new_rect.setPos(rect.pos())
                        new_group.addToGroup(new_rect)
                    elif isinstance(child, QGraphicsEllipseItem):
                        ellipse = child
                        new_ellipse = QGraphicsEllipseItem(ellipse.rect())
                        new_ellipse.setBrush(ellipse.brush())
                        new_ellipse.setPen(ellipse.pen())
                        new_ellipse.setPos(ellipse.pos())
                        new_group.addToGroup(new_ellipse)

                new_group.setPos(group.pos() + QPointF(20, 20))
                new_group.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                new_group.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                self.scene.addItem(new_group)
            # elif isinstance(item, QGraphicsEllipseItem):
            #     ellipse = item
            #     new_ellipse = QGraphicsEllipseItem(ellipse.rect())
            #     new_ellipse.setBrush(ellipse.brush())
            #     new_ellipse.setPen(ellipse.pen())
            #     new_ellipse.setPos(ellipse.pos() + QPointF(20, 20))
            #     new_ellipse.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            #     new_ellipse.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            #     self.scene.addItem(new_ellipse)
    def deleteSelectedShape(self):
        items = self.scene.selectedItems()
        for item in items:
            self.scene.removeItem(item)
    def groupSelectedShapes(self):
        items = self.scene.selectedItems()
        if len(items) > 1:
            group = QGraphicsItemGroup()
            for item in items:
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
                group.addToGroup(item)
            self.scene.addItem(group)

            group.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            group.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def ungroupSelectedShapes(self):
        items = self.scene.selectedItems()
        for item in items:
            if isinstance(item, QGraphicsItemGroup):
                group = item
                self.scene.removeItem(group)
                group_pos = group.pos()
                for child in group.childItems():
                    child_pos = child.pos()
                    ungrouped_pos = group_pos + child_pos
                    self.scene.addItem(child)
                    child.setPos(ungrouped_pos)
                    child.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                    child.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def edit(self):
        items = self.scene.selectedItems()
        if not items:
            QMessageBox.warning(self, "No Selection", "No item selected.")
            return

        dialog = EditDialog(self)
        dialog.exec()

        for item in items:
            if item.isSelected():
                pen = item.pen()
                # if dialog.corner_style:
                #     if isinstance(item, QGraphicsRectItem):
                #         if dialog.corner_style == "Sharp":
                #             pass

                #         elif dialog.corner_style == "Curved":
                #             pass


                if dialog.color_button.isChecked():
                    color = dialog.color_button.palette().color(dialog.color_button.backgroundRole())
                    pen.setColor(color)
                item.setPen(pen)
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()