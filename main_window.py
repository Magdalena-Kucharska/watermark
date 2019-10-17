import os
import time

from PySide2.QtCore import Qt, QSize, QEvent
from PySide2.QtGui import QIcon, QPixmap, QFont
from PySide2.QtWidgets import QMainWindow, QApplication, QMenu, QVBoxLayout, \
    QAction, QFileDialog, QWidget, \
    QListWidget, QListView, QListWidgetItem, QGraphicsView, QGraphicsScene, \
    QDesktopWidget, QLabel, QHBoxLayout, QProgressDialog, QGraphicsTextItem, \
    QGraphicsItem, QComboBox, QGraphicsSceneMouseEvent


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
                self.parent().init_text_settings(self)
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
        self.main_widget = QWidget()
        self.init_size()
        self.addWidget(self.main_widget)

    def init_size(self):
        size = QDesktopWidget().availableGeometry(self.main_widget)
        size.setHeight(int(size.height() * 0.3))
        size.setWidth(int(size.width() * 0.3))
        self.main_widget.setFixedSize(QSize(size.height(), size.width()))

    def init_text_settings(self, text_item):
        self.remove_layout()
        layout = QVBoxLayout()
        # capitalization
        capitalization_layout = QHBoxLayout()
        capitalization_layout.addWidget(QLabel("Capitalization"))
        capitalization_combo_box = QComboBox()
        capitalization_options = ["Not set",
                                  "All uppercase",
                                  "All lowercase",
                                  "Small caps",
                                  "Capitalize"]
        for option in capitalization_options:
            capitalization_combo_box.addItem(option)
        capitalization_combo_box.setCurrentIndex(
            text_item.font().capitalization())
        capitalization_combo_box \
            .currentIndexChanged.connect(lambda x: self.set_text_capitalization(capitalization_combo_box.itemText(x),
                                                                                self.parent().images_panel.image_edit_area.scene().selectedItems()[
                                                                                    0]))
        capitalization_layout.addWidget(capitalization_combo_box)
        layout.addLayout(capitalization_layout)
        self.main_widget.setLayout(layout)

    def remove_layout(self):
        if self.main_widget.layout():
            QWidget().setLayout(self.main_widget.layout())

    @staticmethod
    def set_text_capitalization(capitalization, text_item):
        capitalization_options = {"Not set": QFont.MixedCase,
                                  "All uppercase": QFont.AllUppercase,
                                  "All lowercase": QFont.AllLowercase,
                                  "Small caps": QFont.SmallCaps,
                                  "Capitalize": QFont.Capitalize}
        font = text_item.font()
        font.setCapitalization(capitalization_options[capitalization])
        text_item.setFont(font)


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


if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec_()
