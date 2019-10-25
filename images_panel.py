from PySide2.QtWidgets import QGraphicsView, QGraphicsScene


class ImageEditor(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super(ImageEditor, self).__init__(*args, **kwargs)
        self.setScene(QGraphicsScene())
