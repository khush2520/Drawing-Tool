import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

items_to_save = []
class Shape:
    def __init__(self, shape_type, start_point, end_point, color):
        self.shape_type = shape_type
        self.start_point = start_point
        self.end_point = end_point
        self.color = color
    
class ShapeFactory:
    @staticmethod
    def create_shape(shape_type, startPoint = 0, endPoint = 0):
        if shape_type == "Line":
            return QGraphicsLineItem(startPoint.x(), startPoint.y(), endPoint.x(), endPoint.y())
        elif shape_type == "Rectangle":
                return QGraphicsRectItem(startPoint.x(), startPoint.y(), abs(endPoint.x() - startPoint.x()), abs(endPoint.y() - startPoint.y()))
        else:
            raise ValueError("Invalid shape type")
    


class RoundedRectItem(QGraphicsRectItem):
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def shape(self):
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 50, 50)  # Adjust the radius as needed
        return path

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRoundedRect(self.rect(), 50, 50)  # Adjust the radius as needed

        if self.isSelected():
            pen = QPen(Qt.GlobalColor.gray, 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())


class EditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.color_button = QPushButton("Change Color")
        self.corner_style = "Sharp"
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
        if index == 1:
            self.corner_style = "Sharp"
        elif index == 2:
            self.corner_style = "Curved"
        else:
            self.corner_style = None

class GraphicsScene(QGraphicsScene):
    def __init__(self):
        super().__init__(0, 0, 400, 400)
        # items_to_save = []
        self.setBackgroundBrush(Qt.GlobalColor.black)
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
                self.removeItem(self.temporaryShape)    
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
        if self.temporaryShape:
            self.addItem(self.temporaryShape)
            self.temporaryShape.setPen(QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.DashLine))



    def drawShape(self):
        global items_to_save
        if self.startPoint and self.endPoint:
            shape = ShapeFactory.create_shape(self.drawingShape, self.startPoint, self.endPoint)
            shape_pen = QPen(Qt.GlobalColor.white)
            shape_pen.setWidth(4)
            shape.setPen(shape_pen)
            shape.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            shape.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            self.addItem(shape)
            items_to_save.append(shape)
        else:
            pass
            
        
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.scene = GraphicsScene()

        self.setWindowTitle("Drawing App")

        vbox = QVBoxLayout()

        saveActionTxt = QPushButton("Save as .txt", self)
        vbox.addWidget(saveActionTxt)
        saveActionTxt.clicked.connect(self.save_as_txt)

        saveActionPng = QPushButton("Save as .png", self)
        vbox.addWidget(saveActionPng)
        saveActionPng.clicked.connect(self.save_as_png)

        line_button = QPushButton(QIcon("line_icon.png"), "Line", self)
        line_button.clicked.connect(lambda: self.setDrawingShape("Line"))
        vbox.addWidget(line_button)

        rectangle_button = QPushButton(QIcon("rectangle_icon.png"), "Rectangle", self)
        rectangle_button.clicked.connect(lambda: self.setDrawingShape("Rectangle"))
        vbox.addWidget(rectangle_button)


        move_button = QPushButton(QIcon("move_icon.png"), "Select", self)
        move_button.clicked.connect(lambda: self.setDrawingShape(None))
        vbox.addWidget(move_button)

        up = QPushButton("Bring To Front")
        up.clicked.connect(self.up)
        vbox.addWidget(up)

        down = QPushButton("Send To Back")
        down.clicked.connect(self.down)
        vbox.addWidget(down)

        group_button = QPushButton("Group")
        group_button.clicked.connect(self.groupSelectedShapes)
        vbox.addWidget(group_button)

        ungroup_button = QPushButton("Ungroup")
        ungroup_button.clicked.connect(self.ungroupSelectedShapes)
        vbox.addWidget(ungroup_button)


        ungroupall_button = QPushButton("Ungroup All")
        ungroupall_button.clicked.connect(self.ungroupAllSelectedShapes)
        vbox.addWidget(ungroupall_button)

        rotate = QSlider(Qt.Orientation.Horizontal)
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

    # method for saving canvas
    def save_as_txt(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Drawing", "", "Text Files (*.txt)")
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    def save_items(items, group_level=0):
                        for item in items:
                            if isinstance(item, QGraphicsLineItem):
                                line = item.line()
                                file.write(f"{'  ' * group_level}line {line.x1()} {line.y1()} {line.x2()} {line.y2()} {item.pen().color().name()}\n")
                            elif isinstance(item, QGraphicsRectItem):
                                rect = item.rect()
                                if isinstance(item, RoundedRectItem):
                                    file.write(f"{'  ' * group_level}roundedrect {rect.x()} {rect.y()} {rect.width()} {rect.height()} {item.pen().color().name()}\n")
                                else:
                                    file.write(f"{'  ' * group_level}rect {rect.x()} {rect.y()} {rect.width()} {rect.height()} {item.pen().color().name()}\n")
                            elif isinstance(item, QGraphicsItemGroup):
                                file.write(f"{'  ' * group_level}begin\n")
                                save_items(item.childItems(), group_level + 1)
                                file.write(f"{'  ' * group_level}end\n")

                    save_items(items_to_save)
            except Exception as e:
                print(f"Error saving file: {e}")

    def save_as_png(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Drawing", "", "PNG Files (*.png)")
        if file_path:
            try:
                pixmap = QPixmap(self.scene.sceneRect().size().toSize())
                pixmap.fill(Qt.GlobalColor.black)
                painter = QPainter(pixmap)
                self.scene.render(painter)
                painter.end()  # End the painting before saving
                pixmap.save(file_path)
            except Exception as e:
                print(f"Error saving file: {e}")


    def color_to_char(self, color):
        if color == Qt.GlobalColor.red:
            return "r"
        elif color == Qt.GlobalColor.green:
            return "g"
        elif color == Qt.GlobalColor.blue:
            return "b"
        else:
            return "k"  # Default to black if color not recognized

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
        global items_to_save

        def copy_recursive(item):
            if isinstance(item, QGraphicsItemGroup):
                new_group = QGraphicsItemGroup()
                for child in item.childItems():
                    new_child = copy_recursive(child)
                    new_group.addToGroup(new_child)
                offset = QPointF(20, 20)
                new_group.setPos(item.pos() + offset)
                new_group.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                new_group.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                self.scene.addItem(new_group)
                items_to_save.append(new_group)
                return new_group
            elif isinstance(item, QGraphicsLineItem):
                line = item.line()
                start_point = QPointF(line.x1(), line.y1())
                end_point = QPointF(line.x2(), line.y2())
                new_shape = ShapeFactory.create_shape("Line", start_point, end_point)
            elif isinstance(item, QGraphicsRectItem):
                rect = item.rect()
                start_point = QPointF(rect.x(), rect.y())
                end_point = QPointF(rect.x() + rect.width(), rect.y() + rect.height())
                new_shape = ShapeFactory.create_shape("Rectangle", start_point, end_point)
                if isinstance(item, RoundedRectItem):
                    rounded_rect = RoundedRectItem(new_shape.rect())
                    rounded_rect.setBrush(new_shape.brush())
                    new_shape = rounded_rect
            offset = QPointF(20, 20)
            new_shape.setPen(item.pen())
            new_shape.setPos(item.pos() + offset)
            new_shape.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            new_shape.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            self.scene.addItem(new_shape)
            items_to_save.append(new_shape)
            return new_shape

        items = self.scene.selectedItems()
        if items:
            for item in items:
                copy_recursive(item)

    def deleteSelectedShape(self):
        global items_to_save

        items = self.scene.selectedItems()
        for item in items:
            self.scene.removeItem(item)
            items_to_save.remove(item)


    def groupSelectedShapes(self):
        global items_to_save

        items = self.scene.selectedItems()
        if len(items) > 1:
            group = QGraphicsItemGroup()
            for item in items:
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
                items_to_save.remove(item)
                group.addToGroup(item)

            self.scene.addItem(group)
            items_to_save.append(group)

            group.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            group.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def ungroupSelectedShapes(self):
        global items_to_save

        items = self.scene.selectedItems()
        for item in items:
            if isinstance(item, QGraphicsItemGroup):
                group = item
                self.scene.removeItem(group)
                items_to_save.remove(group)
                group_pos = group.pos()
                for child in group.childItems():
                    child_pos = child.pos()
                    ungrouped_pos = group_pos + child_pos
                    self.scene.addItem(child)
                    items_to_save.append(child)
                    child.setPos(ungrouped_pos)
                    child.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                    child.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def ungroupAllSelectedShapes(self):
        global items_to_save

        def ungroup_recursive(group):
            group_pos = group.pos()
            for child in group.childItems():
                self.scene.removeItem(group)
                items_to_save.remove(group)
                if isinstance(child, QGraphicsItemGroup):
                    ungroup_recursive(child)
                else:
                    child_pos = child.pos()
                    ungrouped_pos = group_pos + child_pos
                    self.scene.addItem(child)
                    items_to_save.append(child)
                    child.setPos(ungrouped_pos)
                    child.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                    child.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        items = self.scene.selectedItems()
        for item in items:
            if isinstance(item, QGraphicsItemGroup):
                ungroup_recursive(item)

    def edit(self):
        items = self.scene.selectedItems()
        if not items:
            QMessageBox.warning(self, "No Selection", "No item selected.")
            return

        for item in items:
            if isinstance(item, QGraphicsItemGroup):
                QMessageBox.warning(self, "Group Object(s) Selected", "Group Object(s) Selected")
                return

        dialog = EditDialog(self)
        dialog.exec()

        for item in items:
            if item.isSelected():
                pen = item.pen()
                if  isinstance(item, QGraphicsRectItem) or isinstance(item, RoundedRectItem):
                    if dialog.corner_style:
                        if dialog.corner_style == "Curved" and isinstance(item, QGraphicsRectItem):
                            rect = item.rect()
                            rounded_rect = RoundedRectItem(rect) # rounded_rect is an instance of RoundedRectItem
                            rounded_rect.setPen(item.pen())
                            rounded_rect.setBrush(item.brush())
                            self.scene.removeItem(item)
                            self.scene.addItem(rounded_rect)
                            items_to_save.remove(item)
                            items_to_save.append(rounded_rect)
                            item = rounded_rect

                        elif dialog.corner_style == "Sharp" and isinstance(item, RoundedRectItem):
                            rect = item.rect()
                            sharp_rect = QGraphicsRectItem(rect)
                            sharp_rect.setPen(item.pen())
                            sharp_rect.setBrush(item.brush())
                            sharp_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                            sharp_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                            self.scene.removeItem(item)
                            self.scene.addItem(sharp_rect)
                            items_to_save.remove(item)
                            items_to_save.append(sharp_rect)
                            item = sharp_rect

                if dialog.color_button.isChecked():
                    color = dialog.color_button.palette().color(dialog.color_button.backgroundRole())
                    pen.setColor(color)
                item.setPen(pen)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
