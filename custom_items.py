from PySide2.QtCore import Qt, QEvent, QPointF
from PySide2.QtGui import QFont, QColor
from PySide2.QtWidgets import QGraphicsTextItem, QGraphicsItem, \
    QGraphicsSceneMouseEvent, QGraphicsPixmapItem


class CustomQGraphicsTextItem(QGraphicsTextItem):

    def __init__(self, *args, **kwargs):
        super(CustomQGraphicsTextItem, self).__init__(*args, **kwargs)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setFlags(QGraphicsTextItem.ItemIsSelectable |
                      QGraphicsTextItem.ItemIsMovable |
                      QGraphicsTextItem.ItemSendsScenePositionChanges |
                      QGraphicsTextItem.ItemIsFocusable)
        self.setTransformOriginPoint(self.boundingRect().width() / 2,
                                     self.boundingRect().height()
                                     / 2)

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            scene_pos = self.scenePos()
            main_window = self.parent().parent().parent()
            main_window.item_pos.setText(f"({round(scene_pos.x(), 1)},"
                                         f" {round(scene_pos.y(), 1)})")
            return value
        if change == self.ItemSelectedHasChanged:
            if value:
                if len(self.scene().selectedItems()) == 1:
                    self.parent().init_font_settings(self)
                    scene_pos = self.scenePos()
                    main_window = self.parent().parent().parent()
                    main_window.item_pos.setText(
                        f"({round(scene_pos.x(), 1)}, "
                        f"{round(scene_pos.y(), 1)})")
                else:
                    self.parent().layout.setCurrentWidget(self.parent(
                    ).tabs)
            else:
                cursor = self.textCursor()
                cursor.clearSelection()
                self.setTextCursor(cursor)
                self.parent().layout.setCurrentWidget(self.parent().tabs)
                self.setTextInteractionFlags(Qt.NoTextInteraction)
                self.setFlags(QGraphicsTextItem.ItemIsSelectable |
                              QGraphicsTextItem.ItemIsMovable |
                              QGraphicsTextItem.ItemSendsScenePositionChanges |
                              QGraphicsTextItem.ItemIsFocusable)
                main_window = self.parent().parent().parent()
                main_window.item_pos.setText("")
        return QGraphicsItem.itemChange(self, change, value)

    def mouseDoubleClickEvent(self, event):
        if self.textInteractionFlags() == Qt.TextEditorInteraction:
            super(CustomQGraphicsTextItem, self).mouseDoubleClickEvent(event)
            return
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus(Qt.MouseFocusReason)
        click = QGraphicsSceneMouseEvent(QEvent.GraphicsSceneMousePress)
        click.setButton(event.button())
        click.setPos(event.pos())
        self.mousePressEvent(click)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            self.moveBy(0.0, 0.1)
        elif event.key() == Qt.Key_Up:
            self.moveBy(0.0, -0.1)
        elif event.key() == Qt.Key_Left:
            self.moveBy(-0.1, 0.0)
        elif event.key() == Qt.Key_Right:
            self.moveBy(0.1, 0.0)

    def get_info(self):
        letter_spacing_types = {QFont.PercentageSpacing: "Percentage spacing",
                                QFont.AbsoluteSpacing: "Absolute spacing"}
        capitalization_options = {QFont.MixedCase: "Not set",
                                  QFont.AllUppercase: "All uppercase",
                                  QFont.AllLowercase: "All lowercase",
                                  QFont.SmallCaps: "Small caps",
                                  QFont.Capitalize: "Capitalize"}
        font_styles = {QFont.StyleNormal: "Normal",
                       QFont.StyleItalic: "Italic",
                       QFont.StyleOblique: "Oblique"}
        font = self.font()
        background_size = self.scene().sceneRect()
        scene_pos = self.scenePos()
        pos_x = round(scene_pos.x() / background_size.width(), 2)
        pos_y = round(scene_pos.y() / background_size.height(), 2)
        info = {"item_type": "text",
                "item_scene_pos_x": pos_x,
                "item_scene_pos_y": pos_y,
                "text": self.toPlainText(),
                "font_family": font.family(),
                "font_size": font.pointSizeF(),
                "color": self.defaultTextColor().name(),
                "font_style": font_styles[font.style()],
                "font_weight": font.weight(),
                "capitalization": capitalization_options[
                    font.capitalization()],
                "stretch": font.stretch(),
                "kerning": font.kerning(),
                "overline": font.overline(),
                "strikeout": font.strikeOut(),
                "underline": font.underline(),
                "letter_spacing_type": letter_spacing_types[
                    font.letterSpacingType()],
                "letter_spacing_value": font.letterSpacing(),
                "opacity": self.opacity(),
                "rotation": self.rotation()}
        print(self.defaultTextColor().name())
        return info

    def load_info(self, info):
        background_size = self.scene().sceneRect()
        x = float(info["item_scene_pos_x"])
        y = float(info["item_scene_pos_y"])
        pos_x = round(background_size.width() * x, 0)
        pos_y = round(background_size.height() * y, 0)
        self.setPos(QPointF(pos_x, pos_y))
        self.setPlainText(info["text"])
        self.parent().set_letter_spacing_type(self,
                                              info["letter_spacing_type"])
        font = self.font()
        font.setFamily(info["font_family"])
        font.setPointSizeF(float(info["font_size"]))
        font.setWeight(int(info["font_weight"]))
        font.setStretch(int(info["stretch"]))
        font.setKerning(bool(info["kerning"]))
        font.setOverline(bool(info["overline"]))
        font.setStrikeOut(bool(info["strikeout"]))
        font.setUnderline(bool(info["underline"]))
        font.setLetterSpacing(font.letterSpacingType(), float(info[
                                                                  "letter_spacing_value"]))
        self.setFont(font)
        self.parent().set_font_style(info["font_style"], self)
        self.setDefaultTextColor(QColor(info["color"]))
        self.parent().set_text_capitalization(info["capitalization"], self)
        self.setOpacity(float(info["opacity"]))
        self.setRotation(float(info["rotation"]))


class CustomQGraphicsPixmapItem(QGraphicsPixmapItem):

    def __init__(self, *args, **kwargs):
        super(CustomQGraphicsPixmapItem, self).__init__(*args, **kwargs)
        self.parent = None
        self.path = ""
        self.setFlags(QGraphicsPixmapItem.ItemIsFocusable |
                      QGraphicsPixmapItem.ItemIsSelectable |
                      QGraphicsPixmapItem.ItemIsMovable |
                      QGraphicsPixmapItem.ItemSendsScenePositionChanges)
        self.setTransformOriginPoint(self.boundingRect().width() / 2,
                                     self.boundingRect().height() / 2)

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            scene_pos = self.scenePos()
            main_window = self.parent.parent().parent()
            main_window.item_pos.setText(f"({round(scene_pos.x(), 0)},"
                                         f" {round(scene_pos.y(), 0)})")
            return value
        if change == self.ItemSelectedHasChanged:
            if value:
                if len(self.scene().selectedItems()) == 1:
                    scene_pos = self.scenePos()
                    main_window = self.parent.parent().parent()
                    main_window.item_pos.setText(
                        f"({round(scene_pos.x(), 1)}, "
                        f"{round(scene_pos.y(), 1)})")
                    self.parent.init_image_settings(self)
                else:
                    self.parent.layout.setCurrentWidget(self.parent.tabs)
            else:
                main_window = self.parent.parent().parent()
                main_window.item_pos.setText("")
                self.parent.layout.setCurrentWidget(self.parent.tabs)
        return QGraphicsItem.itemChange(self, change, value)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            self.moveBy(0.0, 0.1)
        elif event.key() == Qt.Key_Up:
            self.moveBy(0.0, -0.1)
        elif event.key() == Qt.Key_Left:
            self.moveBy(-0.1, 0.0)
        elif event.key() == Qt.Key_Right:
            self.moveBy(0.1, 0.0)

    def get_info(self):
        scene_pos = self.scenePos()
        background_size = self.scene().sceneRect()
        pos_x = round(scene_pos.x() / background_size.width(), 2)
        pos_y = round(scene_pos.y() / background_size.height(), 2)
        info = {"item_type": "image",
                "image_path": self.path,
                "item_scene_pos_x": pos_x,
                "item_scene_pos_y": pos_y,
                "opacity": self.opacity(),
                "rotation": self.rotation(),
                "scale": self.scale()}
        return info

    def load_info(self, info):
        background_size = self.scene().sceneRect()
        x = float(info["item_scene_pos_x"])
        y = float(info["item_scene_pos_y"])
        pos_x = round(background_size.width() * x, 0)
        pos_y = round(background_size.height() * y, 0)
        self.setPos(QPointF(pos_x, pos_y))
        self.setOpacity(float(info["opacity"]))
        self.setRotation(float(info["rotation"]))
        self.setScale(float(info["scale"]))
