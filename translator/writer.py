import os
from reportlab.lib import colors, pagesizes, units
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
)
from book import Book, ContentType, Content, ImageContent
from reportlab.lib.units import inch
from spire.pdf import *
from spire.pdf.common import *


class Writer:
    def __init__(self):
        pass

    def save_translated_book_pdf(self, book: Book, output_file_path: str = None):
        if output_file_path is None:
            output_file_path = book.pdf_file_path.replace('.pdf', f'_translated.pdf')

        font_path = "simsun.ttc"
        pdfmetrics.registerFont(TTFont("SimSun", font_path))
        # Create a new ParagraphStyle with the SimSun font
        simsun_style = ParagraphStyle('SimSun', fontName='SimSun', fontSize=12, leading=14)

        doc = SimpleDocTemplate(output_file_path, pagesize=pagesizes.letter)
        story = []

        for page in book.pages:
            for content in page.contents:
                if content.status:
                    print(f"写入文件中识别到的类型为: {content.content_type}+ {ContentType}")

                    if content.content_type == ContentType.TEXT:
                        text = content.translation
                        for line in text.split('\n'):

                            para = Paragraph(line, simsun_style)

                            story.append(para)


                    elif content.content_type == ContentType.TABLE:
                        table = content.translation
                        table_style = TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'SimSun'),
                            ('FONTSIZE', (0, 0), (-1, 0), 14),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('FONTNAME', (0, 1), (-1, -1), 'SimSun'),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)
                        ])
                        pdf_table = Table([table.columns.tolist()] + table.values.tolist())
                        pdf_table.setStyle(table_style)
                        story.append(pdf_table)
                        story.append(Spacer(1, 12))  # 添加间距

                # 处理图片
                if isinstance(content, ImageContent):
                    img_path = content.img_path
                    img = Image(img_path)

                    # 获取图像的原始尺寸
                    original_width, original_height = img.imageWidth, img.imageHeight

                    # 设置图像的尺寸为原始尺寸，确保不超过页面大小
                    max_width, max_height = pagesizes.letter[0] - 2 * inch, pagesizes.letter[1] - 2 * inch
                    width_ratio = max_width / original_width
                    height_ratio = max_height / original_height
                    scale_ratio = min(width_ratio, height_ratio, 1.0)  # 确保不放大，只缩小

                    img.drawWidth = original_width * scale_ratio
                    img.drawHeight = original_height * scale_ratio
                    story.append(img)

            if page != book.pages[-1]:
                story.append(PageBreak())

        doc.build(story)
