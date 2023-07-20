import json
import os
import sys
from json import JSONEncoder

from PIL import Image
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QFileDialog, QMessageBox, \
    QVBoxLayout, QHBoxLayout, QWidget


class NewQLineEdit(QtWidgets.QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = [u for u in event.mimeData().urls()]
        for url in urls:
            self.setText(url.path()[1:])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置程序标题和图标
        self.setWindowTitle("Image to JSON Converter")
        self.setWindowIcon(QIcon(self.getPath("assets/Icon.svg")))
        self.resize(400, 380)

        # 添加标题
        title_label = QLabel("Image to JSON Converter", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 20, QFont.Bold)
        title_label.setFont(title_font)

        # 主窗口布局
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 添加标题部分并居中
        main_layout.addStretch(1)
        main_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        main_layout.addStretch(1)

        # 图片路径部分布局
        image_path_layout = QHBoxLayout()
        self.image_path_button = QPushButton("选择图片路径", self)
        self.image_path_label = NewQLineEdit("", self)
        self.image_path_label.setPlaceholderText("请输入图片路径或拖入图片")
        self.image_path_button.clicked.connect(self.select_image_path)
        image_path_layout.addWidget(self.image_path_button)
        image_path_layout.addWidget(self.image_path_label)
        main_layout.addLayout(image_path_layout)

        # 输出路径部分布局
        output_path_layout = QHBoxLayout()
        self.output_path_button = QPushButton("选择输出路径", self)
        self.output_path_label = QLineEdit("", self)
        self.output_path_label.setPlaceholderText("请输入输出路径")
        self.output_path_button.clicked.connect(self.select_output_path)
        output_path_layout.addWidget(self.output_path_button)
        output_path_layout.addWidget(self.output_path_label)
        main_layout.addLayout(output_path_layout)

        # 转换按钮
        self.convert_button = QPushButton("点击转换", self)
        self.convert_button.clicked.connect(self.convert_image_to_json)
        self.convert_button.setMinimumHeight(self.convert_button.height() * 2)
        main_layout.addWidget(self.convert_button)

        # 显示版权信息
        current_year = QDate.currentDate().year()
        copy_right_text = "© 2021-{} <a style='color:black;' href='https://www.vastsea.cc/'>瀚海工艺-Vastsea</a> 保留所有权利".format(
            current_year)
        self.copy_right_label = QLabel(copy_right_text, self)
        self.copy_right_label.setAlignment(Qt.AlignCenter)
        self.copy_right_label.setOpenExternalLinks(True)  # 设置为True，使超链接在浏览器中打开
        main_layout.addStretch(1)  # 添加弹性空间，将版权信息推至底部
        main_layout.addWidget(self.copy_right_label)

    def select_image_path(self):
        # 选择要导入的PNG图片
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择图片", "", "PNG 图片 (*.png)")
        if file_path:
            self.image_path_label.setText(file_path)
            self.image_path_label.setStyleSheet("color: black;")
        else:
            self.image_path_label.setText("")
            self.image_path_label.setStyleSheet("color: gray;")

    def select_output_path(self):
        # 选择输出路径
        file_dialog = QFileDialog()
        dir_path = file_dialog.getExistingDirectory(self, "选择输出路径")
        if dir_path:
            self.output_path_label.setText(dir_path)
            self.output_path_label.setStyleSheet("color: black;")
        else:
            self.output_path_label.setText("")
            self.output_path_label.setStyleSheet("color: gray;")

    def convert_image_to_json(self):
        image_path = self.image_path_label.text()
        output_path = self.output_path_label.text()

        # 判断是否填写了图片路径和输出路径
        if not image_path and not output_path:
            self.image_path_label.setText("")
            self.image_path_label.setStyleSheet("color: red;")
            self.output_path_label.setText("")
            self.output_path_label.setStyleSheet("color: red;")
        elif not image_path:
            self.image_path_label.setText("")
            self.image_path_label.setStyleSheet("color: red;")
        elif not output_path:
            self.output_path_label.setText("")
            self.output_path_label.setStyleSheet("color: red;")
        else:
            # 使用 Pillow 加载图片
            try:
                image = Image.open(image_path).convert("L")
                image = image.resize((64, 64), Image.BICUBIC)
                pixels = list(image.getdata())
            except Exception as e:
                self.image_path_label.setStyleSheet("color: red;")
                QMessageBox.warning(self, "错误", "无法加载或处理图像文件！\n\n错误信息：{}".format(str(e)))
                return

            # 转换为二值图像
            grid = []
            row = []
            for i, pixel in enumerate(pixels, start=1):
                value = 0 if pixel == 0 else 1
                row.append(value)
                if i % 64 == 0:
                    grid.append(row)
                    row = []

            # 创建JSON对象
            json_data = {"grid": grid}

            # 将 JSON 数据转换为字符串
            json_string = json.dumps(json_data, separators=(",", ": "), indent=4, cls=JSONEncoder)

            # 修改字符串格式，添加换行符和空格
            json_string = json_string.replace("[\n    [", "[\n        [") \
                .replace("],\n    [", "],\n        [").replace("    ]\n]", "        ]\n    ]") \
                .replace("\n            1,", "1,").replace("\n            0,", "0,") \
                .replace("\n            1", "1").replace("\n            0", "0") \
                .replace("\n        ],", "],").replace("\n        ]", "]")

            # 生成JSON文件名
            json_file_path = os.path.join(output_path, os.path.splitext(os.path.basename(image_path))[0] + ".json")

            # 保存为JSON文件
            with open(json_file_path, "w") as json_file:
                json_file.write(json_string)

            QMessageBox.information(self, "成功", "图片已成功转换为JSON文件！")

    @staticmethod
    def getPath(path: str):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, path)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 加载自定义字体文件
    font_path = MainWindow.getPath("assets/HarmonyOS_Sans_SC_Regular.ttf")
    font_id = QFontDatabase.addApplicationFont(font_path)
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    app.setFont(QFont(font_family, 10))

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
