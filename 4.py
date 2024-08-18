import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                               QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
                               QRubberBand, QDialog, QDialogButtonBox, QListWidgetItem,
                               QScrollArea, QMessageBox, QGridLayout)
from PySide6.QtGui import QPixmap, QScreen, QPainter, QColor, QIcon
from PySide6.QtCore import Qt, QRect, QPoint, Signal, QSize


class ScreenshotItem(QWidget):
    def __init__(self, pixmap, filename, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.image_label = QLabel()
        self.image_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.image_label.setAlignment(Qt.AlignCenter)

        self.filename_label = QLabel(filename)
        self.filename_label.setAlignment(Qt.AlignCenter)

        self.delete_button = QPushButton("X")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4d;
                color: white;
                border-radius: 10px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff3333;
            }
        """)
        self.delete_button.setFixedSize(20, 20)

        layout.addWidget(self.image_label, 0, 0, 1, 2)
        layout.addWidget(self.delete_button, 0, 1, 1, 1, Qt.AlignTop | Qt.AlignRight)
        layout.addWidget(self.filename_label, 1, 0, 1, 2)


class ScreenshotTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screenshot Tool")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Top row: capture and delete all buttons
        top_row = QHBoxLayout()
        self.capture_button = QPushButton("Capture Screenshot")
        self.capture_button.clicked.connect(self.start_capture)
        self.capture_button.setStyleSheet("background-color: #4287f5; color: white; padding: 10px;")

        self.delete_all_button = QPushButton("Delete All Screenshots")
        self.delete_all_button.clicked.connect(self.delete_all_screenshots)
        self.delete_all_button.setStyleSheet("background-color: #4287f5; color: white; padding: 10px;")

        top_row.addWidget(self.capture_button)
        top_row.addWidget(self.delete_all_button)

        self.layout.addLayout(top_row)

        # Main content area
        content_layout = QHBoxLayout()

        # Left side: list and buttons
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.screenshot_list = QListWidget()
        self.screenshot_list.setIconSize(QSize(100, 100))
        self.screenshot_list.setResizeMode(QListWidget.Adjust)
        self.screenshot_list.setSpacing(10)
        self.screenshot_list.itemDoubleClicked.connect(self.show_full_screenshot)

        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.load_saved_screenshots)

        left_layout.addWidget(self.screenshot_list)
        left_layout.addWidget(self.refresh_button)

        # Right side: image preview
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        content_layout.addWidget(left_widget, 1)
        content_layout.addWidget(self.image_label, 2)

        self.layout.addLayout(content_layout)

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
            item_widget = ScreenshotItem(pixmap, filename)
            item_widget.delete_button.clicked.connect(lambda checked, fp=file_path: self.delete_screenshot(fp))

            item = QListWidgetItem(self.screenshot_list)
            item.setSizeHint(item_widget.sizeHint())
            self.screenshot_list.addItem(item)
            self.screenshot_list.setItemWidget(item, item_widget)

    def show_full_screenshot(self, item):
        item_widget = self.screenshot_list.itemWidget(item)
        file_path = os.path.join("screenshots", item_widget.filename_label.text())
        preview_dialog = ImagePreviewDialog(file_path, self)
        preview_dialog.exec()

    def delete_screenshot(self, file_path):
        reply = QMessageBox.question(self, 'Delete Screenshot',
                                     'Are you sure you want to delete this screenshot?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            os.remove(file_path)
            self.load_saved_screenshots()
            self.image_label.clear()

    def delete_all_screenshots(self):
        reply = QMessageBox.question(self, 'Delete All Screenshots',
                                     'Are you sure you want to delete all screenshots?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for filename in os.listdir("screenshots"):
                file_path = os.path.join("screenshots", filename)
                os.remove(file_path)
            self.load_saved_screenshots()
            self.image_label.clear()


# The rest of the classes (ScreenCapture, SaveDialog, ImagePreviewDialog) remain unchanged

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