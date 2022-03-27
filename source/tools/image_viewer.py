import uuid
import logging
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets


class ImageViewer(QtWidgets.QGraphicsView):
    _photoClicked = QtCore.pyqtSignal(QtCore.QPoint)
    _rect: QtWidgets.QGraphicsRectItem = None

    _save_dir_path: str = None
    _selected_class: str = None
    _rect_box_shape: tuple = None

    _zoom: float = 0.0
    _empty: bool = True

    def __init__(self, parent, debug=True):
        super(ImageViewer, self).__init__(parent)
        # initialize logger
        self._logger = logging.getLogger(type(self).__name__)
        self._logger.setLevel(logging.DEBUG if debug else logging.INFO)

        self._parent = parent
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._pen = QtGui.QPen(Qt.red, 5)

        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    @property
    def save_dir_path(self):
        return self._save_dir_path

    @save_dir_path.setter
    def save_dir_path(self, value):
        self._save_dir_path = value

    @property
    def selected_class(self):
        return self._selected_class

    @selected_class.setter
    def selected_class(self, value):
        self._selected_class = value

    @property
    def rect_box_shape(self):
        return self._rect_box_shape

    @rect_box_shape.setter
    def rect_box_shape(self, value):
        self._rect_box_shape = value

        if self._rect is not None:
            self._scene.removeItem(self._rect)

        self._rect = QtWidgets.QGraphicsRectItem(0, 0, value[0], value[1])
        self._rect.setPen(self._pen)

        if self._photo.pixmap() and not self._photo.pixmap().isNull():
            self._scene.addItem(self._rect)

    def fitInView(self, *args):
        rect = QtCore.QRectF(self._photo.pixmap().rect())

        if rect.isNull():
            return

        self.setSceneRect(rect)
        unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
        self.scale(1 / unity.width(), 1 / unity.height())

        view_rect = self.viewport().rect()
        screen_rect = self.transform().mapRect(rect)
        factor = min(view_rect.width() / screen_rect.width(), view_rect.height() / screen_rect.height())

        self.scale(factor, factor)
        self._zoom = 0

    def set_photo(self, pixmap=None):
        self._zoom = 0

        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
            self._scene.addItem(self._rect)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())

        self.fitInView()

    def wheelEvent(self, event):
        if self._empty:
            return

        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1

        if self._zoom > 0:
            self.scale(factor, factor)
        elif self._zoom == 0:
            self.fitInView()
        else:
            self._zoom = 0

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self._photoClicked.emit(self.mapToScene(event.pos()).toPoint())

            if not event.button() == Qt.RightButton:
                return

            if not self._rect_box_shape or not self._save_dir_path or not self._selected_class:
                return

            pixmap: QtGui.QPixmap = self._photo.pixmap()

            center_rect: QtCore.QRectF = self._rect.sceneBoundingRect().center()
            center_rect_x = center_rect.x()
            center_rect_y = center_rect.y()

            x, y = self._rect_box_shape
            cropped: QtGui.QPixmap = pixmap.copy(center_rect_x - x / 2, center_rect_y - y / 2, x, y)
            save_file_name = f"{self._save_dir_path}/{self._selected_class}/{str(uuid.uuid4())}.JPG"
            cropped.save(save_file_name)

            self._logger.info(f'[ New image added by path {save_file_name} ]')
            self._parent.statusbar.showMessage(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [ New image added by path {save_file_name} ]"
            )

        super(ImageViewer, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._photo.isUnderMouse() and self._rect is not None:
            self._rect.setPos(self.mapToScene(event.pos()).toPoint())
        super(ImageViewer, self).mouseMoveEvent(event)
