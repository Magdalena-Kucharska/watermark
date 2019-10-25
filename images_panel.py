from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene


class ImageEditor(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super(ImageEditor, self).__init__(*args, **kwargs)
        # self.images_nav = ImagesNav()
        # self.images_nav.clicked.connect(lambda x: self.load_image(
        #     self.images_nav.currentItem().data(Qt.UserRole)))
        # self.image_edit_area = QGraphicsView()
        self.setScene(QGraphicsScene())
        # self.addWidget(self.image_edit_area)
        # self.addWidget(self.images_nav)
        # self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

    def load_image(self, image_path):
        self.scene().clear()
        image = QPixmap(image_path)
        self.scene().addPixmap(image)
        self.scene().setSceneRect(self.scene().itemsBoundingRect())
