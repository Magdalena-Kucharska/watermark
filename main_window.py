import os
import re
import subprocess
import sys
from uuid import uuid4

import yaml
from PySide2.QtCore import Qt, QRectF, QRect
from PySide2.QtGui import QPixmap, QImage, QPainter, QKeySequence, QIcon, \
    QPen, QColor
from PySide2.QtWidgets import QMainWindow, QMenu, QAction, \
    QFileDialog, QWidget, \
    QDesktopWidget, QLabel, QHBoxLayout, QGraphicsView, \
    QGraphicsScene, QGraphicsPixmapItem, QInputDialog, QMessageBox, \
    QGraphicsDropShadowEffect, QDialog, QVBoxLayout, QComboBox, QPushButton, \
    QDialogButtonBox, QGroupBox, QLineEdit, QProgressDialog, QSlider, \
    QSpinBox, \
    QApplication
from slugify import slugify

import sidebar
from custom_items import CustomQGraphicsTextItem, CustomQGraphicsPixmapItem
from invisible_watermark import Invisible3DDCTBased


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
        self.sidebar.navigation.currentItemChanged.connect(
            lambda current, previous:
            self.load_image(current.data(Qt.UserRole)))

    def load_image(self, image_path, scene=None, for_user=True):
        if scene is None:
            scene = self.image_editor.scene()
        scene.clear()
        image = QPixmap(image_path)
        scene.addPixmap(image)
        scene.setSceneRect(image.rect())
        if for_user:
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
        self.action_quit = QAction("Exit Watermark", self.menu_file)
        self.action_quit.setShortcut(QKeySequence.Quit)
        self.menu_file.addAction(self.action_quit)

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
        self.action_decode = QAction("Decode invisible watermark from the "
                                     "current image...",
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

        self.action_load_preset = QAction("Load preset...", self.menu_presets)
        self.action_load_preset.setToolTip("This will load preset to the "
                                           "current image without saving, "
                                           "making it possible to edit the "
                                           "preset.")
        self.action_load_preset.setEnabled(False)
        self.menu_presets.setToolTipsVisible(True)
        self.menu_presets.addAction(self.action_load_preset)

        self.menu_watermark.addMenu(self.menu_visible)
        self.menu_watermark.addMenu(self.menu_invisible)
        self.menu_watermark.addMenu(self.menu_presets)

        self.menu_settings = QMenu("Settings")
        self.action_set_quality = QAction("Set quality of saved images",
                                          self.menu_settings)
        self.menu_settings.addAction(self.action_set_quality)

        self.menu_about = QMenu("About")
        self.action_about = QAction("About Watermark", self.menu_about)
        self.action_help = QAction("Help", self.menu_about)
        self.action_help.setShortcut(QKeySequence.HelpContents)
        self.menu_about.addAction(self.action_about)
        self.menu_about.addAction(self.action_help)


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


def save_file(scene, file_name, file_format=None, quality=-1):
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
            result = image.save(file_name,
                                format=file_format,
                                quality=quality)
        else:
            result = image.save(file_name, quality=quality)
        return not result
    except:
        return 1


def generate_unique_file_name(file_name, directory):
    existing_files = [file for file in os.listdir(directory) if
                      os.path.isfile(os.path.join(directory, file))]
    unique_name = file_name
    while unique_name in existing_files:
        unique_name = file_name
        unique_name_split = unique_name.split('.')
        unique_name = '.'.join(unique_name_split[:-1])
        unique_name += f"_{str(uuid4())[:5]}"
        unique_name += f".{unique_name_split[-1]}"
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
        self.central_widget = QWidget(parent=self)
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
        if not os.path.exists("presets"):
            os.mkdir("presets")
        if not os.path.exists("extracted watermarks"):
            os.mkdir("extracted watermarks")
        self.visible_saving_quality = -1
        self.visible_saving_format = ".jpg"
        self.invisible_saving_quality = 95
        self.invisible_saving_format = ".jpg"
        self.init_settings()

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
        self.menus.action_set_quality.triggered.connect(
            self.get_quality_setting)
        self.menus.action_encode.triggered.connect(
            self.get_invisible_encoding_settings)
        self.menus.action_decode.triggered.connect(
            self.get_invisible_decoding_settings)
        self.menus.action_load_preset.triggered.connect(lambda:
                                                        self.get_preset_name(
                                                            load_for_user=True))
        self.menuBar().addMenu(self.menus.menu_watermark)
        self.menuBar().addMenu(self.menus.menu_settings)
        self.menuBar().addMenu(self.menus.menu_about)

    def init_status_bar(self):
        self.statusBar().addPermanentWidget(self.item_pos)
        self.statusBar().addPermanentWidget(self.current_image_name)

    def init_size(self):
        size = QDesktopWidget().availableGeometry(self)
        size.setHeight(int(size.height() * 0.7))
        size.setWidth(int(size.width() * 0.7))
        self.setGeometry(size)

    def init_settings(self):
        if not os.path.isfile("settings.yaml"):
            self.save_settings()
        else:
            self.load_settings()

    def settings_to_dict(self):
        settings = {"visible watermarking":
                        {"saving quality": self.visible_saving_quality,
                         "saving format": self.visible_saving_format},
                    "invisible watermarking":
                        {"saving quality": self.invisible_saving_quality,
                         "saving format": self.invisible_saving_format}}
        return settings

    def settings_from_dict(self, settings_dict):
        self.visible_saving_quality = int(settings_dict["visible "
                                                        "watermarking"][
                                              "saving quality"])
        self.visible_saving_format = settings_dict["visible " \
                                                   "watermarking"][
            "saving format"]
        self.invisible_saving_quality = int(settings_dict["invisible "
                                                          "watermarking"][
                                                "saving quality"])
        self.invisible_saving_format = settings_dict["invisible " \
                                                     "watermarking"][
            "saving format"]

    def load_settings(self):
        with open("settings.yaml", "r") as settings_file:
            settings = yaml.load(settings_file, yaml.FullLoader)
        self.settings_from_dict(settings)

    def save_settings(self):
        settings = self.settings_to_dict()
        with open("settings.yaml", "w") as settings_file:
            yaml.dump(settings, settings_file, sort_keys=False)

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
            self.main_layout.sidebar.navigation.currentItemChanged.disconnect()
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
            self.main_layout.sidebar.navigation.currentItemChanged.connect(
                lambda current, previous:
                self.main_layout.load_image(current.data(Qt.UserRole)))
            self.main_layout.sidebar.navigation.setCurrentRow(0)
            self.main_layout.sidebar.log_text(f"Loaded {files_count} file(s).")
            self.menus.menu_visible.setEnabled(True)
            self.menus.menu_invisible.setEnabled(True)
            self.menus.action_apply_preset.setEnabled(True)
            self.menus.action_open_add.setEnabled(True)
            self.menus.action_save_as.setEnabled(True)
            self.menus.action_save_preset.setEnabled(True)
            self.menus.action_close.setEnabled(True)
            self.menus.action_load_preset.setEnabled(True)
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
            result = save_file(self.main_layout.image_editor.scene(),
                               file_name, file_format,
                               self.visible_saving_quality)
            if not result:
                self.main_layout.sidebar.log_text(f"File [{file_name}] "
                                                  f"successfully saved.")
            else:
                self.main_layout.sidebar.log_text(f"Error while saving file "
                                                  f"[{file_name}]. The file "
                                                  f"was NOT saved.", "red")
        else:
            self.main_layout.sidebar.log_text(f"Error while saving file "
                                              f"[{file_name}]. The file "
                                              f"was NOT saved.", "red")
        self.main_layout.sidebar.tabs.setCurrentIndex(1)

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
                        error = QMessageBox(QMessageBox.Warning,
                                            "Invalid name",
                                            "A preset with that name already "
                                            "exists. Would you like to "
                                            "overwrite?",
                                            QMessageBox.Ok |
                                            QMessageBox.Cancel)
                        error.setWindowIcon(self.icon)
                        result = error.exec()
                        if result == QMessageBox.Ok:
                            os.remove(os.path.join("presets",
                                                   f"{preset_name}.yaml"))
                            is_name_valid = True
                else:
                    error = QMessageBox(QMessageBox.Critical, "Invalid name",
                                        "Name can't be empty.",
                                        QMessageBox.Ok)
                    error.setWindowIcon(self.icon)
                    error.exec_()
            else:
                return
        if ok:
            try:
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
                self.main_layout.sidebar.log_text(f"Successfully saved "
                                                  f"preset ["
                                                  f"{preset_name}.yaml].")
            except:
                self.main_layout.sidebar.log_text(f"Error while saving "
                                                  f"preset ["
                                                  f"{preset_name}.yaml]. "
                                                  f"The preset was NOT "
                                                  f"saved.", "red")
            self.main_layout.sidebar.tabs.setCurrentIndex(1)

    def get_preset_name(self, load_for_user=False):
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
        if not load_for_user:
            choice_combo_box = QComboBox()
            choice_combo_box.addItems(
                ["to current image", "to all loaded images"])
            layout.addWidget(choice_combo_box)
            group_box = QGroupBox("Output location")
            group_box_layout = QVBoxLayout()
            path_display = QLineEdit()
            path_display.setText(os.path.dirname(os.path.realpath(__file__)))
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
        if len(presets) == 0:
            button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        layout.addWidget(button_box)
        dialog.setLayout(layout)
        if not load_for_user:
            dialog.accepted.connect(lambda: self.apply_preset(
                presets_combo_box.currentText(),
                choice_combo_box.currentText(),
                path_display.text()))
        else:
            dialog.accepted.connect(lambda: self.apply_preset_to_image(
                self.read_preset(presets_combo_box.currentText()),
                for_user=True))
        dialog.exec()

    def apply_preset_to_image(self, preset, image_path="", output_path="",
                              for_user=False):
        if for_user:
            scene = self.main_layout.image_editor.scene()
        else:
            scene = QGraphicsScene()
            self.main_layout.load_image(image_path, scene, for_user=for_user)
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
                scene.addItem(new_item)
            try:
                new_item.load_config(item)
            except Exception as e:
                self.main_layout.sidebar.log_text(f"Error while applying "
                                                  f"preset.\n"
                                                  f"(Exception: {e}.\n"
                                                  f"Stopping...", "red")
                return 1
        if not for_user:
            image_name = os.path.basename(image_path)
            image_name_split = image_name.split('.')
            image_name = '.'.join(
                image_name_split[:-1]) + self.visible_saving_format
            try:
                unique_name = generate_unique_file_name(image_name,
                                                        output_path)
            except:
                self.main_layout.sidebar.log_text(f"Ouptut directory ["
                                                  f"{output_path}] is "
                                                  f"invalid. "
                                                  f"Stopping...", "red")
                return 1
            save_path = os.path.join(output_path, unique_name)
            result = save_file(scene=scene,
                               file_name=save_path,
                               quality=self.visible_saving_quality)
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
        return 0

    def read_preset(self, preset_name):
        items = []
        with open(os.path.join("presets", preset_name), 'r') as preset_file:
            for item in yaml.load_all(preset_file, yaml.FullLoader):
                items.append(item)
        return items

    def apply_preset(self, preset_name, mode, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)
        self.main_layout.sidebar.log_text(f"Applying preset ["
                                          f"{preset_name}]...")
        items = self.read_preset(preset_name)
        if mode == "to all loaded images":
            progress = QProgressDialog(f"Applying preset [{preset_name}]...",
                                       "Cancel", 0,
                                       len(self.main_layout.sidebar.
                                           navigation.loaded_images), self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setWindowTitle("Watermark")
            progress.setWindowIcon(self.icon)
            result = 0
            for i, image in enumerate(
                    self.main_layout.sidebar.navigation.loaded_images):
                progress.setValue(i)
                if result or progress.wasCanceled():
                    break
                result = self.apply_preset_to_image(items, image, output_path)
            progress.setValue(
                len(self.main_layout.sidebar.navigation.loaded_images))
        else:
            dialog = QMessageBox(QMessageBox.Information, "Watermark",
                                 f"Applying preset [{preset_name}]...")
            dialog.setStandardButtons(QMessageBox.NoButton)
            dialog.setWindowFlags(Qt.WindowTitleHint)
            dialog.setWindowIcon(self.icon)
            dialog.open()
            QApplication.processEvents()
            self.apply_preset_to_image(items,
                                       self.main_layout.sidebar.navigation.
                                       currentItem().data(Qt.UserRole),
                                       output_path)
            dialog.close()
        self.main_layout.sidebar.log_text(f"Finished applying preset ["
                                          f"{preset_name}].")
        self.main_layout.sidebar.tabs.setCurrentIndex(1)

    def get_quality_setting(self):
        dialog = QDialog(self)
        dialog.setModal(True)
        dialog.setWindowIcon(self.icon)
        dialog.setWindowTitle("Set quality of saved images")
        dialog_layout = QVBoxLayout()
        visible_group = QGroupBox("Visible watermarking")
        visible_layout = QVBoxLayout()
        visible_quality_group = QGroupBox("Quality", visible_group)
        visible_quality_desc = QLabel("Specify 0 to obtain small compressed "
                                      "files, 100 for large uncompressed "
                                      "files, "
                                      "-1 for default behavior.")
        visible_quality_desc.setWordWrap(True)
        visible_quality_desc.setMinimumSize(visible_quality_desc.sizeHint())
        visible_quality_layout = QVBoxLayout()
        visible_quality_layout.addWidget(visible_quality_desc)
        visible_slider_layout = QHBoxLayout()
        visible_quality_slider = QSlider(Qt.Horizontal, dialog)
        visible_quality_slider.setTickPosition(QSlider.TicksBelow)
        visible_quality_slider.setRange(0, 100)
        visible_quality_slider.setSingleStep(10)
        visible_quality_slider.setValue(self.visible_saving_quality)
        visible_quality_value = QLabel(f"{self.visible_saving_quality}")
        visible_quality_slider. \
            valueChanged. \
            connect(lambda: visible_quality_value.
                    setText(f"{visible_quality_slider.value()}"))
        visible_slider_layout.addWidget(visible_quality_slider)
        visible_slider_layout.addWidget(visible_quality_value)
        visible_quality_layout.addLayout(visible_slider_layout)
        visible_reset_button = QPushButton("Reset to default")
        visible_reset_button.clicked.connect(lambda:
                                             (visible_quality_slider.setValue(
                                                 0),
                                              visible_quality_value.setText(
                                                  "-1")))
        visible_quality_layout.addWidget(visible_reset_button)
        visible_quality_group.setLayout(visible_quality_layout)
        visible_layout.addWidget(visible_quality_group)
        visible_format_group = QGroupBox("Image format", visible_group)
        visible_format_layout = QVBoxLayout()
        visible_format_desc = QLabel(
            "This setting is used when saving batches "
            "of files after applying a preset.")
        visible_format_desc.setWordWrap(True)
        visible_format_desc.setMinimumSize(visible_format_desc.sizeHint())
        visible_format_layout.addWidget(visible_format_desc)
        visible_formats_combo = QComboBox(dialog)
        visible_formats_combo.addItems([".bmp", ".jpg", ".jpeg", ".png",
                                        ".ppm", ".xbm", ".xpm"])
        visible_formats_combo.setCurrentText(self.visible_saving_format)
        visible_format_layout.addWidget(visible_formats_combo)
        visible_format_group.setLayout(visible_format_layout)
        visible_layout.addWidget(visible_format_group)
        visible_group.setLayout(visible_layout)
        dialog_layout.addWidget(visible_group)
        invisible_group = QGroupBox("Invisible watermarking")
        invisible_layout = QVBoxLayout()
        invisible_format_group = QGroupBox("Image format")
        invisible_format_layout = QVBoxLayout()
        invisible_formats_combo = QComboBox(dialog)
        invisible_formats_combo.addItems([".jpg", ".jpeg", ".png", ".bmp",
                                          ".tiff"])
        invisible_formats_combo.setCurrentText(self.invisible_saving_format)
        invisible_format_layout.addWidget(invisible_formats_combo)
        invisible_format_group.setLayout(invisible_format_layout)
        invisible_layout.addWidget(invisible_format_group)
        invisible_quality_group = QGroupBox("Quality")
        invisible_quality_layout = QVBoxLayout()
        invisible_quality_desc = QLabel("This setting is only used when "
                                        "selected format is .jpg/.jpeg. "
                                        "Select 1 for lowest quality, "
                                        "95 for best quality.")
        invisible_quality_desc.setWordWrap(True)
        invisible_quality_desc.setMinimumSize(
            invisible_quality_desc.sizeHint())
        invisible_quality_layout.addWidget(invisible_quality_desc)
        invisible_quality_slider_layout = QHBoxLayout()
        invisible_quality_slider = QSlider(Qt.Horizontal, dialog)
        invisible_quality_slider.setRange(1, 95)
        invisible_quality_slider.setValue(self.invisible_saving_quality)
        invisible_quality_slider.setTickPosition(QSlider.TicksBelow)
        invisible_quality_value = QLabel(f"{self.invisible_saving_quality}")
        invisible_quality_slider. \
            valueChanged.connect(
            lambda: invisible_quality_value.setText(
                f"{invisible_quality_slider.value()}"))
        invisible_quality_slider.setEnabled(
            invisible_formats_combo.currentText() in [
                ".jpg", ".jpeg"])
        invisible_formats_combo.currentTextChanged.connect(lambda current:
                                                           invisible_quality_slider.setEnabled(
                                                               current in [
                                                                   ".jpg",
                                                                   ".jpeg"]))
        invisible_quality_slider_layout.addWidget(invisible_quality_slider)
        invisible_quality_slider_layout.addWidget(invisible_quality_value)
        invisible_quality_layout.addLayout(invisible_quality_slider_layout)
        invisible_quality_group.setLayout(invisible_quality_layout)
        invisible_layout.addWidget(invisible_quality_group)
        invisible_group.setLayout(invisible_layout)
        dialog_layout.addWidget(invisible_group)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok |
                                   QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog_layout.addWidget(buttons)
        dialog.setLayout(dialog_layout)
        result = dialog.exec()
        self.main_layout.sidebar.log_text("Open quality settings...")
        if result == QDialog.Accepted:
            try:
                self.visible_saving_quality = int(visible_quality_value.text())
                self.visible_saving_format = \
                    visible_formats_combo.currentText()
                self.invisible_saving_quality = int(
                    invisible_quality_value.text())
                self.invisible_saving_format = \
                    invisible_formats_combo.currentText()
                self.save_settings()
                self.main_layout.sidebar.log_text(
                    "Quality setting successfully "
                    "saved.")
            except Exception as e:
                self.main_layout.sidebar.log_text(f"Error while saving "
                                                  f"quality settings:\n"
                                                  f"{e}.\n"
                                                  f"Settings were NOT saved.",
                                                  "red")
                self.main_layout.sidebar.tabs.setCurrentIndex(1)
                return
        else:
            self.main_layout.sidebar.log_text("Cancel setting quality.")

    def get_invisible_encoding_settings(self):
        dialog = QDialog()
        dialog.setModal(True)
        dialog.setWindowIcon(self.icon)
        dialog.setWindowTitle("Invisible watermarking settings")
        dialog_layout = QVBoxLayout()

        mode_combo = QComboBox(dialog)
        mode_combo.addItems(["Encode watermark in the current image",
                             "Encode watermark in all loaded images"])
        dialog_layout.addWidget(mode_combo)

        q_group = QGroupBox("Watermarking strength")
        q_layout = QVBoxLayout()
        q_desc = QLabel("Adjust the Q parameter. Bigger values mean more "
                        "robust watermark at the greater risk of making "
                        "noticeable changes to the cover image.")
        q_desc.setWordWrap(True)
        q_desc.setMinimumSize(q_desc.sizeHint())
        q_layout.addWidget(q_desc)
        q_input_layout = QHBoxLayout()
        q_input_layout.addWidget(QLabel("Q = "))
        q_input = QSpinBox()
        q_input.setRange(5, 60)
        q_input.setValue(60)
        q_input_layout.addWidget(q_input)
        q_layout.addLayout(q_input_layout)
        q_group.setLayout(q_layout)
        dialog_layout.addWidget(q_group)
        channel_group = QGroupBox("Channel")
        channel_layout = QVBoxLayout()
        channel_desc = QLabel("Set channel in which the watermark should be "
                              "encoded. Recommended are G or B.")
        channel_desc.setWordWrap(True)
        channel_desc.setMinimumSize(channel_desc.sizeHint())
        channel_layout.addWidget(channel_desc)
        channel_layout.addWidget(QLabel("R - Red, G - Green, B - Blue"))
        channel_combo = QComboBox(dialog)
        channel_combo.addItems(["R", "G", "B"])
        channel_combo.setCurrentText("B")
        channel_layout.addWidget(channel_combo)
        channel_group.setLayout(channel_layout)
        dialog_layout.addWidget(channel_group)
        output_dir_group = QGroupBox("Output directory")
        output_dir_group_layout = QVBoxLayout()
        output_dir_text = QLineEdit(os.path.dirname(os.path.realpath(
            __file__)))
        output_dir_button = QPushButton("Set output directory")
        output_dir_dialog = QFileDialog()
        output_dir_dialog.setFileMode(QFileDialog.Directory)
        output_dir_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        output_dir_button. \
            clicked. \
            connect(lambda: output_dir_text.
                    setText(os.path.normpath(output_dir_dialog.
                                             getExistingDirectory())))

        output_dir_group_layout.addWidget(output_dir_text)
        output_dir_group_layout.addWidget(output_dir_button)
        output_dir_group.setLayout(output_dir_group_layout)
        dialog_layout.addWidget(output_dir_group)

        watermark_group = QGroupBox("Image to encode")
        watermark_layout = QVBoxLayout()
        watermark_desc = QLabel("Image will be converted to grayscale and "
                                "resized according to the cover image's size.")
        watermark_desc.setWordWrap(True)
        watermark_desc.setMinimumSize(watermark_desc.sizeHint())
        watermark_dir_text = QLineEdit()
        watermark_dir_button = QPushButton("Choose image")
        watermark_dialog = QFileDialog(
            filter="Image files (*.bmp *.BMP *.jpeg "
                   "*.JPEG *.jpg *.JPG *.png *.PNG )")
        watermark_dir_button. \
            clicked. \
            connect(lambda: watermark_dir_text.
                    setText(os.path.normpath(watermark_dialog.
                                             getOpenFileName()[0])))
        watermark_layout.addWidget(watermark_desc)
        watermark_layout.addWidget(watermark_dir_text)
        watermark_layout.addWidget(watermark_dir_button)
        watermark_group.setLayout(watermark_layout)
        dialog_layout.addWidget(watermark_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setEnabled(False)
        output_dir_text.textChanged.connect(lambda text: buttons.button(
            QDialogButtonBox.Ok).setEnabled(bool(len(text)) and bool(len(
            watermark_dir_text.text()))))
        watermark_dir_text.textChanged.connect(lambda text: buttons.button(
            QDialogButtonBox.Ok).setEnabled(bool(len(text)) and bool(len(
            output_dir_text.text()))))
        dialog_layout.addWidget(buttons)
        dialog.setLayout(dialog_layout)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        self.main_layout.sidebar.log_text("Open invisible watermarking "
                                          "settings...")
        result = dialog.exec()
        if result == QDialog.Accepted:
            self.encode_invisible_watermark(q_input.value(),
                                            channel_combo.currentText(),
                                            mode_combo.currentText(),
                                            watermark_dir_text.text(),
                                            output_dir_text.text())

    def encode_invisible_watermark(self, Q, channel, mode,
                                   watermark_path, output_dir):
        invisible_watermark = Invisible3DDCTBased(Q,
                                                  channel.lower(),
                                                  self.invisible_saving_format,
                                                  self.invisible_saving_quality)
        self.main_layout.sidebar.log_text("Encoding invisible watermark "
                                          "started.")
        if mode == "Encode watermark in the current image":
            image_path = self.main_layout.sidebar. \
                navigation.currentItem().data(Qt.UserRole)
            dialog = QMessageBox(QMessageBox.Information, "Watermark",
                                 "Encoding. It may take a while, please "
                                 "wait...")
            try:
                dialog.setStandardButtons(QMessageBox.NoButton)
                dialog.setWindowFlags(Qt.WindowTitleHint)
                dialog.setWindowIcon(self.icon)
                dialog.open()
                QApplication.processEvents()
                invisible_watermark.encode(image_path, watermark_path,
                                           output_dir)
                dialog.close()
                self.main_layout.sidebar.log_text(f"Successfully encoded "
                                                  f"invisible watermark. "
                                                  f"Output image saved to ["
                                                  f"{output_dir}].")
            except Exception as e:
                self.main_layout.sidebar.log_text(f"Error while encoding "
                                                  f"invisible watermark:\n"
                                                  f"{e}. Output image was "
                                                  f"NOT saved. Stopping...",
                                                  "red")
                dialog.close()
                self.main_layout.sidebar.tabs.setCurrentIndex(1)
                return
        else:
            progress = QProgressDialog("Encoding watermark...", "Cancel", 0,
                                       len(self.main_layout.sidebar.
                                           navigation.loaded_images),
                                       self)
            try:
                progress.setWindowModality(Qt.WindowModal)
                progress.setWindowTitle("Watermark")
                progress.setWindowIcon(self.icon)
                for i, image in enumerate(self.main_layout.sidebar.
                                                  navigation.loaded_images):
                    progress.setValue(i)
                    if progress.wasCanceled():
                        self.main_layout.sidebar.log_text("Encoding "
                                                          "watermark "
                                                          "canceled.")
                        self.main_layout.sidebar.tabs.setCurrentIndex(1)
                        return
                    invisible_watermark.encode(image, watermark_path,
                                               output_dir)
                    image_name = os.path.basename(image)
                    self.main_layout.sidebar.log_text(f"{image_name}\n"
                                                      f"Successfully encoded.")
                progress.setValue(len(self.main_layout.sidebar.navigation.
                                      loaded_images))
            except Exception as e:
                self.main_layout.sidebar.log_text(f"Error while encoding:\n"
                                                  f"{e}.\n"
                                                  f"Stopping...", "red")
                progress.setValue(len(self.main_layout.sidebar.navigation.
                                      loaded_images))
                self.main_layout.sidebar.tabs.setCurrentIndex(1)
                return
        self.main_layout.sidebar.log_text("Encoding watermark finished.")
        self.main_layout.sidebar.tabs.setCurrentIndex(1)

    def get_invisible_decoding_settings(self):
        dialog = QDialog()
        dialog.setModal(True)
        dialog.setWindowIcon(self.icon)
        dialog.setWindowTitle("Invisible watermark decoding settings")
        dialog_layout = QVBoxLayout()
        settings_group = QGroupBox("Watermarking settings")
        settings_layout = QVBoxLayout()
        settings_desc = QLabel("Please specify what settings were used to "
                               "encode the watermark.")
        settings_desc.setWordWrap(True)
        settings_desc.setMinimumSize(settings_desc.sizeHint())
        settings_layout.addWidget(settings_desc)
        q_layout = QHBoxLayout()
        q_layout.addWidget(QLabel("Q = "))
        q_input = QSpinBox()
        q_input.setRange(5, 60)
        q_input.setValue(60)
        q_layout.addWidget(q_input)
        settings_layout.addLayout(q_layout)
        channel_layout = QHBoxLayout()
        channel_layout.addWidget(QLabel("Channel"))
        channel_combo = QComboBox()
        channel_combo.addItems(["R", "G", "B"])
        channel_combo.setCurrentText("B")
        channel_layout.addWidget(channel_combo)
        settings_layout.addLayout(channel_layout)
        settings_group.setLayout(settings_layout)
        dialog_layout.addWidget(settings_group)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok |
                                   QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        dialog_layout.addWidget(buttons)
        dialog.setLayout(dialog_layout)
        result = dialog.exec()
        if result == QDialog.Accepted:
            self.decode_invisible_watermark(q_input.value(),
                                            channel_combo.currentText(),
                                            self.main_layout.sidebar.
                                            navigation.currentItem().
                                            data(Qt.UserRole))

    def decode_invisible_watermark(self, Q, channel, image_path):
        invisible_watermark = Invisible3DDCTBased(Q,
                                                  channel.lower(),
                                                  self.invisible_saving_format,
                                                  self.invisible_saving_quality)
        self.main_layout.sidebar.log_text("Decoding invisible watermark "
                                          "started.")
        dialog = QMessageBox(QMessageBox.Information, "Watermark",
                             "Decoding. It may take a while, please "
                             "wait...")
        try:
            dialog.setStandardButtons(QMessageBox.NoButton)
            dialog.setWindowFlags(Qt.WindowTitleHint)
            dialog.setWindowIcon(self.icon)
            dialog.open()
            QApplication.processEvents()
            invisible_watermark.decode(image_path, "extracted watermarks")
            dialog.close()
            self.main_layout.sidebar.log_text("Watermark successfully "
                                              "decoded. Image has been saved "
                                              "to [<application directory>\\"
                                              "extracted watermarks].")
            self.main_layout.sidebar.tabs.setCurrentIndex(1)
        except Exception as e:
            self.main_layout.sidebar.log_text(f"Error while decoding "
                                              f"watermark:\n"
                                              f"{e}.\n"
                                              f"Watermark was NOT decoded.",
                                              "red")
            dialog.close()
            self.main_layout.sidebar.tabs.setCurrentIndex(1)
            return
