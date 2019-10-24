import os

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QListWidget, QListView, QProgressDialog, \
    QListWidgetItem, QGraphicsView, QGraphicsScene, QHBoxLayout


class ImagesNav(QListWidget):

    def __init__(self, *args, **kwargs):
        super(ImagesNav, self).__init__(*args, **kwargs)
        self.loaded_images = None
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setViewMode(QListView.IconMode)
        self.setIconSize(QSize(128, 128))
        self.setResizeMode(QListView.Adjust)
        self.setFixedWidth(160)
        self.setGridSize(QSize(128, 150))
        self.setItemAlignment(Qt.AlignHCenter)

    def update_navbar(self):
        self.clear()
        progress = QProgressDialog("Loading images...", "Cancel", 0,
                                   len(self.loaded_images), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Watermark")
        for i, image_path in enumerate(self.loaded_images):
            progress.setValue(i)
            if progress.wasCanceled():
                break
            scaled_image = QPixmap(image_path).scaled(QSize(128, 128))
            item = QListWidgetItem(QIcon(scaled_image), os.path.basename(
                image_path))
            item.setData(Qt.UserRole, image_path)
            self.addItem(item)
        progress.setValue(len(self.loaded_images))


class ImagesPanel(QHBoxLayout):
    def __init__(self, *args, **kwargs):
        super(ImagesPanel, self).__init__(*args, **kwargs)
        self.images_nav = ImagesNav()
        self.images_nav.clicked.connect(lambda x: self.load_image(
            self.images_nav.currentItem().data(Qt.UserRole)))
        self.image_edit_area = QGraphicsView()
        self.image_edit_area.setScene(QGraphicsScene())
        self.addWidget(self.image_edit_area)
        self.addWidget(self.images_nav)

    def load_image(self, image_path):
        self.image_edit_area.scene().clear()
        image = QPixmap(image_path)
        self.image_edit_area.scene().addPixmap(image)
        self.image_edit_area.scene().setSceneRect(
            self.image_edit_area.scene().itemsBoundingRect())
