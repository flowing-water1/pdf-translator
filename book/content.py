import pandas as pd
from enum import Enum, auto
from PIL import Image as PILImage


class ContentType(Enum):
    TEXT = auto()
    TABLE = auto()
    IMAGE = auto()


class Content:
    def __init__(self, content_type, original, translation=None):
        self.content_type = content_type
        self.original = original
        self.translation = translation
        self.status = False

    def set_translation(self, translation, status):
        if not self.check_translation_type(translation):
            raise ValueError(f"Invalid translation type. Expected {self.content_type}, but got {type(translation)}")
        self.translation = translation
        self.status = status

    def check_translation_type(self, translation):
        if self.content_type == ContentType.TEXT and isinstance(translation, str):
            return True
        elif self.content_type == ContentType.TABLE and isinstance(translation, list):
            return True
        elif self.content_type == ContentType.IMAGE:
            return True
        return False

    def __str__(self):
        return self.original


class TableContent(Content):
    def __init__(self, data, translation=None):
        df = pd.DataFrame(data)

        # Verify if the number of rows and columns in the data and DataFrame object match
        if len(data) != len(df) or len(data[0]) != len(df.columns):
            raise ValueError(
                "The number of rows and columns in the extracted table data and DataFrame object do not match.")

        super().__init__(ContentType.TABLE, df)

    # 重写设置翻译的函数
    def set_translation(self, translation, status):
        try:
            if not isinstance(translation, str):
                raise ValueError("翻译不正确，目标类型为str，但是却是{type(translation)}")

            # 将传入的表格分离开来，将每行的前后空格都去除，并为每行加上换行符分割成一个列表
            table_data = [row.strip().split() for row in translation.strip().split("\n")]
            # print(f"table_data: {table_data}")
            # 将刚才分离开的做成一个dataframe
            taranslated_df = pd.DataFrame(table_data[1:], columns=table_data[0])
            # print(f"taranslated_df: {taranslated_df}")
            # 重置状态和翻译内容
            self.translation = taranslated_df
            self.status = status

        except Exception as e:
            # 如果出错，重置状态和翻译内容
            self.translation = None
            self.status = False

    def __str__(self):
        # 返回原文
        return self.original.to_string(header=False, index=False)

    # 构成一个表格
    def iter_items(self, translated=None):
        # 将原来或者翻译好的表格传入
        target_df = self.translation if translated else self.original
        # 遍历表格，构成新的表格
        for row_idx, row in target_df.iterrows():
            for col_idx, item in enumerate(row):
                yield (row_idx, col_idx, item)

    def update_item(self, row_idx, col_idx, new_value, translated=False):
        # 更新表格内的内容
        target_df = self.translation if translated else self.original
        target_df.at[row_idx, col_idx] = new_value

    def get_original_as_str(self):
        # 返回原来的文本
        if isinstance(self.original, list):
            self.original = pd.DataFrame(self.original)
        print(f"Type of original content :{type(self.original)}")
        if isinstance(self.original, pd.DataFrame):
            return self.original.to_string(header=False, index=False)
        else:
            raise TypeError(f"期待的是DataFrame，但是现在是{type(self.original)}")


class ImageContent(Content):
    def __init__(self, img_path, x, y, width, height, page_index, content_type, original):
        super().__init__(ContentType.IMAGE, original)
        self.img_path = img_path
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.page_index = page_index
