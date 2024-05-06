import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import xml.etree.ElementTree as ET

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
        self.isPartOfGroup = False

    def shape(self):
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 50, 50)  # Adjust the radius as needed
        return path

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRoundedRect(self.rect(), 50, 50)  # Adjust the radius as needed

        if self.isSelected():
            if not self.isPartOfGroup:
                pen = QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DashLine)
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
            self.temporaryShape.setPen(QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.DashLine))

    def drawShape(self):
        global items_to_save
        self.unsaved_changes = True  # Set flag to True after making changes

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
        super(MainWindow, self).__init__()


        self.scene = GraphicsScene()

        self.setWindowTitle("Drawing App")
        self.unsaved_changes = False

        vbox = QVBoxLayout()

        open_button = QPushButton("Open", self)
        open_button.clicked.connect(self.open_file)
        vbox.addWidget(open_button)

        saveActionTxt = QPushButton("Save as .txt", self)
        vbox.addWidget(saveActionTxt)
        saveActionTxt.clicked.connect(self.save_as_txt)

        saveActionPng = QPushButton("Save as .png", self)
        vbox.addWidget(saveActionPng)
        saveActionPng.clicked.connect(self.save_as_png)

        save_action_xml = QPushButton("Save as .xml", self)
        save_action_xml.clicked.connect(self.save_as_xml)
        vbox.addWidget(save_action_xml)

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

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Drawing", "", "Text Files (*.txt)")
        if file_path:
            try:
                self.scene.clear()
                with open(file_path, 'r') as file:
                    def load_items(group=None):
                        while True:
                            line = file.readline().strip()
                            if not line:
                                break
                            data = line.split()
                            if data[0] == "line":
                                x1, y1, x2, y2, color = float(data[1]), float(data[2]), float(data[3]), float(data[4]), data[5]
                                line_item = QGraphicsLineItem(x1, y1, x2, y2)
                                line_item.setPen(QPen(QColor(color)))
                                line_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                                line_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                                if group:
                                    group.addToGroup(line_item)
                                else:
                                    self.scene.addItem(line_item)
                            elif data[0] == "rect":
                                x, y, width, height, color = float(data[1]), float(data[2]), float(data[3]), float(data[4]), data[5]
                                rect_item = QGraphicsRectItem(x, y, width, height)
                                rect_item.setPen(QPen(QColor(color)))
                                rect_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                                rect_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                                if group:
                                    group.addToGroup(rect_item)
                                else:
                                    self.scene.addItem(rect_item)
                            elif data[0] == "roundedrect":
                                x, y, width, height, color = float(data[1]), float(data[2]), float(data[3]), float(data[4]), data[5]
                                rounded_rect_item = RoundedRectItem(QRectF(x, y, width, height))
                                rounded_rect_item.setPen(QPen(QColor(color)))
                                rounded_rect_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                                rounded_rect_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                                if group:
                                    group.addToGroup(rounded_rect_item)
                                else:
                                    self.scene.addItem(rounded_rect_item)
                            elif data[0] == "begin":
                                new_group = QGraphicsItemGroup()
                                items_to_save.append()
                                load_items(new_group)
                                if group:
                                    group.addToGroup(new_group)
                                else:
                                    self.scene.addItem(new_group)
                            elif data[0] == "end":
                                return

                    load_items()
            except Exception as e:
                print(f"Error opening file: {e}")

    def closeEvent(self, event):
        if self.unsaved_changes:
            reply = QMessageBox.question(self, "Unsaved Changes",
                                        "There are unsaved changes. Do you want to exit?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def set_unsaved_changes(self, value=True):
        self.unsaved_changes = value

    def save_as_txt(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Drawing", "", "Text Files (*.txt)")
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    def save_items(items):
                        for item in items:
                            if isinstance(item, QGraphicsLineItem):
                                line = item.line()
                                file.write(f"line {line.x1()} {line.y1()} {line.x2()} {line.y2()} {item.pen().color().name()}\n")
                            elif isinstance(item, QGraphicsRectItem):
                                rect = item.rect()
                                top_left = rect.topLeft()
                                bottom_right = rect.bottomRight()
                                if isinstance(item, RoundedRectItem):
                                    file.write(f"rect {top_left.x()} {top_left.y()} {bottom_right.x()} {bottom_right.y()} {item.pen().color().name()} r\n")
                                else:
                                    file.write(f"rect {top_left.x()} {top_left.y()} {bottom_right.x()} {bottom_right.y()} {item.pen().color().name()} s\n")
                            elif isinstance(item, QGraphicsItemGroup):
                                file.write(f"begin\n")
                                save_items(item.childItems())
                                file.write(f"end\n")

                    save_items(items_to_save)
                    self.unsaved_changes = False
            except Exception as e:
                print(f"Error saving file: {e}")
    
    def save_as_xml(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Drawing", "", "XML Files (*.xml)")
        if file_path:
            try:
                root = ET.Element("drawing")

                def save_item(item_to_write, parent_element=None):
                    if isinstance(item_to_write, QGraphicsLineItem):
                        line = item_to_write.line()
                        line_element = ET.SubElement(parent_element, "line")
                        begin_element = ET.SubElement(line_element, "begin")
                        x_begin = ET.SubElement(begin_element, "x")
                        x_begin.text = str(line.x1())
                        y_begin = ET.SubElement(begin_element, "y")
                        y_begin.text = str(line.y1())
                        end_element = ET.SubElement(line_element, "end")
                        x_end = ET.SubElement(end_element, "x")
                        x_end.text = str(line.x2())
                        y_end = ET.SubElement(end_element, "y")
                        y_end.text = str(line.y2())
                        color_element = ET.SubElement(line_element, "color")
                        color_element.text = item_to_write.pen().color().name()
                    elif isinstance(item_to_write, QGraphicsRectItem):
                        rect = item_to_write.rect()
                        rect_element = ET.SubElement(parent_element, "rectangle")
                        upper_left_element = ET.SubElement(rect_element, "upper-left")
                        x_upper_left = ET.SubElement(upper_left_element, "x")
                        x_upper_left.text = str(rect.x())
                        y_upper_left = ET.SubElement(upper_left_element, "y")
                        y_upper_left.text = str(rect.y())
                        lower_right_element = ET.SubElement(rect_element, "lower-right")
                        x_lower_right = ET.SubElement(lower_right_element, "x")
                        x_lower_right.text = str(rect.x() + rect.width())
                        y_lower_right = ET.SubElement(lower_right_element, "y")
                        y_lower_right.text = str(rect.y() + rect.height())
                        color_element = ET.SubElement(rect_element, "color")
                        color_element.text = item_to_write.pen().color().name()
                        corner_element = ET.SubElement(rect_element, "corner")
                        corner_element.text = "rounded" if isinstance(item_to_write, RoundedRectItem) else "square"
                    elif isinstance(item_to_write, QGraphicsItemGroup):
                        group_element = ET.SubElement(parent_element, "group")
                        for item in item_to_write.childItems():
                            save_item(item, group_element)
                for item in items_to_save:
                    save_item(item, root)
                self.unsaved_changes = False
                tree = ET.ElementTree(root)
                tree.write(file_path, encoding="utf-8", xml_declaration=True)
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
                self.unsaved_changes = False  # Set flag to False after saving
            except Exception as e:
                print(f"Error saving file: {e}")

    def up(self):
        self.unsaved_changes = True  # Set flag to True after making changes
        items = self.scene.selectedItems()
        for item in items:
            z = item.zValue()
            item.setZValue(z + 1)

    def down(self):
        self.unsaved_changes = True  # Set flag to True after making changes
        items = self.scene.selectedItems()
        for item in items:
            z = item.zValue()
            item.setZValue(z - 1)

    def rotate(self, value):
        self.unsaved_changes = True  # Set flag to True after making changes
        items = self.scene.selectedItems()
        for item in items:
            item.setRotation(value)

    def setDrawingShape(self, shape):
        self.unsaved_changes = True  # Set flag to True after making changes
        self.scene.drawingShape = shape


    def copySelectedShape(self):
        self.unsaved_changes = True  # Set flag to True after making changes

        global items_to_save

        def copy_recursive(item):
            if isinstance(item, QGraphicsItemGroup):
                new_group = QGraphicsItemGroup()
                for child in item.childItems():
                    new_child = copy_recursive(child)
                    new_group.addToGroup(new_child)
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
        self.unsaved_changes = True  # Set flag to True after making changes
        items = self.scene.selectedItems()
        for item in items:
            self.scene.removeItem(item)
            items_to_save.remove(item)


    def groupSelectedShapes(self):
        global items_to_save

        items = self.scene.selectedItems()
        if len(items) > 1:
            self.unsaved_changes = True  # Set flag to True after making changes
            group = QGraphicsItemGroup()
            for item in items:
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
                items_to_save.remove(item)
                group.addToGroup(item)
                if isinstance(item,RoundedRectItem):
                    item.isPartOfGroup = True

            self.scene.addItem(group)
            items_to_save.append(group)

            group.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            group.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def ungroupSelectedShapes(self):
        global items_to_save

        items = self.scene.selectedItems()
        for item in items:
            self.unsaved_changes = True  # Set flag to True after making changes
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
                    if isinstance(child,RoundedRectItem):
                        child.isPartOfGroup = False

    def ungroupAllSelectedShapes(self):
        global items_to_save

        def ungroup_recursive(group):
            group_pos = group.pos()
            self.unsaved_changes = True  # Set flag to True after making changes
            for child in group.childItems():
                self.scene.removeItem(group)
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
                    if isinstance(child,RoundedRectItem):
                        child.isPartOfGroup = False

        items = self.scene.selectedItems()
        for item in items:
            if isinstance(item, QGraphicsItemGroup):
                items_to_save.remove(item)
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

        self.unsaved_changes = True  # Set flag to True after making changes
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
                            rounded_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                            rounded_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
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
