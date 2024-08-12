import time
from typing import Optional
from translator.pdf_parser import PDFParser
from translator.writer import Writer
from book import ContentType
from openai import OpenAI
from zhipuai import ZhipuAI
import pandas as pd  # 引入 pandas
import os
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


class TranslationChain:
    def __init__(self, model_name: str = None, openai_api_key=None, openai_api_base=None):

        # 翻译任务指令始终由 System 角色承担
        template = (
            """You are a translation expert, proficient in various languages. \n
            Translates to {target_language}."""
        )
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)

        # 待翻译文本由 Human 角色输入
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        # 使用 System 和 Human 角色的提示模板构造 ChatPromptTemplate
        chat_prompt_template = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        # 为了翻译结果的稳定性，将 temperature 设置为 0
        chat = ChatOpenAI(model=model_name,
                          openai_api_key=openai_api_key,
                          openai_api_base=openai_api_base,

                          )

        self.chain = LLMChain(llm=chat, prompt=chat_prompt_template, verbose=True)

    def run(self, text: str, target_language: str) -> (str, bool):
        result = ""
        try:
            result = self.chain.invoke({
                "text": text,

                "target_language": target_language,
            })
        except Exception as e:

            return result, False

        return result['text'], True


# 修改prompt（根据类型选择不同的prompt) 或者 试着用llmchain
class PDFTranslator:
    def __init__(self,model_name=None, openai_api_key=None, openai_api_base=None):
        self.chain = None
        self.pdf_parser = PDFParser()
        self.model_name = model_name
        self.writer = Writer()
        self.openai_api_key = openai_api_key
        self.openai_api_base = openai_api_base
        self.translate_chain = TranslationChain(model_name, openai_api_key, openai_api_base)

    def translate_pdf(self,
                      pdf_file_path: str,
                      target_language: str = 'Chinese',
                      output_file_path: str = None,
                      pages: Optional[int] = None):

        self.book = self.pdf_parser.parse_pdf(pdf_file_path, pages)
        for page_idx, page in enumerate(self.book.pages):
            for content_idx, content in enumerate(page.contents):
                # 判断内容类型，区分文本和表格

                translation, status = self.translate_chain.run(content,
                                                               target_language
                                                               )
                print(f"传输出来的文本翻译结果是：{translation}")

                self.book.pages[page_idx].contents[content_idx].set_translation(translation, status)

        self.writer.save_translated_book_pdf(self.book, output_file_path)
