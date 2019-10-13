import os
import time

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QMainWindow, QApplication, QMenu, QVBoxLayout, \
    QAction, QFileDialog, QWidget, \
    QListWidget, QListView, QListWidgetItem, QGraphicsView, QGraphicsScene, \
    QDesktopWidget, QLabel, QHBoxLayout, QProgressDialog, QGraphicsTextItem, \
    QGraphicsItem


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
        return QGraphicsItem.itemChange(self, change, value)


class ImagesNav(QListWidget):

    def __init__(self, *args, **kwargs):
        super(ImagesNav, self).__init__(*args, **kwargs)
        self.loaded_images = None
        self.setFlow(QListView.LeftToRight)
        self.setWrapping(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setViewMode(QListView.IconMode)
        self.setIconSize(QSize(128, 128))
        self.setResizeMode(QListView.Adjust)
        self.setFixedHeight(160)

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


class ImagesPanel(QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super(ImagesPanel, self).__init__(*args, **kwargs)
        self.images_nav = ImagesNav()
        self.images_nav.clicked.connect(lambda x: self.load_image(
            self.images_nav.currentItem().data(Qt.UserRole)))
        self.image_edit_area = QGraphicsView()
        self.image_edit_area.setScene(QGraphicsScene())
        self.addWidget(self.images_nav)
        self.addWidget(self.image_edit_area)

    def load_image(self, image_path):
        self.image_edit_area.scene().clear()
        image = QPixmap(image_path)
        self.image_edit_area.scene().addPixmap(image)
        self.image_edit_area.scene().setSceneRect(
            self.image_edit_area.scene().itemsBoundingRect())


class SettingsPanel(QVBoxLayout):

    def __init__(self, *args, **kwargs):
        super(SettingsPanel, self).__init__(*args, **kwargs)
        self.addWidget(QLabel("Test"))


class MainLayout(QHBoxLayout):

    def __init__(self, *args, **kwargs):
        super(MainLayout, self).__init__(*args, **kwargs)
        self.images_panel = ImagesPanel()
        self.addLayout(self.images_panel)
        self.settings_panel = SettingsPanel()
        self.addLayout(SettingsPanel())


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.main_layout = MainLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Watermark")
        self.status_message = QLabel()
        self.init_status_bar()
        self.init_menu()
        self.init_size()

    def init_menu(self):
        file_menu = QMenu("File")
        open_action = QAction("Open...", file_menu)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        self.menuBar().addMenu(file_menu)
        watermark_menu = QMenu("Watermark")
        add_text_action = QAction("Add text", watermark_menu)
        add_text_action.triggered.connect(self.add_text)
        watermark_menu.addAction(add_text_action)
        self.menuBar().addMenu(watermark_menu)

    def init_status_bar(self):
        self.statusBar()
        self.status_message.setText("Ready.")
        self.statusBar().addWidget(self.status_message)

    def init_size(self):
        size = QDesktopWidget().availableGeometry(self)
        size.setHeight(int(size.height() * 0.7))
        size.setWidth(int(size.width() * 0.7))
        self.setGeometry(size)

    def open_file(self):
        self.status_message.setText("Open file...")
        loaded_images = QFileDialog().getOpenFileNames(
            filter="Image files (*.bmp *.BMP *.gif "
                   "*.GIF *.jpeg *.JPEG *.jpg *.JPG "
                   "*.png *.PNG *.bpm *.BPM *.pgm "
                   "*.PGM *.ppm *.PPM *.xbm *.XBM "
                   "*.xpm *.XPM)")
        files_number = len(loaded_images[0])
        if files_number > 0:
            t1 = time.time()
            self.main_layout.images_panel.images_nav.loaded_images = \
                loaded_images[0]
            self.main_layout.images_panel.images_nav.update_navbar()
            self.status_message.setText(f"Loaded {files_number} files.")
            print(time.time() - t1)
        else:
            self.status_message.setText("Opening files canceled.")

    def add_text(self):
        text_item = CustomQGraphicsTextItem("Watermark")
        text_item.setFlags(QGraphicsTextItem.ItemIsSelectable |
                           QGraphicsTextItem.ItemIsMovable |
                           QGraphicsTextItem.ItemSendsScenePositionChanges)
        self.main_layout.images_panel.image_edit_area.scene().addItem(
            text_item)


if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()
