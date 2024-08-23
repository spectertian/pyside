from paddleocr import PaddleOCR
from pdf2image import convert_from_path
import pandas as pd
import numpy as np


def extract_table_from_image(image):
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')
    result = ocr.ocr(image, cls=True)
    print(result)

    # 提取所有识别到的文本及其位置
    texts_with_positions = []
    for line in result:
        for word_info in line:
            position = word_info[0]
            text = word_info[1][0]
            x = (position[0][0] + position[1][0] + position[2][0] + position[3][0]) / 4
            y = (position[0][1] + position[1][1] + position[2][1] + position[3][1]) / 4
            texts_with_positions.append((text, x, y))

    # 根据y坐标对文本进行分组，形成行
    sorted_texts = sorted(texts_with_positions, key=lambda x: x[2])

    print(sorted_texts)
    rows = []
    current_row = []
    last_y = sorted_texts[0][2]
    for text, x, y in sorted_texts:
        if abs(y - last_y) > 10:  # 假设新的一行
            rows.append(sorted(current_row, key=lambda x: x[1]))
            current_row = []
        current_row.append((text, x))
        last_y = y
    if current_row:
        rows.append(sorted(current_row, key=lambda x: x[1]))

    # 将行转换为DataFrame
    table_data = [[cell[0] for cell in row] for row in rows]
    return pd.DataFrame(table_data)


def process_pdf(pdf_path):
    # 将PDF转换为图像
    images = convert_from_path(pdf_path)

    all_tables = []
    for img in images:
        # 将PIL Image转换为numpy数组
        img_np = np.array(img)
        table = extract_table_from_image(img_np)
        all_tables.append(table)

    # 合并所有表格
    final_table = pd.concat(all_tables, ignore_index=True)
    return final_table


# 主程序
pdf_path = "doc/20240820200038923.pdf"
excel_path = "output.xlsx"

# 处理PDF并提取数据
table_data = process_pdf(pdf_path)

# 保存到Excel
table_data.to_excel(excel_path, index=False)

print(f"数据已成功保存到 {excel_path}")