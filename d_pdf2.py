import cv2
import numpy as np
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
from openpyxl import Workbook


# 设置 Tesseract 路径（如果需要的话）
# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

def preprocess_image(image):
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 应用自适应阈值
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return thresh


def detect_lines(image):
    # 检测水平线和垂直线
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

    horizontal_lines = cv2.erode(image, horizontal_kernel, iterations=3)
    horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=3)

    vertical_lines = cv2.erode(image, vertical_kernel, iterations=3)
    vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=3)

    return horizontal_lines, vertical_lines


def find_intersections(h_lines, v_lines):
    # 找到线的交点
    intersections = cv2.bitwise_and(h_lines, v_lines)
    return cv2.findNonZero(intersections)


def extract_table_data(image, intersections):
    # 根据交点提取单元格数据
    intersections = np.squeeze(intersections)
    intersections = sorted(intersections, key=lambda x: (x[1], x[0]))

    rows = []
    current_row = []
    last_y = intersections[0][1]

    for point in intersections:
        if point[1] - last_y > 10:  # 新行
            rows.append(current_row)
            current_row = []
        current_row.append(point)
        last_y = point[1]

    if current_row:
        rows.append(current_row)

    table_data = []
    for i in range(len(rows) - 1):
        row_data = []
        for j in range(len(rows[i]) - 1):
            x1, y1 = rows[i][j]
            x2, y2 = rows[i + 1][j + 1]
            cell = image[y1:y2, x1:x2]
            text = pytesseract.image_to_string(cell, config='--psm 6')
            row_data.append(text.strip())
        table_data.append(row_data)

    return table_data


def process_pdf(pdf_path):
    # 将 PDF 转换为图片
    images = convert_from_path(pdf_path)

    all_data = []

    for image in images:
        # 将 PIL 图像转换为 OpenCV 格式
        open_cv_image = np.array(image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()

        # 预处理图像
        preprocessed = preprocess_image(open_cv_image)

        # 检测线条
        h_lines, v_lines = detect_lines(preprocessed)

        # 找到交点
        intersections = find_intersections(h_lines, v_lines)

        # 提取表格数据
        table_data = extract_table_data(open_cv_image, intersections)

        all_data.extend(table_data)

    return all_data


# 主程序
pdf_path = "doc/20240820200038923.pdf"
excel_path = "doc/output.xlsx"


# 处理 PDF 并提取数据
data = process_pdf(pdf_path)

# 创建 DataFrame
df = pd.DataFrame(data)

# 保存到 Excel
with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
    df.to_excel(writer, index=False)

print(f"数据已成功保存到 {excel_path}")