import os
import json
import logging
import dataclasses
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtWidgets, QtCore, QtGui

from source.config import AppConfig
from source.tools.image_viewer import ImageViewer
from source.main_window.main_window import Ui_MainWindow


class ImageCropTool(Ui_MainWindow, QMainWindow):

    def __init__(self, app_config: dict, parent=None, debug=True):
        super(ImageCropTool, self).__init__(parent=parent)
        self.setupUi(self)

        # initialize logger
        self._logger = logging.getLogger(type(self).__name__)
        self._logger.setLevel(logging.DEBUG if debug else logging.INFO)

        # initialize app config
        self._app_config = AppConfig(**app_config)

        # instances
        self._image_viewer = ImageViewer(self)
        self.gridLayoutImageViewer.addWidget(self._image_viewer)

        # events
        self.actionSetSaveDir.triggered.connect(self._save_image_folder_dialog)
        self.actionOpenimageDir.triggered.connect(self._open_image_folder_dialog)
        self.comboBoxClass.currentIndexChanged.connect(self._on_combobox_class_changed)
        self.lineEditListWidgetImagesFinder.textChanged.connect(self._on_line_edit_text_changed)
        self.comboBoxCropValues.currentIndexChanged.connect(self._on_combobox_crop_value_changed)
        self.listWidgetImageList.itemDoubleClicked.connect(self._on_list_widget_image_list_item_double_clicked)

        # load last changes
        self._load_from_config()

        # log start
        self._update_log(message="[ Program started ]")

    def closeEvent(self, event):
        close = QtWidgets.QMessageBox.question(self, "QUIT", "Are you sure want to stop process?",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if close == QtWidgets.QMessageBox.Yes:
            with open('data/config.json', 'w') as fp:
                json.dump(dataclasses.asdict(self._app_config), fp)
            event.accept()
        else:
            event.ignore()

    def _on_line_edit_text_changed(self):
        current_text = self.lineEditListWidgetImagesFinder.text()

        for row in range(self.listWidgetImageList.count()):
            it = self.listWidgetImageList.item(row)

            if current_text:
                it.setHidden(current_text not in it.text())
            else:
                it.setHidden(False)

    def _on_combobox_crop_value_changed(self):
        crop_value = self.comboBoxCropValues.currentText()
        x, y = crop_value.split('x')
        x = int(x)
        y = int(y)

        self._app_config.rect_box_shape = (x, y)
        self._image_viewer.rect_box_shape = (x, y)
        self._update_log(message=f"[ Crop value {(x, y)} is changed ]")

    def _on_combobox_class_changed(self):
        class_name = self.comboBoxClass.currentText()

        self._app_config.class_name = class_name
        self._image_viewer.selected_class = class_name
        self._update_log(message=f"[ Class name {class_name} is changed ]")

    def _open_image_folder_dialog(self):
        file_dialog: QtWidgets.QFileDialog = self._folder_file_dialog()

        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.listWidgetImageList.clear()
            file_path = file_dialog.selectedFiles()[0]

            self._update_list_widget_items(file_path)
            self._app_config.image_folder_path = file_path
            self._update_log(message=f"[ Folder {file_path} is loaded ]")

    def _update_list_widget_items(self, file_path, last_opened_file=None):
        folder_files = os.listdir(file_path)
        for folder_file in folder_files:
            if not folder_file.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.TIF', '.TIFF', '.tiff')):
                continue

            full_folder_file = os.path.join(file_path, folder_file)
            list_widget_item = QtWidgets.QListWidgetItem(full_folder_file)
            self.listWidgetImageList.addItem(list_widget_item)

            if full_folder_file == last_opened_file:
                self.listWidgetImageList.setCurrentItem(list_widget_item)

    def _save_image_folder_dialog(self):
        file_dialog: QtWidgets.QFileDialog = self._folder_file_dialog()

        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            self._update_save_image_folder_tree_view(file_path)

            self._image_viewer.save_dir_path = file_path
            self._app_config.save_folder_path = file_path
            self._update_save_image_folder_tree_view(file_path)
            self._update_log(message=f"[ Save folder {file_path} is set ]")

    def _update_save_image_folder_tree_view(self, file_path: str):
        if not os.path.exists(file_path):
            os.mkdir(file_path)

        folder_files = os.listdir(file_path)
        defined_classes = [self.comboBoxClass.itemText(i) for i in range(self.comboBoxClass.count())]

        if all([False for folder_file in folder_files if folder_file in defined_classes]):
            for defined_class in defined_classes:
                os.mkdir(os.path.join(file_path, defined_class))

        self.treeViewSaveFolder.setContextMenuPolicy(Qt.CustomContextMenu)
        self._model_tree_save_folder: QtWidgets.QFileSystemModel = QtWidgets.QFileSystemModel(
            self.treeViewSaveFolder
        )
        self._model_tree_save_folder.setRootPath(file_path)
        self.treeViewSaveFolder.setModel(self._model_tree_save_folder)
        self.treeViewSaveFolder.setRootIndex(
            self._model_tree_save_folder.index(file_path)
        )
        self.treeViewSaveFolder.setSortingEnabled(True)

    def _on_list_widget_image_list_item_double_clicked(self):
        file_path = self.listWidgetImageList.currentItem().text()
        pixmap = QtGui.QPixmap(file_path)
        self._image_viewer.set_photo(pixmap)

        self._app_config.last_opened_image = file_path
        self._update_log(message=f"[ Image {file_path} opened ]")

    def _folder_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        options |= QtWidgets.QFileDialog.DontUseCustomDirectoryIcons

        dialog = QtWidgets.QFileDialog(self)
        dialog.setOptions(options)
        dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dialog.setDirectory(os.path.abspath(os.getcwd()))

        return dialog

    def _update_log(self, message: str):
        self._logger.info(message)
        self.statusbar.showMessage(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}")

    def _load_from_config(self):
        # update views
        if self._app_config.image_folder_path:
            self._update_list_widget_items(self._app_config.image_folder_path, self._app_config.last_opened_image)

        if self._app_config.save_folder_path:
            self._update_save_image_folder_tree_view(self._app_config.save_folder_path)
            self._image_viewer.save_dir_path = self._app_config.save_folder_path

        # update settings data
        if self._app_config.class_name:
            self.comboBoxClass.setCurrentText(self._app_config.class_name)
            x, y = self._app_config.rect_box_shape
            self.comboBoxCropValues.setCurrentText(f"{x}x{y}")
            self._image_viewer.rect_box_shape = self._app_config.rect_box_shape

        # update settings data
        if self._app_config.class_name:
            self._image_viewer.selected_class = self._app_config.class_name

        # open the image
        if self._app_config.last_opened_image:
            pixmap = QtGui.QPixmap(self._app_config.last_opened_image)
            self._image_viewer.set_photo(pixmap)
