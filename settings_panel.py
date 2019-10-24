from PySide2.QtGui import QFont, QFontDatabase, QIntValidator
from PySide2.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLabel, \
    QComboBox, QGroupBox, QCheckBox, QLineEdit, \
    QSizePolicy


class SettingsPanel(QVBoxLayout):

    def __init__(self, *args, **kwargs):
        super(SettingsPanel, self).__init__(*args, **kwargs)
        self.main_widget = QWidget()
        self.main_widget.setSizePolicy(QSizePolicy.Maximum,
                                       QSizePolicy.Maximum)
        self.addWidget(self.main_widget)

    def init_font_settings(self, text_item):
        self.remove_layout()
        self.main_widget.setFixedWidth(160)
        font_layout = QVBoxLayout()
        font_layout.addLayout(self.init_capitalization_layout(text_item))
        font_layout.addLayout(self.init_stretch_layout(text_item))
        font_layout.addLayout(self.init_font_families_layout(text_item))
        font_layout.addWidget(self.init_kerning_widget(text_item))
        font_layout.addWidget(self.init_overline_widget(text_item))
        font_layout.addWidget(self.init_strikeout_widget(text_item))
        font_layout.addWidget(self.init_underline_widget(text_item))
        font_layout.addLayout(self.init_letter_spacing_layout(text_item))
        font_group_box = QGroupBox("Font")
        font_group_box.setLayout(font_layout)
        layout = QVBoxLayout()
        layout.addWidget(font_group_box)
        self.main_widget.setLayout(layout)
        self.parent().images_panel.images_nav.hide()
        self.main_widget.show()

    def remove_layout(self):
        if self.main_widget.layout():
            QWidget().setLayout(self.main_widget.layout())
            self.main_widget.hide()
            self.parent().images_panel.images_nav.show()

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

    def init_letter_spacing_layout(self, text_item):
        letter_spacing_layout = QVBoxLayout()
        letter_spacing_layout.addWidget(QLabel("Letter spacing"))
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
        return letter_spacing_layout

    def init_kerning_widget(self, text_item):
        kerning_widget = QCheckBox("Kerning")
        kerning_widget.setChecked(text_item.font().kerning())
        kerning_widget.stateChanged.connect(lambda x: self.set_text_kerning(
            x, text_item))
        return kerning_widget

    def init_font_families_layout(self, text_item):
        families_layout = QVBoxLayout()
        families_layout.addWidget(QLabel("Family"))
        families_combo_box = QComboBox()
        families_list = QFontDatabase().families()
        for family in families_list:
            families_combo_box.addItem(family)
        families_combo_box.setCurrentText(text_item.font().family())
        families_combo_box.currentTextChanged.connect(lambda x:
                                                      self.set_font_family(
                                                          x,
                                                          text_item))
        families_layout.addWidget(families_combo_box)
        return families_layout

    def init_capitalization_layout(self, text_item):
        capitalization_layout = QVBoxLayout()
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
        capitalization_combo_box.currentIndexChanged.connect(
            lambda x: self.set_text_capitalization(
                capitalization_combo_box.itemText(x), text_item))
        capitalization_layout.addWidget(capitalization_combo_box)
        return capitalization_layout

    def init_stretch_layout(self, text_item):
        stretch_layout = QVBoxLayout()
        stretch_layout.addWidget(QLabel("Stretch"))
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
        stretch_layout.addWidget(stretch_combo_box)
        return stretch_layout

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
