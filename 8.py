import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                               QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
                               QRubberBand, QDialog, QDialogButtonBox, QListWidgetItem,
                               QScrollArea, QMessageBox, QGridLayout)
from PySide6.QtGui import QPixmap, QScreen, QPainter, QColor, QIcon, QGuiApplication
from PySide6.QtCore import Qt, QRect, QPoint, Signal, QSize
from PySide6.QtWidgets import QStyle
from PySide6.QtWidgets import QToolTip



from PySide6.QtWidgets import QRubberBand
from PySide6.QtGui import QImage, QPainter

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
        self.setGeometry(100, 100, 600, 500)  # 调整窗口大小

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Top area: buttons with blue background
        top_widget = QWidget()
        top_widget.setStyleSheet("""
                    background-color: #4287f5;
                """)
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(20)

        # Create buttons with new style
        button_style = """
                    QPushButton {
                        background-color: transparent;
                        color: black;
                        border: none;
                        padding: 5px 10px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 0.2);
                    }
                    QPushButton:pressed {
                        background-color: rgba(255, 255, 255, 0.3);
                    }
                """

        self.capture_button = QPushButton("截图")
        self.capture_button.setStyleSheet(button_style)
        self.capture_button.clicked.connect(self.start_capture)

        # Add title label
        self.title_label = QLabel("截图板")
        self.title_label.setStyleSheet("""
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                """)

        self.delete_all_button = QPushButton("全部清空")
        self.delete_all_button.setStyleSheet(button_style)
        self.delete_all_button.clicked.connect(self.delete_all_screenshots)

        top_layout.addWidget(self.capture_button)
        top_layout.addStretch()
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.delete_all_button)

        self.layout.addWidget(top_widget)

        # Bottom area: content with pink background
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("background-color: #FFC0CB;")
        bottom_layout = QVBoxLayout(bottom_widget)

        # Screenshot list
        self.screenshot_list = QListWidget()
        self.screenshot_list.setIconSize(QSize(100, 100))
        self.screenshot_list.setResizeMode(QListWidget.Adjust)
        self.screenshot_list.setSpacing(10)
        self.screenshot_list.itemDoubleClicked.connect(self.show_full_screenshot)

        # Refresh button
        self.refresh_button = QPushButton("Refresh List")
        self.refresh_button.clicked.connect(self.load_saved_screenshots)
        self.refresh_button.setStyleSheet("""
                    background-color: white;
                    color: #4287f5;
                    padding: 5px;
                    border: none;
                    border-radius: 3px;
                """)

        bottom_layout.addWidget(self.screenshot_list)
        bottom_layout.addWidget(self.refresh_button)

        self.layout.addWidget(bottom_widget)

        self.load_saved_screenshots()

    def create_tab_button(self, text, icon_path):
        button = QPushButton(text)
        button.setIcon(QIcon(icon_path))
        button.setStyleSheet("""
            QPushButton {
                background-color: #3268c7;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2758b3;
            }
            QPushButton:pressed {
                background-color: #1e4c9a;
            }
        """)
        return button
    def start_capture(self):
        self.hide()
        self.screen_capture = ScreenCapture()
        self.screen_capture.screenshot_taken.connect(self.handle_screenshot)
        self.screen_capture.show()

    # def handle_screenshot(self, pixmap, rect):
    #     self.show()
    #     if pixmap:
    #         save_dialog = SaveDialog(pixmap, rect, self)
    #         if save_dialog.exec() == QDialog.Accepted:
    #             filename = f"screenshot_{len(os.listdir('screenshots')) + 1}.png"
    #             pixmap.save(os.path.join("screenshots", filename))
    #             self.load_saved_screenshots()

    def handle_screenshot(self, pixmap, rect):
        if pixmap:
            save_dialog = SaveDialog(pixmap, rect, self)
            result = save_dialog.exec()
            if result == QDialog.Accepted:
                filename = f"screenshot_{len(os.listdir('screenshots')) + 1}.png"
                pixmap.save(os.path.join("screenshots", filename))
                self.load_saved_screenshots()
            self.show()  # Show the main window after the dialog is closed

    def load_saved_screenshots(self):
        self.screenshot_list.clear()
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        for filename in os.listdir("screenshots"):
            file_path = os.path.join("screenshots", filename)
            pixmap = QPixmap(file_path)
            item_widget = ScreenshotItem(pixmap, filename)
            item_widget.delete_button.clicked.connect(lambda checked=False, fp=file_path: self.delete_screenshot(fp))

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


class ScreenCapture(QWidget):
    screenshot_taken = Signal(QPixmap, QRect)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color:black")
        self.setWindowOpacity(0.3)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.begin = QPoint()
        self.end = QPoint()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)

    def mousePressEvent(self, event):
        self.begin = event.position().toPoint()
        self.end = self.begin
        self.rubberBand.setGeometry(QRect(self.begin, self.end))
        self.rubberBand.show()

    def mouseMoveEvent(self, event):
        self.end = event.position().toPoint()
        self.rubberBand.setGeometry(QRect(self.begin, self.end).normalized())

    def mouseReleaseEvent(self, event):
        self.rubberBand.hide()
        rect = QRect(self.begin, self.end).normalized()
        if rect.width() > 0 and rect.height() > 0:
            screen = QApplication.primaryScreen()
            pixmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
            self.screenshot_taken.emit(pixmap, rect)
        self.close()


class SaveDialog(QDialog):
    def __init__(self, pixmap, rect, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowTitle("Save Screenshot")
        self.pixmap = pixmap
        self.setStyleSheet("background-color: transparent;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Image container
        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel()
        self.label.setPixmap(pixmap)
        image_layout.addWidget(self.label)
        main_layout.addWidget(image_container)

        # Buttons container
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setAlignment(Qt.AlignBottom | Qt.AlignRight)

        # Create buttons
        self.save_button = QPushButton()
        self.save_button.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        self.save_button.clicked.connect(self.accept)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border-radius: 15px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.cancel_button = QPushButton()
        self.cancel_button.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border-radius: 15px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)

        # Set button size
        button_size = 30
        self.save_button.setFixedSize(button_size, button_size)
        self.cancel_button.setFixedSize(button_size, button_size)

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)

        main_layout.addWidget(buttons_container)

        self.adjustSize()
        self.move(rect.topLeft())

    # ... (其他方法保持不变)


class SelectionDialog(QDialog):
    def __init__(self, image, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.image = image
        self.setGeometry(QGuiApplication.primaryScreen().geometry())
        self.setStyleSheet("background-color: transparent;")
        self.setWindowOpacity(0.3)

        self.rubberband = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(self.rect(),
                          QImage(self.image.data, self.image.shape[1], self.image.shape[0], QImage.Format_RGB888))

    def mousePressEvent(self, event):
        self.origin = event.position().toPoint()
        self.rubberband.setGeometry(QRect(self.origin, QSize()))
        self.rubberband.show()

    def mouseMoveEvent(self, event):
        self.rubberband.setGeometry(QRect(self.origin, event.position().toPoint()).normalized())

    def mouseReleaseEvent(self, event):
        self.rubberband.hide()
        self.accept()

    def get_selection(self):
        return self.rubberband.geometry()


import os
import time
import threading
from PySide6.QtWidgets import QWidget, QToolTip
from PySide6.QtGui import QPainter, QColor, QIcon, QPixmap
from PySide6.QtCore import (Qt, QRect, QSize, QPoint, QTimer,
                            QPropertyAnimation, QEasingCurve, Property, Signal, Slot)


def get_tooltip_text():
    # 这里模拟从接口获取数据，实际使用时替换为真实的API调用
    time.sleep(1)  # 等待1秒
    return "这是从接口获取的提示文本"


class OverlayWidget(QWidget):
    tooltip_ready = Signal(str)
    loading_finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)

        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "icons", "info_icon.png"))
        self.icon = QIcon(icon_path)
        self.icon_size = QSize(30, 30)
        self.icon_rect = QRect()

        # 加载动画
        loader_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "icons", "loading.gif"))
        self.loader_pixmap = QPixmap(loader_path)
        self.loader_rect = QRect()
        self._rotation = 0
        self.animation = QPropertyAnimation(self, b"rotation")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.setLoopCount(-1)  # 无限循环
        self.animation.setEasingCurve(QEasingCurve.Linear)

        self.tooltip_text = ""
        self.tooltip_timer = QTimer(self)
        self.tooltip_timer.setSingleShot(True)
        self.tooltip_timer.timeout.connect(self.fetch_tooltip)

        self.is_loading = False

        # 连接信号到槽
        self.tooltip_ready.connect(self.show_tooltip)
        self.loading_finished.connect(self.on_loading_finished)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        # 计算图标位置 (右下角七分之三处)
        icon_x = int(width * (1 - 3 / 7) - self.icon_size.width() / 2)
        icon_y = int(height * (1 - 3 / 7) - self.icon_size.height() / 2)
        self.icon_rect = QRect(icon_x, icon_y, self.icon_size.width(), self.icon_size.height())

        # 绘制半透明白色背景
        painter.setBrush(QColor(255, 255, 255, 200))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.icon_rect)

        if self.is_loading:
            # 绘制加载动画
            painter.save()
            painter.translate(self.icon_rect.center())
            painter.rotate(self._rotation)
            painter.translate(-self.icon_rect.center())
            painter.drawPixmap(self.icon_rect, self.loader_pixmap)
            painter.restore()
        else:
            # 绘制图标
            self.icon.paint(painter, self.icon_rect)

    def mouseMoveEvent(self, event):
        if self.icon_rect.contains(event.position().toPoint()):
            if not self.tooltip_timer.isActive() and not self.is_loading:
                self.tooltip_timer.start(100)  # 100ms后开始加载
        else:
            self.tooltip_timer.stop()
            QToolTip.hideText()

    def fetch_tooltip(self):
        self.is_loading = True
        self.animation.start()
        self.update()

        def fetch():
            tooltip_text = get_tooltip_text()
            self.tooltip_ready.emit(tooltip_text)
            self.loading_finished.emit()

        threading.Thread(target=fetch, daemon=True).start()

    @Slot(str)
    def show_tooltip(self, text):
        self.tooltip_text = text
        cursor_pos = self.mapToGlobal(self.mapFromGlobal(self.cursor().pos()))
        QToolTip.showText(cursor_pos, self.tooltip_text)

    @Slot()
    def on_loading_finished(self):
        self.is_loading = False
        self.animation.stop()
        self.update()

    def leaveEvent(self, event):
        self.tooltip_timer.stop()
        QToolTip.hideText()

    def get_rotation(self):
        return self._rotation

    def set_rotation(self, rotation):
        if self._rotation != rotation:
            self._rotation = rotation
            self.update()

    rotation = Property(int, get_rotation, set_rotation)


class ImagePreviewDialog(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Preview")
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 图片区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        self.content = QWidget()
        self.scroll_area.setWidget(self.content)

        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.image_label)

        self.original_pixmap = QPixmap(image_path)
        self.scale_factor = 0.75
        self.updateImageSize()

        # 添加覆盖层
        self.overlay = OverlayWidget(self.image_label)
        self.overlay.resize(self.image_label.size())
        self.overlay.lower()

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        scaled_size = self.original_pixmap.size() * self.scale_factor
        self.resize(scaled_size)

        self.centerOnScreen()

        # 添加覆盖层
        self.overlay = OverlayWidget(self.image_label)
        self.overlay.setGeometry(self.image_label.rect())
        self.overlay.raise_()  # 确保覆盖层在最上层
        self.overlay.show()

    def updateImageSize(self):
        scaled_pixmap = self.original_pixmap.scaled(
            self.original_pixmap.size() * self.scale_factor,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        if hasattr(self, 'overlay'):
            self.overlay.resize(self.image_label.size())

    def centerOnScreen(self):
        screen = self.screen().availableGeometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)


    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'overlay'):
            self.overlay.setGeometry(self.image_label.rect())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    tool = ScreenshotTool()
    tool.show()
    sys.exit(app.exec())