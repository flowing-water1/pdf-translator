import tempfile
import streamlit as st
from translator import PDFTranslator
import os
import pdfplumber
from streamlit_pdf_viewer import pdf_viewer

def target_language_check(target_language):
    if target_language == "中文":
        target_language = "Chinese"
    elif target_language == "日文":
        target_language = "Japanese"
    elif target_language == "英文":
        target_language = "English"
    elif target_language == "韩文":
        target_language = "Korean"
    return target_language


st.title("📔 AI智能PDF翻译工具")
with st.sidebar:
    tab1, tab2 = st.tabs(["OPENAI", "智谱"])
    with tab1:
        openai_api_key = st.text_input("OpenAI API Key:", type="password")
        openai_api_base = st.text_input("OpenAI API Base:")
        # openai_port = st.text_input("VPN的端口：")
        st.markdown("[获取OpenAI API key](https://platform.openai.com/account/api-keys)")
        st.markdown("[OpenAI API文档](https://platform.openai.com/docs/api-reference/introduction)")
        st.markdown("要用直连原版的API话，要开VPN，端口设置为7890。")
        st.markdown("用中转的不用开VPN，已测试过中转的跟直连的效果一样。")

    with tab2:
        zhipu_api_key = st.text_input("智谱AI的API Key:", type="password")
        zhipu_api_base = st.text_input("智谱AI的API Base:")
        st.markdown("[获取智谱AI的API key](https://www.zhipuai.cn/)")
        st.markdown("国产的智谱的翻译质量比较差，甚至如果用了glm-4，还会识别错prompt，建议用glm-3-turbo，或者用OPENAI的API")

st.divider()

upload_file = st.file_uploader("上传PDF文件", type="pdf")
if upload_file:
    st.write(f"你上传的PDF文件是: {upload_file.name}")
    st.divider()
    st.info("文件预览：")
    pdf_preview = pdf_viewer(input=f"{upload_file.name}", height=400, key='1')

    before_pdf, after_pdf = st.columns([1, 1])

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(upload_file.read())
        temp_file_path = temp_file.name
        original_file_name = os.path.splitext(upload_file.name)[0]

# 如果用户没有输入任何API key，提示输入
if not (openai_api_key or zhipu_api_key):
    st.info("请输入OpenAI API Key或者智谱AI的API key")

if (openai_api_key or zhipu_api_key) and not upload_file:
    st.info("请先上传PDF文件")

if openai_api_key and zhipu_api_key and upload_file:
    st.info("有两个api，请选择一个使用即可")

# 如果用户点击了翻译按钮且上传了文件并且提供了API Key
if upload_file and (openai_api_key and not zhipu_api_key) or (zhipu_api_key and not openai_api_key):

    if openai_api_key or zhipu_api_key:
        column1, column2, column3 = st.columns([1, 1, 1])

        with column1:
            target_language = st.selectbox("选择翻译的目标语言",
                                           ["中文", "日文", "韩文", "英文"])
        with column2:
            if openai_api_key and not zhipu_api_key:
                model_name = st.selectbox("选择翻译模型", ["gpt-3.5-turbo", "gpt-4"])
            if zhipu_api_key and not openai_api_key:
                model_name = st.selectbox("选择翻译模型", ["glm-3-turbo", "glm-4"])

        with column3:
            temp_pdf_for_page = pdfplumber.open(temp_file_path)
            page_number_request = st.number_input("选择要翻译的页面数：", value=1, min_value=1,
                                                  max_value=len(temp_pdf_for_page.pages),
                                                  step=1)

        translate_button = st.button("开始翻译")
        target_language = target_language_check(target_language)

        if translate_button:
            del pdf_preview
            with st.spinner("AI正在思考中，请稍等..."):
                if openai_api_key:
                    translator = PDFTranslator(model_name, openai_api_key, openai_api_base)
                elif zhipu_api_key:
                    translator = PDFTranslator(model_name, zhipu_api_key, zhipu_api_base)

                translated_file_path = f"{original_file_name}_translated.pdf"
                translator.translate_pdf(temp_file_path, target_language, translated_file_path, page_number_request)

                with open(translated_file_path, "rb") as f:
                    translated_file_contents = f.read()

                st.success("翻译完成！")

                st.download_button(label="下载翻译后的PDF", data=translated_file_contents,
                                   file_name=translated_file_path)

                st.info("翻译后：")
                pdf_viewer(input=f"{translated_file_path}", height=500, key='2')
