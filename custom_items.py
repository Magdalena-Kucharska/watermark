from PySide2.QtCore import Qt, QEvent
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QGraphicsTextItem, QGraphicsItem, \
    QGraphicsSceneMouseEvent, QGraphicsPixmapItem


class CustomQGraphicsTextItem(QGraphicsTextItem):

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            scene_pos = self.scenePos()
            main_window = self.parent().parent().parent()
            main_window.item_pos.setText(f"({int(scene_pos.x())},"
                                         f" {int(scene_pos.y())})")
            return value
        if change == self.ItemSelectedHasChanged:
            if value:
                if len(self.scene().selectedItems()) == 1:
                    self.parent().init_font_settings(self)
                    scene_pos = self.scenePos()
                    main_window = self.parent().parent().parent()
                    main_window.item_pos.setText(
                        f"({int(scene_pos.x())}, {int(scene_pos.y())})")
                else:
                    self.parent().layout.setCurrentWidget(self.parent(

                    ).navigation)
            else:
                cursor = self.textCursor()
                cursor.clearSelection()
                self.setTextCursor(cursor)
                self.parent().layout.setCurrentWidget(self.parent().navigation)
                self.setTextInteractionFlags(Qt.NoTextInteraction)
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


class CustomQGraphicsPixmapItem(QGraphicsPixmapItem):

    def __init__(self, *args, **kwargs):
        super(CustomQGraphicsPixmapItem, self).__init__(*args, **kwargs)
        self.parent = None
        self.path = ""

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            scene_pos = self.scenePos()
            main_window = self.parent.parent().parent()
            main_window.item_pos.setText(f"({int(scene_pos.x())},"
                                         f" {int(scene_pos.y())})")
            return value
        if change == self.ItemSelectedHasChanged:
            if value:
                if len(self.scene().selectedItems()) == 1:
                    scene_pos = self.scenePos()
                    main_window = self.parent.parent().parent()
                    main_window.item_pos.setText(
                        f"({int(scene_pos.x())}, {int(scene_pos.y())})")
                    self.parent.init_image_settings(self)
                else:
                    self.parent.layout.setCurrentWidget(self.parent.navigation)
            else:
                main_window = self.parent.parent().parent()
                main_window.item_pos.setText("")
                self.parent.layout.setCurrentWidget(self.parent.navigation)
        return QGraphicsItem.itemChange(self, change, value)

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
