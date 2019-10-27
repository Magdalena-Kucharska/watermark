from PySide2.QtCore import Qt, QEvent
from PySide2.QtWidgets import QGraphicsTextItem, QGraphicsItem, \
    QGraphicsSceneMouseEvent, QGraphicsPixmapItem


class CustomQGraphicsTextItem(QGraphicsTextItem):

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            scene_pos = self.scenePos()
            main_window = self.parent().parent().parent()
            main_window.item_pos.setText(f"({scene_pos.x()}, {scene_pos.y()})")
            return value
        if change == self.ItemSelectedHasChanged:
            if value:
                if len(self.scene().selectedItems()) == 1:
                    self.parent().init_font_settings(self)
                    scene_pos = self.scenePos()
                    main_window = self.parent().parent().parent()
                    main_window.item_pos.setText(
                        f"({scene_pos.x()}, {scene_pos.y()})")
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


class CustomQGraphicsPixmapItem(QGraphicsPixmapItem):

    def __init__(self, *args, **kwargs):
        super(CustomQGraphicsPixmapItem, self).__init__(*args, **kwargs)
        self.parent = None

    def set_parent(self, parent):
        self.parent = parent

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            scene_pos = self.scenePos()
            main_window = self.parent.parent().parent()
            main_window.item_pos.setText(f"({scene_pos.x()}, {scene_pos.y()})")
            return value
        if change == self.ItemSelectedHasChanged:
            if value:
                if len(self.scene().selectedItems()) == 1:
                    scene_pos = self.scenePos()
                    main_window = self.parent.parent().parent()
                    main_window.item_pos.setText(
                        f"({scene_pos.x()}, {scene_pos.y()})")
                    self.parent.init_image_settings(self)
                else:
                    self.parent.layout.setCurrentWidget(self.parent.navigation)
            else:
                main_window = self.parent.parent().parent()
                main_window.item_pos.setText("")
                self.parent.layout.setCurrentWidget(self.parent.navigation)
        return QGraphicsItem.itemChange(self, change, value)
