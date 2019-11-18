from PySide2.QtCore import Qt, QEvent, QPointF
from PySide2.QtGui import QFont, QColor
from PySide2.QtWidgets import QGraphicsTextItem, QGraphicsItem, \
    QGraphicsSceneMouseEvent, QGraphicsPixmapItem

from sidebar import set_font_style, set_text_capitalization, \
    set_letter_spacing_type


def move_item_with_arrows(item, key_press_event):
    if key_press_event.key() == Qt.Key_Down:
        item.moveBy(0.0, 0.1)
    elif key_press_event.key() == Qt.Key_Up:
        item.moveBy(0.0, -0.1)
    elif key_press_event.key() == Qt.Key_Left:
        item.moveBy(-0.1, 0.0)
    elif key_press_event.key() == Qt.Key_Right:
        item.moveBy(0.1, 0.0)


def load_item_position_from_config(item, config):
    background_size = item.scene().sceneRect()
    x = float(config["item_scene_pos_x"])
    y = float(config["item_scene_pos_y"])
    pos_x = round(background_size.width() * x, 0)
    pos_y = round(background_size.height() * y, 0)
    item.setPos(QPointF(pos_x, pos_y))


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
        move_item_with_arrows(self, event)

    def get_config(self):
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
        return info

    def load_config(self, config):
        load_item_position_from_config(self, config)
        self.setPlainText(config["text"])
        set_letter_spacing_type(self, config["letter_spacing_type"])
        font = self.font()
        font.setFamily(config["font_family"])
        font.setPointSizeF(float(config["font_size"]))
        font.setWeight(int(config["font_weight"]))
        font.setStretch(int(config["stretch"]))
        font.setKerning(bool(config["kerning"]))
        font.setOverline(bool(config["overline"]))
        font.setStrikeOut(bool(config["strikeout"]))
        font.setUnderline(bool(config["underline"]))
        font.setLetterSpacing(font.letterSpacingType(),
                              float(config["letter_spacing_value"]))
        self.setFont(font)
        set_font_style(config["font_style"], self)
        self.setDefaultTextColor(QColor(config["color"]))
        set_text_capitalization(config["capitalization"], self)
        self.setOpacity(float(config["opacity"]))
        self.setRotation(float(config["rotation"]))


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
        move_item_with_arrows(self, event)

    def get_config(self):
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

    def load_config(self, config):
        load_item_position_from_config(self, config)
        self.setOpacity(float(config["opacity"]))
        self.setRotation(float(config["rotation"]))
        self.setScale(float(config["scale"]))
