import json
import os
import sys
from json import JSONEncoder

from PIL import Image
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置程序标题和图标
        self.setWindowTitle("Image to JSON Converter")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.resize(400, 380)

        # 创建选择图片路径按钮和标签
        self.image_path_button = QPushButton("选择图片路径", self)
        self.image_path_button.setGeometry(140, 50, 120, 30)
        self.image_path_button.clicked.connect(self.select_image_path)
        self.image_path_label = QLabel("请选择图片路径", self)
        self.image_path_label.setGeometry(50, 100, 300, 30)
        self.image_path_label.setAlignment(Qt.AlignCenter)

        # 创建选择输出路径按钮和标签
        self.output_path_button = QPushButton("选择输出路径", self)
        self.output_path_button.setGeometry(140, 150, 120, 30)
        self.output_path_button.clicked.connect(self.select_output_path)
        self.output_path_label = QLabel("请选择输出路径", self)
        self.output_path_label.setGeometry(50, 200, 300, 30)
        self.output_path_label.setAlignment(Qt.AlignCenter)

        # 创建转换按钮
        self.convert_button = QPushButton("转换", self)
        self.convert_button.setGeometry(140, 250, 120, 30)
        self.convert_button.clicked.connect(self.convert_image_to_json)

        # 显示版权信息
        current_year = QDate.currentDate().year()
        self.copy_right_label = QLabel("© 2021-{} 瀚海工艺-Vastsea 保留所有权利".format(current_year), self)
        self.copy_right_label.setGeometry(50, 310, 300, 30)
        self.copy_right_label.setAlignment(Qt.AlignCenter)

    def select_image_path(self):
        # 选择要导入的PNG图片
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择图片", "", "PNG 图片 (*.png)")
        if file_path:
            self.image_path_label.setText(file_path)
            self.image_path_label.setStyleSheet("color: black;")
        else:
            self.image_path_label.setText("请选择图片路径")
            self.image_path_label.setStyleSheet("color: red;")

    def select_output_path(self):
        # 选择输出路径
        file_dialog = QFileDialog()
        dir_path = file_dialog.getExistingDirectory(self, "选择输出路径")
        if dir_path:
            self.output_path_label.setText(dir_path)
            self.output_path_label.setStyleSheet("color: black;")
        else:
            self.output_path_label.setText("请选择输出路径")
            self.output_path_label.setStyleSheet("color: red;")

    def convert_image_to_json(self):
        image_path = self.image_path_label.text()
        output_path = self.output_path_label.text()

        # 判断是否填写了图片路径和输出路径
        if not image_path and not output_path:
            self.image_path_label.setText("请选择图片路径")
            self.image_path_label.setStyleSheet("color: red;")
            self.output_path_label.setText("请选择输出路径")
            self.output_path_label.setStyleSheet("color: red;")
        elif not image_path:
            self.image_path_label.setText("请选择图片路径")
            self.image_path_label.setStyleSheet("color: red;")
        elif not output_path:
            self.output_path_label.setText("请选择输出路径")
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
            json_string = json.dumps(json_data, separators=(",", ": "), indent=None, cls=JSONEncoder)

            # 生成JSON文件名
            json_file_path = os.path.join(output_path, os.path.splitext(os.path.basename(image_path))[0] + ".json")

            # 保存为JSON文件
            with open(json_file_path, "w") as json_file:
                json_file.write(json_string)

            self.image_path_label.setStyleSheet("color: green;")
            self.output_path_label.setStyleSheet("color: green;")
            QMessageBox.information(self, "成功", "图片已成功转换为JSON文件！")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
