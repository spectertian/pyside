import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                               QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
                               QRubberBand, QDialog, QDialogButtonBox)
from PySide6.QtGui import QPixmap, QScreen, QPainter, QColor
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
        self.screenshot_list.itemClicked.connect(self.show_screenshot)

        self.delete_button = QPushButton("Delete Screenshot")
        self.delete_button.clicked.connect(self.delete_screenshot)

        left_layout.addWidget(self.capture_button)
        left_layout.addWidget(self.screenshot_list)
        left_layout.addWidget(self.delete_button)

        # Right side: image preview
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(left_widget)
        self.layout.addWidget(self.image_label)

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
            self.screenshot_list.addItem(filename)

    def show_screenshot(self, item):
        filename = item.text()
        pixmap = QPixmap(os.path.join("screenshots", filename))
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def delete_screenshot(self):
        current_item = self.screenshot_list.currentItem()
        if current_item:
            filename = current_item.text()
            os.remove(os.path.join("screenshots", filename))
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tool = ScreenshotTool()
    tool.show()
    sys.exit(app.exec())