import time

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow, QMenu, QAction, \
    QFileDialog, QWidget, \
    QDesktopWidget, QLabel, QHBoxLayout, QGraphicsTextItem

from custom_items import CustomQGraphicsTextItem
from images_panel import ImagesPanel
from settings_panel import SettingsPanel


class MainLayout(QHBoxLayout):

    def __init__(self, *args, **kwargs):
        super(MainLayout, self).__init__(*args, **kwargs)
        self.images_panel = ImagesPanel()
        self.addLayout(self.images_panel)
        self.settings_panel = SettingsPanel()
        self.addLayout(self.settings_panel)


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
        text_item.setTextInteractionFlags(Qt.NoTextInteraction)
        text_item.setFlags(QGraphicsTextItem.ItemIsSelectable |
                           QGraphicsTextItem.ItemIsMovable |
                           QGraphicsTextItem.ItemSendsScenePositionChanges |
                           QGraphicsTextItem.ItemIsFocusable)
        text_item.setParent(self.main_layout.settings_panel)
        self.main_layout.images_panel.image_edit_area.scene().addItem(
            text_item)
