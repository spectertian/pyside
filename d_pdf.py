import cv2
import numpy as np
import pandas as pd
from pdf2image import convert_from_path
import pytesseract
from openpyxl import Workbook


# 设置 Tesseract 路径（Windows 用户需要设置）
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image):
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 应用阈值处理
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    return thresh


def find_table_cells(image):
    # 查找轮廓
    contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # 按面积排序，只保留较大的轮廓（可能是单元格）
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:100]
    return contours


def extract_cell_content(image, contour):
    x, y, w, h = cv2.boundingRect(contour)
    cell = image[y:y + h, x:x + w]
    # 使用 OCR 识别单元格内容
    text = pytesseract.image_to_string(cell, config='--psm 6')
    return text.strip()


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

        # 查找表格单元格
        cells = find_table_cells(preprocessed)

        # 提取每个单元格的内容
        table_data = [extract_cell_content(open_cv_image, cell) for cell in cells]

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