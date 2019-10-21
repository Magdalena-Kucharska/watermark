from PySide2.QtCore import QSize
from PySide2.QtGui import QFont, QFontDatabase
from PySide2.QtWidgets import QVBoxLayout, QWidget, QDesktopWidget, \
    QHBoxLayout, QLabel, QComboBox, QGroupBox


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
        font_layout = QVBoxLayout()
        # capitalization
        font_layout.addLayout(self.init_capitalization_layout(text_item))
        font_layout.addLayout(self.init_stretch_layout(text_item))
        font_layout.addLayout(self.init_families_layout(text_item))
        font_group_box = QGroupBox("Font")
        font_group_box.setLayout(font_layout)
        layout = QVBoxLayout()
        layout.addWidget(font_group_box)
        self.main_widget.setLayout(layout)

    def remove_layout(self):
        if self.main_widget.layout():
            QWidget().setLayout(self.main_widget.layout())

    def init_families_layout(self, text_item):
        families_layout = QHBoxLayout()
        families_layout.addWidget(QLabel("Family"))
        families_combo_box = QComboBox()
        families_list = QFontDatabase().families()
        for family in families_list:
            families_combo_box.addItem(family)
        families_combo_box.setCurrentText(text_item.font().family())
        selected_text_item = \
            self.parent().images_panel.image_edit_area.scene().selectedItems()[
                0]
        families_combo_box.currentTextChanged.connect(lambda x:
                                                      self.set_font_family(
                                                          x,
                                                          selected_text_item))
        families_layout.addWidget(families_combo_box)
        return families_layout

    def init_capitalization_layout(self, text_item):
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
        selected_text_item = \
            self.parent().images_panel.image_edit_area.scene().selectedItems()[
                0]
        capitalization_combo_box.currentIndexChanged.connect(
            lambda x: self.set_text_capitalization(
                capitalization_combo_box.itemText(x), selected_text_item))
        capitalization_layout.addWidget(capitalization_combo_box)
        return capitalization_layout

    def init_stretch_layout(self, text_item):
        stretch_layout = QHBoxLayout()
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
        selected_text_item = \
            self.parent().images_panel.image_edit_area.scene().selectedItems()[
                0]
        stretch_combo_box.currentIndexChanged.connect(lambda x:
                                                      self.set_text_stretch(
                                                          stretch_combo_box.itemText(
                                                              x),
                                                          selected_text_item))
        stretch_layout.addWidget(stretch_combo_box)
        return stretch_layout

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
