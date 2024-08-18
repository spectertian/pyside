import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                               QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
                               QRubberBand, QDialog, QDialogButtonBox, QListWidgetItem,
                               QScrollArea, QMessageBox)
from PySide6.QtGui import QPixmap, QScreen, QPainter, QColor, QIcon
from PySide6.QtCore import Qt, QRect, QPoint, Signal, QSize


class ScreenshotTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screenshot Tool")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)

        # Left side: buttons and list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.capture_button = QPushButton("Capture Screenshot")
        self.capture_button.clicked.connect(self.start_capture)

        self.screenshot_list = QListWidget()
        self.screenshot_list.setIconSize(QSize(100, 100))
        self.screenshot_list.setResizeMode(QListWidget.Adjust)
        self.screenshot_list.setViewMode(QListWidget.IconMode)
        self.screenshot_list.itemDoubleClicked.connect(self.show_full_screenshot)

        self.delete_button = QPushButton("Delete Screenshot")
        self.delete_button.clicked.connect(self.delete_screenshot)

        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.load_saved_screenshots)

        left_layout.addWidget(self.capture_button)
        left_layout.addWidget(self.screenshot_list)
        left_layout.addWidget(self.delete_button)
        left_layout.addWidget(self.refresh_button)

        # Right side: image preview
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(left_widget, 1)
        self.layout.addWidget(self.image_label, 2)

        self.load_saved_screenshots()

    def start_capture(self):
        self.hide()
        self.screen_capture = ScreenCapture()
        self.screen_capture.screenshot_taken.connect(self.handle_screenshot)
        self.screen_capture.show()

    def handle_screenshot(self, pixmap):
        self.show()
        if pixmap:
            save_dialog = SaveDialog(pixmap, self)
            if save_dialog.exec() == QDialog.Accepted:
                filename = f"screenshot_{len(os.listdir('screenshots')) + 1}.png"
                pixmap.save(os.path.join("screenshots", filename))
                self.load_saved_screenshots()

    def load_saved_screenshots(self):
        self.screenshot_list.clear()
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        for filename in os.listdir("screenshots"):
            file_path = os.path.join("screenshots", filename)
            pixmap = QPixmap(file_path)
            icon = QIcon(pixmap)
            item = QListWidgetItem(icon, filename)
            item.setData(Qt.UserRole, file_path)
            self.screenshot_list.addItem(item)

    def show_full_screenshot(self, item):
        file_path = item.data(Qt.UserRole)
        preview_dialog = ImagePreviewDialog(file_path, self)
        preview_dialog.exec()

    def delete_screenshot(self):
        current_item = self.screenshot_list.currentItem()
        if current_item:
            reply = QMessageBox.question(self, 'Delete Screenshot',
                                         'Are you sure you want to delete this screenshot?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                file_path = current_item.data(Qt.UserRole)
                os.remove(file_path)
                self.load_saved_screenshots()
                self.image_label.clear()


class ScreenCapture(QWidget):
    screenshot_taken = Signal(QPixmap)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black;")
        self.setWindowOpacity(0.3)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self.rubberband = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubberband.setGeometry(QRect(self.origin, QSize()))
            self.rubberband.show()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            self.rubberband.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.rubberband.hide()
            rect = self.rubberband.geometry()
            self.take_screenshot(rect)

    def take_screenshot(self, rect):
        screen = QApplication.primaryScreen()
        pixmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
        self.screenshot_taken.emit(pixmap)
        self.close()


class SaveDialog(QDialog):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Screenshot")
        self.pixmap = pixmap

        layout = QVBoxLayout(self)

        self.label = QLabel()
        self.label.setPixmap(pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(self.label)
        layout.addWidget(button_box)


class ImagePreviewDialog(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Preview")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        content = QWidget()
        scroll_area.setWidget(content)

        content_layout = QVBoxLayout(content)

        label = QLabel()
        pixmap = QPixmap(image_path)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(label)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tool = ScreenshotTool()
    tool.show()
    sys.exit(app.exec())