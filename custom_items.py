from PySide2.QtCore import Qt, QEvent
from PySide2.QtWidgets import QGraphicsTextItem, QGraphicsItem, \
    QGraphicsSceneMouseEvent


class CustomQGraphicsTextItem(QGraphicsTextItem):

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            rect = self.scene().sceneRect()
            if not rect.contains(value):
                value.setX(min(rect.right() - self.boundingRect().width(),
                               max(value.x(), rect.left())))
                value.setY(min(rect.bottom() - self.boundingRect().height(),
                               max(value.y(), rect.top())))
                return value
        if change == self.ItemSelectedHasChanged:
            if value:
                if len(self.scene().selectedItems()) == 1:
                    self.parent().init_font_settings(self)
                else:
                    self.parent().remove_layout()
                    self.parent().hide()
                    self.parent().parent().images_panel.images_nav.show()
            else:
                cursor = self.textCursor()
                cursor.clearSelection()
                self.setTextCursor(cursor)
                self.parent().remove_layout()
                self.setTextInteractionFlags(Qt.NoTextInteraction)
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
