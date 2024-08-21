import sys
import os
import time
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
                               QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
                               QRubberBand, QDialog, QDialogButtonBox, QListWidgetItem,
                               QScrollArea, QMessageBox, QGridLayout, QToolTip,QStyle)
from PySide6.QtGui import (QPixmap, QScreen, QPainter, QColor, QIcon, QGuiApplication,
                           QImage, QTransform)
from PySide6.QtCore import (Qt, QRect, QPoint, Signal, QSize, QPropertyAnimation,
                            QEasingCurve, Property, QEvent, QThread, QTimer)


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        self.label = QLabel(self)
        pixmap = QPixmap("icons/logo_big.png")  # 替换为您的启动画面图片路径
        self.label.setPixmap(pixmap)
        layout.addWidget(self.label)

        self.setFixedSize(pixmap.width()+120, pixmap.height()+140)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
class ScreenshotItem(QWidget):
    def __init__(self, pixmap, filename, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)  # 启用鼠标跟踪
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        # 创建一个容器来包含图片和删除按钮
        container = QWidget()
        container_layout = QGridLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 增大图片尺寸
        self.image_label = QLabel()
        self.image_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.image_label.setAlignment(Qt.AlignCenter)

        self.delete_button = QPushButton()
        delete_icon = QIcon("icons/remove_icon.png")  # 确保路径正确
        self.delete_button.setIcon(delete_icon)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 50);
            }
        """)
        self.delete_button.setFixedSize(24, 24)
        self.delete_button.setIconSize(self.delete_button.size())
        self.delete_button.hide()  # 初始时隐藏删除按钮

        # 将图片和删除按钮添加到容器中
        container_layout.addWidget(self.image_label, 0, 0)
        container_layout.addWidget(self.delete_button, 0, 0, Qt.AlignTop | Qt.AlignRight)

        layout.addWidget(container)

        # 存储文件名，但不显示
        self.filename = filename

    def enterEvent(self, event):
        self.delete_button.show()

    def leaveEvent(self, event):
        self.delete_button.hide()

    def sizeHint(self):
        return QSize(160, 160)
class ScreenshotTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("截图工具")
        self.setGeometry(100, 100, 200, 500)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Top area: buttons with blue background
        top_widget = QWidget()
        top_widget.setStyleSheet("background-color: #651FFF;")
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(10)

        # Logo icon
        icon_container = QWidget()
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignLeft)

        icon_label = QLabel()
        icon_pixmap = QPixmap("icons/logo_small.png")  # 替换为你的图标路径
        icon_label.setPixmap(icon_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon_layout.addWidget(icon_label)
        icon_layout.addStretch(1)  # 添加伸缩项，使图标左对齐

        top_layout.addWidget(icon_container)

        # Buttons container
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(20)

        # Create capture button with icon
        # 创建包含文字和图标的截图按钮
        # 创建包含文字和图标的截图按钮
        self.capture_button = QPushButton("截图")
        self.capture_button.setStyleSheet("""
            QPushButton {
                background-color: #651FFF;
                color: black;
                border: none;
                padding: 5px 10px;
                font-size: 14px;
                font-weight: bold;
                text-align: left;  /* 文字左对齐 */
            }
            QPushButton:hover {
                background-color: #3268c7;
            }
            QPushButton:pressed {
                background-color: #2758b3;
            }
        """)

        # 设置图标
        icon = QIcon("icons/cut_icon.png")  # 确保路径正确
        self.capture_button.setIcon(icon)
        self.capture_button.setIconSize(QSize(24, 24))  # 设置图标大小

        # 设置文字和图标的间距
        self.capture_button.setStyleSheet(self.capture_button.styleSheet() +
                                          "QPushButton { padding-left: 5px; padding-right: 10px; }")
        self.capture_button.clicked.connect(self.start_capture)
        # Add title label
        self.title_label = QLabel("截图板")
        self.title_label.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)

        # Add delete all button
        self.delete_all_button = QPushButton("全部清空")
        self.delete_all_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;  /* 透明背景 */
                color: black;
                border: none;  /* 无边框 */
                padding: 5px 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(50, 104, 199, 0.1);  /* 半透明的悬停效果 */
            }
            QPushButton:pressed {
                background-color: rgba(39, 88, 179, 0.2);  /* 半透明的按下效果 */
            }
        """)

        self.delete_all_button.clicked.connect(self.delete_all_screenshots)

        # buttons_layout.addWidget(capture_button_container)
        buttons_layout.addWidget(self.capture_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.title_label)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.delete_all_button)

        top_layout.addWidget(buttons_widget)

        self.layout.addWidget(top_widget)

        # Bottom area: content with pink background
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("background-color: #EFEFEF;")
        bottom_layout = QVBoxLayout(bottom_widget)

        # Screenshot list
        self.screenshot_list = QListWidget()
        self.screenshot_list.setIconSize(QSize(100, 100))
        self.screenshot_list.setResizeMode(QListWidget.Adjust)
        self.screenshot_list.setSpacing(10)
        self.screenshot_list.itemDoubleClicked.connect(self.show_full_screenshot)

        self.screenshot_list.setStyleSheet("""
            QListWidget::item:selected {
                background-color: transparent;
                border: 3px solid #E2974B;
                padding: 2px;
            }
            QListWidget::item:hover {
                background-color: transparent;
                border: 1px solid #E2974B;
            }
        """)

        bottom_layout.addWidget(self.screenshot_list)
        self.layout.addWidget(bottom_widget)

        self.load_saved_screenshots()

    def create_tab_button(self, text, icon_path):
        button = QPushButton()
        button_layout = QHBoxLayout(button)
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(5)

        text_label = QLabel(text)
        text_label.setStyleSheet("""
            color: black;
            font-size: 14px;
            font-weight: bold;
        """)

        icon_label = QLabel()
        icon_pixmap = QPixmap(icon_path)
        icon_label.setPixmap(icon_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        button_layout.addWidget(text_label)
        button_layout.addWidget(icon_label)
        button_layout.addStretch()

        button.setStyleSheet("""
            QPushButton {
                background-color: #3268c7;
                border: none;
                padding: 10px;
                text-align: left;
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
        file_path = os.path.join("screenshots", item_widget.filename)  # 使用 filename 属性
        preview_dialog = ImagePreviewDialog(file_path, self)
        preview_dialog.exec()

    def delete_screenshot(self, file_path):
        reply = QMessageBox.question(self, '删除图片',
                                     '是否要删除图片?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            os.remove(file_path)
            self.load_saved_screenshots()
            self.image_label.clear()

    def delete_all_screenshots(self):
        reply = QMessageBox.question(self, '删除全部图片',
                                     '是否要删除全部图片?',
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

        # Create buttons with icons
        self.save_button = QPushButton()
        save_icon = QIcon("icons/confirm_icon.png")
        self.save_button.setIcon(save_icon)
        self.save_button.setIconSize(QSize(40, 40))  # 增大图标尺寸
        self.save_button.clicked.connect(self.accept)
        self.save_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: rgba(76, 175, 80, 0.1);
                        border-radius: 20px;
                    }
                """)

        self.cancel_button = QPushButton()
        cancel_icon = QIcon("icons/cancel_icon.png")
        self.cancel_button.setIcon(cancel_icon)
        self.cancel_button.setIconSize(QSize(40, 40))  # 增大图标尺寸
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: rgba(244, 67, 54, 0.1);
                        border-radius: 20px;
                    }
                """)

        # Set button size
        button_size = 50  # 增大按钮尺寸
        self.save_button.setFixedSize(button_size, button_size)
        self.cancel_button.setFixedSize(button_size, button_size)

        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)

        main_layout.addWidget(buttons_container)

        self.adjustSize()
        self.move(rect.topLeft())

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


from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QMovie
from PySide6.QtCore import Qt, QSize
class RotatingLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)  # 设置固定大小
        self.setAttribute(Qt.WA_TranslucentBackground)  # 允许透明背景

        # 创建 QMovie 对象
        self.movie = QMovie("icons/loading.gif")
        self.movie.setScaledSize(QSize(40, 40))  # 设置 GIF 大小
        self.setMovie(self.movie)
        self.movie.start()

    def startAnimation(self):
        self.movie.start()

    def stopAnimation(self):
        self.movie.stop()

    # def setRotation(self, rotation):
    #     self._rotation = rotation
    #     self.update()
    #
    # def rotation(self):
    #     return self._rotation
    #
    # rotation = Property(float, rotation, setRotation)

    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     painter.setRenderHint(QPainter.Antialiasing)
    #     painter.setRenderHint(QPainter.SmoothPixmapTransform)
    #
    #     # 清除背景
    #     painter.eraseRect(self.rect())

        # 绘制旋转的图标
        # painter.translate(self.width() / 2, self.height() / 2)
        # painter.rotate(self._rotation)
        # painter.translate(-self._pixmap.width() / 2, -self._pixmap.height() / 2)
        # painter.drawPixmap(0, 0, self._pixmap)

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QWidget,
                               QHBoxLayout, QToolTip, QProgressBar)
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor,QEventPoint
from PySide6.QtCore import Qt, QPoint, QSize, Signal, QTimer, QThread, Signal
import time

class ImageInfoThread(QThread):
    info_received = Signal(str)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path

    def run(self):
        # 模拟异步获取图片信息的过程
        time.sleep(2)  # 模拟网络延迟
        # 这里应该是实际的API调用，获取图片信息
        info = f"图片路径: {self.image_path}\n大小: 1024x768\n格式: PNG\n创建时间: {time.ctime()}"
        self.info_received.emit(info)

class ImagePreviewDialog(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("预览")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.image_path = image_path

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 图片容器
        self.image_container = QWidget(self)
        self.image_container.setStyleSheet("background-color: white; border-radius: 10px;")
        image_layout = QVBoxLayout(self.image_container)
        image_layout.setContentsMargins(10, 10, 10, 10)

        # 图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(self.image_label)

        main_layout.addWidget(self.image_container)

        # 设置图片
        self.original_pixmap = QPixmap(image_path)
        self.updateImageSize()

        # 添加 OverlayWidget
        self.overlay = OverlayWidget(self.image_container)
        self.overlay.setGeometry(self.image_container.rect())

        # 添加关闭按钮
        self.close_button = QPushButton(self)
        self.close_button.setIcon(QIcon("icons/close_icon.png"))
        self.close_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 0, 0, 50);
                    }
                """)
        self.close_button.setFixedSize(40, 40)  # 增大按钮尺寸
        self.close_button.setIconSize(QSize(30, 30))  # 增大图标尺寸
        self.close_button.clicked.connect(self.close)

        # 添加加载动画
        self.loading_icon = RotatingLabel(self)
        self.loading_icon.setFixedSize(40, 40)
        self.loading_icon.hide()

        # 设置窗口大小和位置
        self.updateDialogSize()
        self.centerOnScreen()

        # 启动加载过程
        self.startLoading()

    def updateImageSize(self):
        screen = QGuiApplication.primaryScreen().geometry()
        max_width = int(screen.width() * 0.7)
        max_height = int(screen.height() * 0.7)

        scaled_pixmap = self.original_pixmap.scaled(
            max_width, max_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def updateDialogSize(self):
        image_size = self.image_label.pixmap().size()
        dialog_size = QSize(image_size.width() + 20, image_size.height() + 20)  # 20是边距
        self.setFixedSize(dialog_size.width() + 40, dialog_size.height() + 20)  # 为按钮预留空间
        self.image_container.setFixedSize(dialog_size)
        self.overlay.setGeometry(self.image_container.geometry())
        self.close_button.move(self.width() - 50, 10)  # 调整按钮位置

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.setGeometry(self.image_container.rect())
        self.close_button.move(self.width() - 50, 10)  # 调整按钮位置
        self.overlay.updateInfoButtonPosition()

    def centerOnScreen(self):
        screen = self.screen().availableGeometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)



    def startLoading(self):
        self.loading_icon.show()
        self.loading_icon.move(10, 10)  # 放在左上角
        self.loading_icon.startAnimation()

        # 创建并启动线程
        self.info_thread = ImageInfoThread(self.image_path)
        self.info_thread.info_received.connect(self.onInfoReceived)
        self.info_thread.start()

    def onInfoReceived(self, info):
        self.loading_icon.stopAnimation()
        self.loading_icon.hide()
        # 更新 OverlayWidget 中的信息
        self.overlay.setInfo(info)
class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)

        self.info_button = QPushButton(self)
        self.info_button.setIcon(QIcon("icons/info_icon.png"))  # 替换为实际的信息图标路径
        self.info_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 150);
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 200);
            }
        """)
        self.info_button.setFixedSize(30, 30)
        self.info_button.setCursor(Qt.PointingHandCursor)
        self.info_button.installEventFilter(self)

        self.info = "加载中..."

    def setInfo(self, info):
        self.info = info

    def eventFilter(self, obj, event):
        if obj == self.info_button:
            if event.type() == QEvent.Enter:
                self.showTooltip()
                return True
            elif event.type() == QEvent.Leave:
                self.hideTooltip()
                return True
        return super().eventFilter(obj, event)

    def showTooltip(self):
        QToolTip.showText(self.info_button.mapToGlobal(QPoint(0, self.info_button.height())),
                          self.info, self.info_button)

    def hideTooltip(self):
        QToolTip.hideText()

    def updateInfoButtonPosition(self):
        x = int(self.width() * 0.9)  # 90% 从左边
        y = int(self.height() * 0.1)  # 10% 从上边
        self.info_button.move(x - self.info_button.width(), y)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))  # 几乎完全透明的背景


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 显示启动画面
    splash = SplashScreen()
    splash.show()

    # 创建主窗口，但不要立即显示
    tool = ScreenshotTool()


    # 使用 QTimer 来控制启动画面的显示时间
    def show_main_window():
        splash.close()
        tool.show()


    QTimer.singleShot(500, show_main_window)  # 5000 毫秒 = 5 秒

    sys.exit(app.exec())