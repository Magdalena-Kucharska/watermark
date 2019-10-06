import os

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QApplication, QMenu, QVBoxLayout, \
    QAction, QFileDialog, QWidget, \
    QListWidget, QListView, QListWidgetItem, QGraphicsView, QGraphicsScene


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
        for image in self.loaded_images[0]:
            self.addItem(QListWidgetItem(QIcon(image), os.path.basename(
                image)))


class MainLayout(QVBoxLayout):

    def __init__(self, *args, **kwargs):
        super(MainLayout, self).__init__(*args, **kwargs)
        self.images_nav = ImagesNav()
        self.image_edit_area = QGraphicsView()
        self.image_edit_area.setScene(QGraphicsScene())
        self.addWidget(self.images_nav)
        self.addWidget(self.image_edit_area)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.main_layout = MainLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Watermark")
        self.statusBar().showMessage("Ready.")
        self.init_menu()

    def init_menu(self):
        file_menu = QMenu("File")
        open_action = QAction("Open...", file_menu)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        self.menuBar().addMenu(file_menu)

    def open_file(self):
        self.main_layout.images_nav.loaded_images = QFileDialog()\
            .getOpenFileNames(filter="Image files (*.bmp *.BMP *.gif "
                                     "*.GIF *.jpeg *.JPEG *.jpg *.JPG "
                                     "*.png *.PNG *.bpm *.BPM *.pgm "
                                     "*.PGM *.ppm *.PPM *.xbm *.XBM "
                                     "*.xpm *.XPM)")
        self.main_layout.images_nav.update_navbar()


if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()
