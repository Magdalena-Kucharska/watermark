import os

from PySide2.QtCore import Qt, QLocale
from PySide2.QtGui import QFont, QFontDatabase, QIntValidator, \
    QDoubleValidator, QKeySequence
from PySide2.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLabel, \
    QComboBox, QGroupBox, QCheckBox, QLineEdit, \
    QSizePolicy, QStackedLayout, QListWidget, QListView, QProgressDialog, \
    QListWidgetItem, QPushButton, QColorDialog, QSlider, QDial, QMenu, QAction


class ImagesNav(QListWidget):

    def __init__(self, *args, **kwargs):
        super(ImagesNav, self).__init__(*args, **kwargs)
        self.loaded_images = None
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setResizeMode(QListView.Adjust)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        self.setContextMenuPolicy(Qt.DefaultContextMenu)

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
            item = QListWidgetItem(os.path.basename(image_path))
            item.setData(Qt.UserRole, image_path)
            self.addItem(item)
        progress.setValue(len(self.loaded_images))

    def contextMenuEvent(self, event):
        if len(self.selectedItems()) > 0 and len(self.loaded_images) > 1:
            context_menu = QMenu(self)
            remove_action = QAction("Remove from list")
            remove_action.setShortcut(QKeySequence(Qt.Key_Delete))
            remove_action.triggered.connect(self.remove_selected_item)
            context_menu.addAction(remove_action)
            context_menu.exec_(event.globalPos())

    def remove_selected_item(self):
        selected_item = self.takeItem(self.row(self.selectedItems()[0]))
        self.loaded_images.remove(selected_item.data(Qt.UserRole))
        del selected_item

    def keyPressEvent(self, event):
        if len(self.selectedItems()) > 0 and event.key() == Qt.Key_Delete \
                and len(self.loaded_images) > 1:
            self.remove_selected_item()

class Sidebar(QWidget):

    def __init__(self, *args, **kwargs):
        super(Sidebar, self).__init__(*args, **kwargs)
        self.settings = QWidget()
        self.navigation = ImagesNav()
        self.layout = QStackedLayout()
        self.layout.addWidget(self.settings)
        self.layout.addWidget(self.navigation)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        self.setLayout(self.layout)
        self.layout.setCurrentWidget(self.navigation)

    def init_font_settings(self, text_item):
        self.remove_layout()
        font_layout = QVBoxLayout()
        font_layout.setAlignment(Qt.AlignTop)
        font_layout.addWidget(QLabel("Family"))
        font_layout.addWidget(self.init_font_families_widget(text_item))
        font_layout.addWidget(QLabel("Size"))
        font_layout.addLayout(self.init_font_size_layout(text_item))
        font_layout.addWidget(QLabel("Color"))
        font_layout.addWidget(self.init_font_color_widget(text_item))
        font_layout.addWidget(QLabel("Style"))
        font_layout.addWidget(self.init_font_style_widget(text_item))
        font_layout.addWidget(QLabel("Weight"))
        font_layout.addWidget(self.init_font_weight_widget(text_item))
        font_layout.addWidget(QLabel("Capitalization"))
        font_layout.addWidget(self.init_capitalization_widget(text_item))
        font_layout.addWidget(QLabel("Stretch"))
        font_layout.addWidget(self.init_stretch_layout(text_item))
        font_layout.addWidget(self.init_kerning_widget(text_item))
        font_layout.addWidget(self.init_overline_widget(text_item))
        font_layout.addWidget(self.init_strikeout_widget(text_item))
        font_layout.addWidget(self.init_underline_widget(text_item))
        font_layout.addWidget(self.init_letter_spacing_widget(text_item))
        font_group_box = QGroupBox("Font")
        font_group_box.setLayout(font_layout)
        layout = QVBoxLayout()
        layout.addWidget(font_group_box)
        text_item_group_box = QGroupBox("Text item")
        text_item_layout = QVBoxLayout()
        text_item_layout.setAlignment(Qt.AlignTop)
        text_item_layout.addLayout(self
                                   .init_item_opacity_layout(text_item))
        text_item_layout.addLayout(self.init_item_rotation_layout(text_item))
        text_item_group_box.setLayout(text_item_layout)
        layout.addWidget(text_item_group_box)
        self.settings.setLayout(layout)
        self.layout.setCurrentWidget(self.settings)

    def init_image_settings(self, image_item):
        self.remove_layout()
        image_layout = QVBoxLayout()
        image_layout.setAlignment(Qt.AlignTop)
        image_group_box = QGroupBox("Image")
        image_layout.addLayout(self.init_item_opacity_layout(image_item))
        image_layout.addSpacing(30)
        image_layout.addLayout(self.init_item_rotation_layout(image_item))
        image_layout.addSpacing(30)
        image_layout.addLayout(self.init_image_scale_layout(image_item))
        image_group_box.setLayout(image_layout)
        layout = QVBoxLayout()
        layout.addWidget(image_group_box)
        self.settings.setLayout(layout)
        self.layout.setCurrentWidget(self.settings)

    def remove_layout(self):
        if self.settings.layout():
            QWidget().setLayout(self.settings.layout())

    def init_image_scale_layout(self, image_item):
        current_scale = image_item.scale()
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("Scale"))
        scale_value_label = QLabel(str(current_scale * 100) + "%")
        label_layout.addWidget(scale_value_label)
        scale_input = QSlider()
        scale_input.setOrientation(Qt.Horizontal)
        scale_input.setMinimum(1)
        scale_input.setMaximum(1000)
        scale_input.setSingleStep(1)
        scale_input.setValue(current_scale * 100)
        scale_input.valueChanged.connect(lambda current_value:
                                         self.set_image_scale(current_value,
                                                              image_item,
                                                              scale_value_label))
        scale_layout = QVBoxLayout()
        scale_layout.addLayout(label_layout)
        scale_layout.addWidget(scale_input)
        return scale_layout

    def init_item_rotation_layout(self, item):
        current_rotation = item.rotation()
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("Rotation"))
        rotation_value_label = QLabel(str(current_rotation) + " degrees")
        label_layout.addWidget(rotation_value_label)
        rotation_layout = QVBoxLayout()
        rotation_layout.addLayout(label_layout)
        rotation_input = QDial()
        rotation_input.setMinimum(0)
        rotation_input.setMaximum(359)
        rotation_input.setSingleStep(1)
        rotation_input.setWrapping(True)
        rotation_input.setValue(int(current_rotation))
        rotation_input.valueChanged.connect(lambda current_value:
                                            self.set_item_rotation(
                                                current_value, item,
                                                rotation_value_label))
        rotation_layout.addWidget(rotation_input)
        return rotation_layout

    def init_item_opacity_layout(self, item):
        current_opacity = item.opacity()
        label_layout = QHBoxLayout()
        label_layout.addWidget(QLabel("Opacity"))
        opacity_value_label = QLabel(str(current_opacity))
        label_layout.addWidget(opacity_value_label)
        opacity_layout = QVBoxLayout()
        opacity_layout.addLayout(label_layout)
        opacity_input = QSlider()
        opacity_input.setOrientation(Qt.Horizontal)
        opacity_input.setMinimum(1)
        opacity_input.setMaximum(100)
        opacity_input.setSingleStep(1)
        opacity_value = current_opacity * 100
        opacity_input.setValue(opacity_value)
        opacity_input.valueChanged.connect(lambda current_value:
                                           self.set_item_opacity(
                                               current_value, item,
                                               opacity_value_label))
        opacity_layout.addWidget(opacity_input)
        return opacity_layout

    def init_font_color_widget(self, text_item):
        button = QPushButton("Set color")
        button.clicked.connect(lambda: self.set_font_color(text_item))
        return button

    def init_font_weight_widget(self, text_item):
        font_weights = {0: "Thin",
                        12: "Extra light",
                        25: "Light",
                        50: "Normal",
                        57: "Medium",
                        63: "Demi bold",
                        75: "Bold",
                        81: "Extra bold",
                        87: "Black"}
        font_weight_combo_box = QComboBox()
        for font_weight in font_weights.values():
            font_weight_combo_box.addItem(font_weight)
        font_weight_combo_box.setCurrentText(font_weights[text_item.font(

        ).weight()])
        font_weight_combo_box.currentTextChanged.connect(lambda
                                                             current_text:
                                                         self.set_font_weight(
                                                             current_text,
                                                             text_item))
        return font_weight_combo_box

    def init_font_style_widget(self, text_item):
        font_styles = {QFont.StyleNormal: "Normal",
                       QFont.StyleItalic: "Italic",
                       QFont.StyleOblique: "Oblique"}
        font_style_combo_box = QComboBox()
        for font_style in font_styles.values():
            font_style_combo_box.addItem(font_style)
        font_style_combo_box.setCurrentText(font_styles[text_item.font(

        ).style()])
        font_style_combo_box.currentTextChanged.connect(lambda current_text:
                                                        self.set_font_style(
                                                            current_text,
                                                            text_item))
        return font_style_combo_box

    def init_font_size_layout(self, text_item):
        font_size_input = QLineEdit()
        validator = QDoubleValidator(0.5, 900., 2)
        validator.setNotation(QDoubleValidator.StandardNotation)
        font_size_input.setValidator(validator)
        font_size_input.setText(str(text_item.font().pointSizeF()))
        font_size_input.returnPressed.connect(lambda:
                                              self.set_font_size(
                                                  font_size_input.text(),
                                                  text_item))
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(font_size_input)
        font_size_layout.addWidget(QLabel("pt"))
        return font_size_layout

    def init_strikeout_widget(self, text_item):
        strikeout_checkbox = QCheckBox("Strikeout")
        strikeout_checkbox.setChecked(text_item.font().strikeOut())
        strikeout_checkbox.stateChanged.connect(lambda x:
                                                self.set_font_strikeout(x,
                                                                        text_item))
        return strikeout_checkbox

    def init_underline_widget(self, text_item):
        underline_checkbox = QCheckBox("Underline")
        underline_checkbox.setChecked(text_item.font().underline())
        underline_checkbox.stateChanged.connect(lambda x:
                                                self.set_font_underline(x,
                                                                        text_item))
        return underline_checkbox

    def init_overline_widget(self, text_item):
        overline_checkbox = QCheckBox("Overline")
        overline_checkbox.setChecked(text_item.font().overline())
        overline_checkbox.stateChanged.connect(lambda x:
                                               self.set_font_overline(x,
                                                                      text_item))
        return overline_checkbox

    def init_letter_spacing_widget(self, text_item):
        letter_spacing_layout = QVBoxLayout()
        letter_spacing_type_combo_box = QComboBox()
        letter_spacing_value_input = QLineEdit()

        letter_spacing_types = {QFont.PercentageSpacing: "Percentage spacing",
                                QFont.AbsoluteSpacing: "Absolute spacing"}
        for letter_spacing_type in letter_spacing_types.values():
            letter_spacing_type_combo_box.addItem(letter_spacing_type)
        current_spacing_type = text_item.font().letterSpacingType()
        letter_spacing_type_combo_box.setCurrentText(
            letter_spacing_types[current_spacing_type])
        letter_spacing_type_combo_box.currentTextChanged.connect(lambda x:
                                                                 self.set_letter_spacing_type(
                                                                     text_item,
                                                                     x,
                                                                     letter_spacing_value_input,
                                                                     units_label))

        letter_spacing_layout.addWidget(letter_spacing_type_combo_box)

        letter_spacing_value_input.setValidator(QIntValidator(-10000, 10000))
        current_spacing = str(int(text_item.font().letterSpacing()))
        if current_spacing_type == QFont.PercentageSpacing and \
                current_spacing == "0":
            letter_spacing_value_input.setText("100")
        else:
            letter_spacing_value_input.setText(current_spacing)
        letter_spacing_value_input.returnPressed.connect(lambda:
                                                         self.set_letter_spacing_value(
                                                             text_item,
                                                             letter_spacing_type_combo_box,
                                                             letter_spacing_value_input))
        letter_spacing_value_input_layout = QHBoxLayout()
        letter_spacing_value_input_layout.addWidget(letter_spacing_value_input)
        units_label = QLabel()
        if current_spacing_type == QFont.PercentageSpacing:
            units_label.setText("%")
        else:
            units_label.setText("px")
        letter_spacing_value_input_layout.addWidget(units_label)
        letter_spacing_layout.addLayout(letter_spacing_value_input_layout)
        letter_spacing_group_box = QGroupBox("Letter spacing")
        letter_spacing_group_box.setLayout(letter_spacing_layout)
        return letter_spacing_group_box

    def init_kerning_widget(self, text_item):
        kerning_widget = QCheckBox("Kerning")
        kerning_widget.setChecked(text_item.font().kerning())
        kerning_widget.stateChanged.connect(lambda x: self.set_text_kerning(
            x, text_item))
        return kerning_widget

    def init_font_families_widget(self, text_item):
        families_combo_box = QComboBox()
        families_list = QFontDatabase().families()
        for family in families_list:
            families_combo_box.addItem(family)
        families_combo_box.setCurrentText(text_item.font().family())
        families_combo_box.currentTextChanged.connect(lambda x:
                                                      self.set_font_family(
                                                          x,
                                                          text_item))
        return families_combo_box

    def init_capitalization_widget(self, text_item):
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
        capitalization_combo_box.currentIndexChanged.connect(
            lambda x: self.set_text_capitalization(
                capitalization_combo_box.itemText(x), text_item))
        return capitalization_combo_box

    def init_stretch_layout(self, text_item):
        stretch_combo_box = QComboBox()
        stretch_options = {0: "Not set",
                           50: "UltraCondensed",
                           62: "ExtraCondensed",
                           75: "Condensed",
                           87: "SemiCondensed",
                           100: "Unstretched",
                           112: "SemiExpanded",
                           125: "Expanded",
                           150: "ExtraExpanded",
                           200: "UltraExpanded"}
        for option in stretch_options.values():
            stretch_combo_box.addItem(option)
        stretch_combo_box.setCurrentText(stretch_options[text_item.font(

        ).stretch()])
        stretch_combo_box.currentIndexChanged.connect(lambda x:
                                                      self.set_text_stretch(
                                                          stretch_combo_box.itemText(
                                                              x),
                                                          text_item))
        return stretch_combo_box

    @staticmethod
    def set_image_scale(scale, image_item, value_label):
        image_item.setScale(scale / 100)
        value_label.setText(str(scale) + "%")

    @staticmethod
    def set_item_rotation(rotation, item, value_label):
        item.setRotation(float(rotation))
        value_label.setText(str(rotation) + " degrees")

    @staticmethod
    def set_item_opacity(opacity, item, value_label):
        item.setOpacity(opacity / 100)
        value_label.setText(str(opacity / 100))

    @staticmethod
    def set_font_color(text_item):
        font_color_dialog = QColorDialog()
        font_color = font_color_dialog.getColor(
            initial=text_item.defaultTextColor(

            ))
        if font_color.isValid():
            text_item.setDefaultTextColor(font_color)

    @staticmethod
    def set_font_weight(weight, text_item):
        font_weights = {"Thin": 0,
                        "Extra light": 12,
                        "Light": 25,
                        "Normal": 50,
                        "Medium": 57,
                        "Demi bold": 63,
                        "Bold": 75,
                        "Extra bold": 81,
                        "Black": 87}
        font = text_item.font()
        font.setWeight(font_weights[weight])
        text_item.setFont(font)

    @staticmethod
    def set_font_style(style, text_item):
        font_styles = {"Normal": QFont.StyleNormal,
                       "Italic": QFont.StyleItalic,
                       "Oblique": QFont.StyleOblique}
        font = text_item.font()
        font.setStyle(font_styles[style])
        text_item.setFont(font)

    @staticmethod
    def set_font_size(size, text_item):
        font = text_item.font()
        (size_double, ok) = QLocale.toDouble(QLocale.system(), size)
        font.setPointSizeF(size_double)
        text_item.setFont(font)

    @staticmethod
    def set_font_strikeout(strikeout, text_item):
        font = text_item.font()
        font.setStrikeOut(strikeout)
        text_item.setFont(font)

    @staticmethod
    def set_font_underline(underline, text_item):
        font = text_item.font()
        font.setUnderline(underline)
        text_item.setFont(font)

    @staticmethod
    def set_font_overline(overline, text_item):
        font = text_item.font()
        font.setOverline(overline)
        text_item.setFont(font)

    @staticmethod
    def set_letter_spacing_type(text_item, letter_spacing_type,
                                letter_spacing_value_input, units_label):
        font = text_item.font()
        letter_spacing_types = {"Percentage spacing": QFont.PercentageSpacing,
                                "Absolute spacing": QFont.AbsoluteSpacing}
        if letter_spacing_type == "Percentage spacing":
            spacing = 100
        else:
            spacing = 0
        font.setLetterSpacing(letter_spacing_types[letter_spacing_type],
                              spacing)
        text_item.setFont(font)
        if units_label:
            if letter_spacing_type == "Percentage spacing":
                units_label.setText("%")
            else:
                units_label.setText("px")
        letter_spacing_value_input.setText(str(spacing))

    @staticmethod
    def set_letter_spacing_value(text_item,
                                 letter_spacing_type_combo_box,
                                 letter_spacing_value_input):
        letter_spacing_types = {"Percentage spacing": QFont.PercentageSpacing,
                                "Absolute spacing": QFont.AbsoluteSpacing}
        font = text_item.font()
        letter_spacing_type = letter_spacing_type_combo_box.currentText()
        letter_spacing_value = int(letter_spacing_value_input.text())
        font.setLetterSpacing(letter_spacing_types[letter_spacing_type],
                              letter_spacing_value)
        text_item.setFont(font)

    @staticmethod
    def set_text_kerning(kerning, text_item):
        font = text_item.font()
        font.setKerning(kerning)
        text_item.setFont(font)

    @staticmethod
    def set_font_family(family, text_item):
        font = text_item.font()
        font.setFamily(family)
        text_item.setFont(font)

    @staticmethod
    def set_text_stretch(stretch, text_item):
        stretch_options = {"Not set": QFont.AnyStretch,
                           "UltraCondensed": QFont.UltraCondensed,
                           "ExtraCondensed": QFont.ExtraCondensed,
                           "Condensed": QFont.Condensed,
                           "SemiCondensed": QFont.SemiCondensed,
                           "Unstretched": QFont.Unstretched,
                           "SemiExpanded": QFont.SemiExpanded,
                           "Expanded": QFont.Expanded,
                           "ExtraExpanded": QFont.ExtraExpanded,
                           "UltraExpanded": QFont.UltraExpanded}
        font = text_item.font()
        font.setStretch(stretch_options[stretch])
        text_item.setFont(font)

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
