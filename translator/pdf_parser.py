import pdfplumber
from typing import Optional
from book import Book, Content, ContentType, TableContent, Page, ImageContent
from translator.exceptions import PageOutOfRangeException
from PIL import Image as PILImage
from io import BytesIO
import tempfile
from spire.pdf import *
from spire.pdf.common import *
import re
import os
import fitz


class PDFParser:
    def __init__(self):
        pass

    def parse_pdf(self, pdf_file_path: str, pages: Optional[int] = None) -> Book:
        book = Book(pdf_file_path)

        # 提取图像
        file = pdf_file_path
        # 打开 PDF 文件
        pdf_file = fitz.open(file)

        with pdfplumber.open(pdf_file_path) as pdf:
            if pages is not None and pages > len(pdf.pages):
                raise PageOutOfRangeException(len(pdf.pages), pages)

            if pages is None:
                pages_to_parse = pdf.pages
            else:
                pages_to_parse = pdf.pages[:pages]

            for page_index, pdf_page in enumerate(pages_to_parse):
                page = Page()
                raw_text = pdf_page.extract_text()
                tables = pdf_page.extract_tables()
                print(f"刚开始提取时的{tables}")
                # 提取图像
                extracted_images = []
                page_ = pdf_file[page_index]
                images = page_.get_images(full=True)
                # Process tables first and get their text positions

                #检测位置
                table_positions = []
                if tables:
                    for table in tables:

                        for row in table:
                            if row:
                                table_text = ' '.join(map(str, row))
                                table_positions.append(re.escape(table_text))
                print(f"if tables后的{tables}")

                # 剔除表格
                if raw_text:
                    for table_pos in table_positions:
                        raw_text = re.sub(table_pos, '', raw_text)

                print(f"if raw_text后的{tables}")

                if images:
                    print(f"[+] 在页面：{page_index}，总共发现 {len(images)} 张图片。")
                else:
                    print(f"[+] 在页面：{page_index}，没有发现图片。")

                for img in images:
                    xref = img[0]
                    x, y, width, height = img[1], img[2], img[3], img[4]
                    pix = fitz.Pixmap(pdf_file, xref)

                    if pix.n < 5:  # this is GRAY or RGB
                        img_path = f'image{page_index + 1}_{xref}.png'
                        pix.save(img_path)
                        extracted_images.append(
                            ImageContent(img_path, x, y, width, height, page_index, ContentType.IMAGE, img))
                    else:  # CMYK: convert to RGB first
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                        img_path = f'image{page_index + 1}_{xref}.png'
                        pix.save(img_path)
                        extracted_images.append(
                            ImageContent(img_path, x, y, width, height, page_index, ContentType.IMAGE, img))

                if raw_text:
                    raw_text_lines = raw_text.splitlines()
                    cleaned_raw_text_lines = []
                    for i, line in enumerate(raw_text_lines):
                        # 如果下一行是空行，则保留当前行
                        if i < len(raw_text_lines) - 1 and not raw_text_lines[i + 1].strip():
                            cleaned_raw_text_lines.append(line)
                        # 如果当前行是最后一行，则直接保留
                        elif i == len(raw_text_lines) - 1:
                            cleaned_raw_text_lines.append(line.strip())
                        # 如果当前行不是最后一行，且下一行不是空行，则去除首尾空白
                        elif line.strip():
                            cleaned_raw_text_lines.append(line.strip())

                    cleaned_raw_text = "\n".join(cleaned_raw_text_lines)
                    text_content = Content(content_type=ContentType.TEXT, original=cleaned_raw_text)
                    page.add_content(text_content)


                if tables:
                    table_content = TableContent(table)
                    page.add_content(table_content)


                if extracted_images:
                    for img_content in extracted_images:
                        page.add_content(img_content)

                book.add_page(page)

        return book
