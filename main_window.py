import os
import re
import subprocess
import sys

import yaml
from PySide2.QtCore import Qt, QRectF, QRect
from PySide2.QtGui import QPixmap, QImage, QPainter, QKeySequence, QIcon, \
    QPen, QColor
from PySide2.QtWidgets import QMainWindow, QMenu, QAction, \
    QFileDialog, QWidget, \
    QDesktopWidget, QLabel, QHBoxLayout, QGraphicsView, \
    QGraphicsScene, QGraphicsPixmapItem, QInputDialog, QMessageBox, \
    QGraphicsDropShadowEffect, QDialog, QVBoxLayout, QComboBox, QPushButton, \
    QDialogButtonBox, QGroupBox, QLineEdit
from slugify import slugify

import sidebar
from custom_items import CustomQGraphicsTextItem, CustomQGraphicsPixmapItem


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
        self.sidebar = sidebar.Sidebar()
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
        self.parent().parent().current_image_name.setText(os.path.basename(
            image_path))


class Menus:

    def __init__(self):
        self.menu_file = QMenu("File")
        self.action_open = QAction("Open...", self.menu_file)
        self.action_open.setShortcut(QKeySequence.Open)
        self.menu_file.addAction(self.action_open)
        self.action_open_add = QAction("Add...", self.menu_file)
        self.action_open_add.setShortcut(QKeySequence(Qt.CTRL + Qt.SHIFT +
                                                      Qt.Key_O))
        self.action_open_add.setEnabled(False)
        self.menu_file.addAction(self.action_open_add)
        self.action_save_as = QAction("Save as...", self.menu_file)
        self.action_save_as.setShortcut(QKeySequence.Save)
        self.action_save_as.setEnabled(False)
        self.menu_file.addAction(self.action_save_as)
        self.action_close = QAction("Close", self.menu_file)
        self.action_close.setShortcut(QKeySequence.Close)
        self.action_close.setEnabled(False)
        self.menu_file.addAction(self.action_close)

        self.menu_watermark = QMenu("Watermarking")

        self.menu_visible = QMenu("Visible")

        self.action_add_text = QAction("Add text", self.menu_visible)
        self.menu_visible.addAction(self.action_add_text)
        self.action_add_image = QAction("Add image...", self.menu_visible)
        self.menu_visible.addAction(self.action_add_image)

        self.menu_visible.setEnabled(False)

        self.menu_invisible = QMenu("Invisible")
        self.action_encode = QAction("Encode invisible watermark...",
                                     self.menu_invisible)
        self.action_decode = QAction("Decode invisible watermark...",
                                     self.menu_invisible)
        self.menu_invisible.addAction(self.action_encode)
        self.menu_invisible.addAction(self.action_decode)
        self.menu_invisible.setEnabled(False)

        self.menu_presets = QMenu("Presets")

        self.action_save_preset = QAction("Save current watermark as "
                                          "preset...", self.menu_presets)
        self.action_save_preset.setEnabled(False)
        self.menu_presets.addAction(self.action_save_preset)
        self.action_manage_presets = QAction("Open presets directory",
                                             self.menu_presets)
        self.menu_presets.addAction(self.action_manage_presets)

        self.action_apply_preset = QAction("Apply preset...",
                                           self.menu_presets)
        self.menu_presets.addAction(self.action_apply_preset)
        self.action_apply_preset.setEnabled(False)

        self.menu_watermark.addMenu(self.menu_visible)
        self.menu_watermark.addMenu(self.menu_invisible)
        self.menu_watermark.addMenu(self.menu_presets)


def is_preset_name_valid(name):
    path = os.path.join("presets")
    if os.path.exists(path):
        presets = [file for file in os.listdir(path) if os.path.isfile(
            os.path.join(path, file))]
        for preset in presets:
            if preset.lower() == f"{name.lower()}.yaml":
                return False
    else:
        os.mkdir("presets")
    return True


def save_file(scene, file_name, file_format=None):
    try:
        scene.clearSelection()
        w = scene.width()
        h = scene.height()
        target = QRectF(0, 0, w, h)
        image = QImage(w, h, QImage.Format_A2BGR30_Premultiplied)
        painter = QPainter()
        painter.begin(image)
        scene.render(painter, target)
        painter.end()
        save_dir = os.path.dirname(file_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)
        if file_format:
            image.save(file_name,
                       format=file_format)
        else:
            image.save(file_name)
        return 0
    except:
        return 1


def generate_unique_file_name(file_name, directory):
    existing_files = [file for file in os.listdir(directory) if
                      os.path.isfile(os.path.join(directory, file))]
    unique_name = file_name
    count = 1
    while unique_name in existing_files:
        unique_name_split = unique_name.split('.')
        unique_name = '.'.join(unique_name_split[:-1]) + f" ({count})"
        unique_name += f".{unique_name_split[-1]}"
        count += 1
    return unique_name


def open_folder(path):
    if sys.platform == "darwin":
        subprocess.Popen(["open", "--", path])
    elif sys.platform == "linux2":
        subprocess.Popen(["xdg-open", "--", path])
    elif sys.platform == "win32":
        subprocess.Popen(["explorer", path])


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.icon = QIcon("logo.png")
        self.menus = Menus()
        self.main_layout = MainLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Watermark")
        self.item_pos = QLabel()
        self.item_pos.setToolTip("You can adjust item's position with greater "
                                 "accuracy by using arrow keys.")
        self.current_image_name = QLabel()
        self.init_status_bar()
        self.init_menu()
        self.init_size()
        self.setWindowIcon(self.icon)
        self.main_layout.sidebar.log_text("Ready.")

    def init_menu(self):
        self.menus.action_open.triggered.connect(self.open_file)
        self.menus.action_open_add.triggered.connect(lambda: self.open_file(
            add=True))
        self.menuBar().addMenu(self.menus.menu_file)
        self.menus.action_add_text.triggered.connect(self.add_text)
        self.menus.action_add_image.triggered.connect(self.add_image)
        self.menus.action_save_as.triggered.connect(self.get_save_file_name)
        self.menus.action_save_preset.triggered.connect(self.save_preset)
        self.menus.action_apply_preset.triggered.connect(self.get_preset_name)
        presets_path = os.path.join(os.path.dirname(os.path.realpath(
            __file__)), "presets")
        self.menus.action_manage_presets.triggered.connect(lambda:
                                                           open_folder(
                                                               presets_path))
        self.menus.action_close.triggered.connect(
            self.main_layout.sidebar.navigation.remove_selected_item)
        self.menuBar().addMenu(self.menus.menu_watermark)

    def init_status_bar(self):
        self.statusBar().addPermanentWidget(self.item_pos)
        self.statusBar().addPermanentWidget(self.current_image_name)

    def init_size(self):
        size = QDesktopWidget().availableGeometry(self)
        size.setHeight(int(size.height() * 0.7))
        size.setWidth(int(size.width() * 0.7))
        self.setGeometry(size)

    def open_file(self, add=False):
        self.main_layout.image_editor.scene().clearSelection()
        self.main_layout.sidebar.log_text("Open file(s)...")
        loaded_images = QFileDialog.getOpenFileNames(
            filter="Image files (*.bmp *.BMP *.gif "
                   "*.GIF *.jpeg *.JPEG *.jpg *.JPG "
                   "*.png *.PNG *.bpm *.BPM *.pgm "
                   "*.PGM *.ppm *.PPM *.xbm *.XBM "
                   "*.xpm *.XPM)")
        files_count = len(loaded_images[0])
        if files_count > 0:
            loaded_images_normalized = [os.path.normpath(image) for image in
                                        loaded_images[0]]
            if add:
                for image in loaded_images_normalized:
                    if image not in \
                            self.main_layout.sidebar.navigation.loaded_images:
                        self.main_layout.sidebar.navigation.loaded_images \
                            .append(image)
            else:
                self.main_layout.sidebar.navigation.loaded_images = \
                    loaded_images_normalized
            self.main_layout.sidebar.navigation.update_navbar()
            if not add:
                self.main_layout.sidebar.navigation.setCurrentRow(0)
                self.main_layout.load_image(loaded_images_normalized[0])
            self.main_layout.sidebar.log_text(f"Loaded {files_count} file(s).")
            self.menus.menu_visible.setEnabled(True)
            self.menus.menu_invisible.setEnabled(True)
            self.menus.action_apply_preset.setEnabled(True)
            self.menus.action_open_add.setEnabled(True)
            self.menus.action_save_as.setEnabled(True)
            self.menus.action_save_preset.setEnabled(True)
            self.menus.action_close.setEnabled(True)
        else:
            self.main_layout.sidebar.log_text("Opening files canceled.")

    def add_text(self):
        text_item = CustomQGraphicsTextItem("Watermark")
        text_item.setParent(self.main_layout.sidebar)
        self.main_layout.image_editor.scene().addItem(text_item)
        self.main_layout.image_editor.scene().clearSelection()
        text_item.setSelected(True)

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
            image_item.path = os.path.normpath(image[0])
            self.main_layout.image_editor.scene().addItem(image_item)
            self.main_layout.image_editor.scene().clearSelection()
            image_item.setSelected(True)

    def get_save_file_name(self):
        (file_name, file_format) = \
            QFileDialog.getSaveFileName(self,
                                        "Save image as...",
                                        filter="Windows Bitmap (*.bmp);;"
                                               "Joint Photographic Experts "
                                               "Group (*.jpg *jpeg);;"
                                               "Portable Network "
                                               "Graphics (*.png);;"
                                               "Portable Pixmap (*.ppm);;"
                                               "X11 Bitmap (*.xbm);;"
                                               "X11 Pixmap (*.xpm)")
        if file_name:
            save_file(self.main_layout.image_editor.scene(), file_name,
                      file_format)

    def save_preset(self):
        dialog = QInputDialog()
        dialog.setWindowIcon(self.icon)
        is_name_valid = False
        ok = False
        preset_name = ""
        while not is_name_valid:
            (preset_name, ok) = dialog.getText(self, "Save preset as...",
                                               "Preset name:")
            if ok:
                if len(preset_name) > 0:
                    is_name_valid = is_preset_name_valid(preset_name)
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
                    items_list.append(item.get_config())
            preset_dir = os.path.join("presets",
                                      f"{slugify(preset_name)}.yaml")
            preset_file = open(preset_dir, "w")
            yaml.dump_all(items_list, preset_file, sort_keys=False)
            preset_file.close()

    def get_preset_name(self):
        presets = []
        for file in os.listdir("presets"):
            if os.path.isfile(os.path.join("presets", file)) and re.match(
                    r"[\s\S]+.yaml", file):
                presets.append(file)
        dialog = QDialog()
        dialog.setWindowTitle("Apply preset")
        dialog.setModal(True)
        dialog.setWindowIcon(self.icon)
        layout = QVBoxLayout()
        presets_combo_box = QComboBox()
        presets_combo_box.addItems(presets)
        layout.addWidget(presets_combo_box)
        choice_combo_box = QComboBox()
        choice_combo_box.addItems(["to current image", "to all loaded images"])
        layout.addWidget(choice_combo_box)
        group_box = QGroupBox("Output location")
        group_box_layout = QVBoxLayout()
        path_display = QLineEdit()
        group_box_layout.addWidget(path_display)
        path_button = QPushButton("Set directory")
        path_input = QFileDialog()
        path_input.setFileMode(QFileDialog.Directory)
        path_input.setOption(QFileDialog.ShowDirsOnly, True)
        path_button.clicked.connect(lambda:
                                    path_display.setText(
                                        os.path.normpath(
                                            path_input.getExistingDirectory())))
        group_box_layout.addWidget(path_button)
        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok |
                                      QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        dialog.accepted.connect(lambda: self.apply_preset(
            presets_combo_box.currentText(), choice_combo_box.currentText(),
            path_display.text()))
        dialog.exec_()

    def apply_preset_to_image(self, preset, image_path, output_path):
        self.main_layout.load_image(image_path)
        new_item = None
        for item in preset:
            if item["item_type"] == "text":
                new_item = CustomQGraphicsTextItem()
                new_item.setParent(self.main_layout.sidebar)
            else:
                if os.path.exists(item["image_path"]):
                    new_item = CustomQGraphicsPixmapItem(item["image_path"])
                    new_item.parent = self.main_layout.sidebar
                    new_item.path = item["image_path"]
                else:
                    self.main_layout. \
                        sidebar.log_text(f"Error while retrieving watermark "
                                         f"[{item['image_path']}]. "
                                         f"Stopping...", "red")
                    return 1
            if new_item:
                self.main_layout.image_editor.scene().addItem(new_item)
            try:
                new_item.load_config(item)
            except Exception as e:
                self.main_layout.sidebar.log_text(f"Error while applying "
                                                  f"preset.\n"
                                                  f"(Exception: {e}.\n"
                                                  f"Stopping...", "red")
                return 1
        image_name = os.path.basename(image_path)
        unique_name = generate_unique_file_name(image_name, output_path)
        save_path = os.path.join(output_path, unique_name)
        result = save_file(scene=self.main_layout.image_editor.scene(),
                           file_name=save_path)
        if result:
            self.main_layout.sidebar.log_text(f"{image_name}\n"
                                              f"Error while saving to "
                                              f"specified "
                                              f"directory: [{save_path}]. "
                                              f"File "
                                              f"[{unique_name}] was "
                                              f"NOT saved. Stopping ...",
                                              "red")
            return 1
        else:
            self.main_layout.sidebar.log_text(f"{image_name}\n"
                                              f"File "
                                              f"[{unique_name}] saved to"
                                              f" [{output_path}].")
            return 0

    def apply_preset(self, preset_name, mode, output_path):
        self.main_layout.sidebar.log_text(f"Applying preset ["
                                          f"{preset_name}]...")
        items = []
        with open(os.path.join("presets", preset_name), 'r') as preset_file:
            for item in yaml.load_all(preset_file, yaml.FullLoader):
                items.append(item)
        if mode == "to all loaded images":
            result = 0
            for image in self.main_layout.sidebar.navigation.loaded_images:
                if result:
                    break
                result = self.apply_preset_to_image(items, image, output_path)
        else:
            self.apply_preset_to_image(items,
                                       self.main_layout.sidebar.navigation.
                                       currentItem().data(Qt.UserRole),
                                       output_path)
        self.main_layout.sidebar.log_text(f"Finished applying preset ["
                                          f"{preset_name}].")
        self.main_layout.sidebar.tabs.setCurrentIndex(1)
