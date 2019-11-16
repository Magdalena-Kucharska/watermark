import os
from os import listdir
from os.path import isfile

import yaml
from PySide2.QtCore import Qt, QItemSelectionModel, QRectF, QRect
from PySide2.QtGui import QPixmap, QImage, QPainter, QKeySequence, QIcon, \
    QPen, QColor
from PySide2.QtWidgets import QMainWindow, QMenu, QAction, \
    QFileDialog, QWidget, \
    QDesktopWidget, QLabel, QHBoxLayout, QGraphicsTextItem, QGraphicsView, \
    QGraphicsScene, QGraphicsPixmapItem, QInputDialog, QMessageBox, \
    QGraphicsDropShadowEffect
from slugify import slugify

from custom_items import CustomQGraphicsTextItem, CustomQGraphicsPixmapItem
from sidebar import Sidebar


class MainLayout(QHBoxLayout):

    def __init__(self, *args, **kwargs):
        super(MainLayout, self).__init__(*args, **kwargs)
        self.image_editor = QGraphicsView()
        self.image_editor.setScene(QGraphicsScene())
        logo = QGraphicsPixmapItem("logo.png")
        drop_shadow = QGraphicsDropShadowEffect()
        drop_shadow.setColor(QColor(63, 63, 63, 90))
        drop_shadow.setBlurRadius(20.)
        logo.setGraphicsEffect(drop_shadow)
        self.image_editor.scene().addItem(logo)
        self.addWidget(self.image_editor)
        self.sidebar = Sidebar()
        self.sidebar. \
            navigation. \
            itemSelectionChanged.connect(lambda:
                                         self.load_image(
                                             self.sidebar.
                                                 navigation.
                                                 currentItem().
                                                 data(Qt.UserRole)))
        self.addWidget(self.sidebar)

    def load_image(self, image_path):
        self.image_editor.scene().clear()
        image = QPixmap(image_path)
        self.image_editor.scene().addPixmap(image)
        self.image_editor.scene().setSceneRect(image.rect())
        pen = QPen()
        rect = QRect(0 - pen.width(),
                     0 - pen.width(),
                     image.rect().width() + pen.width(),
                     image.rect().height() + pen.width())
        self.image_editor.scene().addRect(rect, pen)


class Menus:

    def __init__(self):
        self.menu_file = QMenu("File")
        self.action_open = QAction("Open...", self.menu_file)
        self.action_open.setShortcut(QKeySequence.Open)
        self.menu_file.addAction(self.action_open)
        self.action_open_add = QAction("Add...", self.menu_file)
        self.action_open_add.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT + \
                                                      Qt.Key_O))
        self.action_open_add.setEnabled(False)
        self.menu_file.addAction(self.action_open_add)
        self.action_save_as = QAction("Save as...")
        self.action_save_as.setShortcut(QKeySequence.Save)
        self.action_save_as.setEnabled(False)
        self.menu_file.addAction(self.action_save_as)

        self.menu_watermark = QMenu("Watermark")

        self.menu_visible = QMenu("Visible")

        self.action_add_text = QAction("Add text", self.menu_visible)
        self.menu_visible.addAction(self.action_add_text)
        self.action_add_image = QAction("Add image", self.menu_visible)
        self.menu_visible.addAction(self.action_add_image)

        self.menu_visible.setEnabled(False)

        self.menu_invisible = QMenu("Invisible")
        self.action_encode = QAction("Encode invisible watermark",
                                     self.menu_invisible)
        self.action_decode = QAction("Decode invisible watermark",
                                     self.menu_invisible)
        self.menu_invisible.addAction(self.action_encode)
        self.menu_invisible.addAction(self.action_decode)
        self.menu_invisible.setEnabled(False)

        self.menu_presets = QMenu("Presets")

        self.action_save_preset = QAction("Save current watermark as "
                                          "preset", self.menu_presets)
        self.action_save_preset.setEnabled(False)
        self.menu_presets.addAction(self.action_save_preset)
        self.action_manage_presets = QAction("Manage presets",
                                             self.menu_presets)
        self.menu_presets.addAction(self.action_manage_presets)

        self.menu_apply_preset = QMenu("Apply preset")
        self.action_apply_preset_current = QAction("To current image",
                                                   self.menu_apply_preset)
        self.menu_apply_preset.addAction(self.action_apply_preset_current)
        self.menu_presets.addMenu(self.menu_apply_preset)
        self.action_apply_preset_all = QAction("To all loaded "
                                               "images",
                                               self.menu_apply_preset)
        self.menu_apply_preset.addAction(self.action_apply_preset_all)
        self.menu_apply_preset.setEnabled(False)

        self.menu_watermark.addMenu(self.menu_visible)
        self.menu_watermark.addMenu(self.menu_invisible)
        self.menu_watermark.addMenu(self.menu_presets)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.menus = Menus()
        self.main_layout = MainLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Watermark")
        self.status_message = QLabel()
        self.item_pos = QLabel()
        self.init_status_bar()
        self.init_menu()
        self.init_size()
        self.setWindowIcon(QIcon("logo.png"))

    def init_menu(self):
        self.menus.action_open.triggered.connect(self.open_file)
        self.menus.action_open_add.triggered.connect(lambda: self.open_file(
            add=True))
        self.menuBar().addMenu(self.menus.menu_file)
        self.menus.action_add_text.triggered.connect(self.add_text)
        self.menus.action_add_image.triggered.connect(self.add_image)
        self.menus.action_save_as.triggered.connect(self.save_file)
        self.menus.action_save_preset.triggered.connect(self.save_preset)
        self.menuBar().addMenu(self.menus.menu_watermark)

    def init_status_bar(self):
        self.statusBar()
        self.status_message.setText("Ready.")
        self.statusBar().addWidget(self.status_message)
        self.statusBar().addWidget(self.item_pos)

    def init_size(self):
        size = QDesktopWidget().availableGeometry(self)
        size.setHeight(int(size.height() * 0.7))
        size.setWidth(int(size.width() * 0.7))
        self.setGeometry(size)

    def open_file(self, add=False):
        self.status_message.setText("Open file...")
        loaded_images = QFileDialog().getOpenFileNames(
            filter="Image files (*.bmp *.BMP *.gif "
                   "*.GIF *.jpeg *.JPEG *.jpg *.JPG "
                   "*.png *.PNG *.bpm *.BPM *.pgm "
                   "*.PGM *.ppm *.PPM *.xbm *.XBM "
                   "*.xpm *.XPM)")
        files_count = len(loaded_images[0])
        if files_count > 0:
            if add:
                for image in loaded_images[0]:
                    if image not in \
                            self.main_layout.sidebar.navigation.loaded_images:
                        self.main_layout.sidebar.navigation.loaded_images \
                            .append(image)
            else:
                self.main_layout.sidebar.navigation.loaded_images = \
                    loaded_images[0]
            self.main_layout.sidebar.navigation.itemSelectionChanged \
                .disconnect()
            self.main_layout.sidebar.navigation.update_navbar()
            self.status_message.setText(f"Loaded {files_count} files.")
            self.menus.menu_visible.setEnabled(True)
            self.menus.menu_invisible.setEnabled(True)
            self.menus.menu_apply_preset.setEnabled(True)
            self.menus.action_open_add.setEnabled(True)
            self.menus.action_save_as.setEnabled(True)
            self.menus.action_save_preset.setEnabled(True)
            self.main_layout.sidebar.navigation.itemSelectionChanged \
                .connect(lambda:
                         self.main_layout.load_image(
                             self.main_layout.sidebar.navigation.currentItem().data(
                                 Qt.UserRole)))
            self.main_layout.sidebar.navigation.setCurrentRow(0,
                                                              QItemSelectionModel.SelectCurrent)
        else:
            self.status_message.setText("Opening files canceled.")

    def add_text(self):
        text_item = CustomQGraphicsTextItem("Watermark")
        text_item.setTextInteractionFlags(Qt.NoTextInteraction)
        text_item.setFlags(QGraphicsTextItem.ItemIsSelectable |
                           QGraphicsTextItem.ItemIsMovable |
                           QGraphicsTextItem.ItemSendsScenePositionChanges |
                           QGraphicsTextItem.ItemIsFocusable)
        text_item.setParent(self.main_layout.sidebar)
        text_item.setTransformOriginPoint(text_item.boundingRect().width() / 2,
                                          text_item.boundingRect().height()
                                          / 2)
        self.main_layout.image_editor.scene().addItem(text_item)

    def add_image(self):
        image = QFileDialog.getOpenFileName(
            filter="Image files (*.bmp *.BMP *.gif "
                   "*.GIF *.jpeg *.JPEG *.jpg *.JPG "
                   "*.png *.PNG *.bpm *.BPM *.pgm "
                   "*.PGM *.ppm *.PPM *.xbm *.XBM "
                   "*.xpm *.XPM)")
        if image:
            image_item = CustomQGraphicsPixmapItem(image[0])
            image_item.parent = self.main_layout.sidebar
            image_item.path = image[0]
            image_item.setFlags(QGraphicsPixmapItem.ItemIsFocusable |
                                QGraphicsPixmapItem.ItemIsSelectable |
                                QGraphicsPixmapItem.ItemIsMovable |
                                QGraphicsPixmapItem.ItemSendsScenePositionChanges)
            image_item.setTransformOriginPoint(image_item.boundingRect().width(

            ) / 2,
                                               image_item.boundingRect().height() / 2)
            self.main_layout.image_editor.scene().addItem(image_item)

    def save_file(self):
        file_name = QFileDialog.getSaveFileName(self, "Save image as...",
                                                filter="Windows Bitmap ("
                                                       "*.bmp);;"
                                                       "Joint Photographic "
                                                       "Experts Group (*.jpg "
                                                       "*jpeg);;"
                                                       "Portable Network "
                                                       "Graphics (*.png);;"
                                                       "Portable Pixmap ("
                                                       "*.ppm);;"
                                                       "X11 Bitmap (*.xbm);;"
                                                       "X11 Pixmap (*.xpm)")
        if file_name[0]:
            self.main_layout.image_editor.scene().clearSelection()
            w = self.main_layout.image_editor.scene().width()
            h = self.main_layout.image_editor.scene().height()
            target = QRectF(0, 0, w, h)
            image = QImage(w, h, QImage.Format_A2BGR30_Premultiplied)
            painter = QPainter()
            painter.begin(image)
            self.main_layout.image_editor.scene().render(painter, target)
            painter.end()
            image.save(file_name[0], format=file_name[1])

    @staticmethod
    def is_preset_name_valid(name):
        path = os.path.join("presets")
        if os.path.exists(path):
            presets = [file for file in listdir(path) if isfile(
                os.path.join(path, file))]
            for preset in presets:
                if preset.lower() == f"{name.lower()}.yaml":
                    return False
        else:
            os.mkdir("presets")
        return True

    def save_preset(self):
        dialog = QInputDialog()
        is_name_valid = False
        ok = False
        preset_name = ""
        while not is_name_valid:
            (preset_name, ok) = dialog.getText(self, "Save preset as...",
                                               "Preset name:")
            if ok:
                if len(preset_name) > 0:
                    is_name_valid = self.is_preset_name_valid(preset_name)
                    if not is_name_valid:
                        error = QMessageBox(QMessageBox.Critical,
                                            "Invalid name",
                                            "A preset with that name already "
                                            "exists.",
                                            QMessageBox.Ok)
                        error.exec_()
                else:
                    error = QMessageBox(QMessageBox.Critical, "Invalid name",
                                        "Name can't be empty.",
                                        QMessageBox.Ok)
                    error.exec_()
            else:
                ok = False
                return
        if ok:
            scene_items = self.main_layout.image_editor.scene().items()
            items_list = []
            for item in scene_items:
                if type(item) == CustomQGraphicsTextItem or type(
                        item) == CustomQGraphicsPixmapItem:
                    items_list.append(item.get_info())
            preset_dir = os.path.join("presets",
                                      f"{slugify(preset_name)}.yaml")
            preset_file = open(preset_dir, "w")
            yaml.dump_all(items_list, preset_file, sort_keys=False)
            preset_file.close()
