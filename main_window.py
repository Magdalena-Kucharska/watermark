import os

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QApplication, QMenu, QVBoxLayout, \
    QAction, QFileDialog, QWidget, \
    QListWidget, QListView, QListWidgetItem, QGraphicsView, QGraphicsScene, \
    QDesktopWidget, QLabel, QHBoxLayout


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
        self.setFixedHeight(180)

    def update_navbar(self):
        self.clear()
        for image in self.loaded_images:
            self.addItem(QListWidgetItem(QIcon(image), os.path.basename(
                image)))


class ImagesPanel(QVBoxLayout):
    def __init__(self, *args, **kwargs):
        super(ImagesPanel, self).__init__(*args, **kwargs)
        self.images_nav = ImagesNav()
        self.image_edit_area = QGraphicsView()
        self.image_edit_area.setScene(QGraphicsScene())
        self.addWidget(self.images_nav)
        self.addWidget(self.image_edit_area)


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
            self.main_layout.images_panel.images_nav.loaded_images = \
                loaded_images[0]
            self.main_layout.images_panel.images_nav.update_navbar()
            self.status_message.setText(f"Loaded {files_number} files.")
        else:
            self.status_message.setText("Opening files canceled.")


if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()
