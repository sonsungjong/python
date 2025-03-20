# streamlit run app.py
import streamlit as st
import pymupdf

from scripts.llm import ask_llm, validate_json

st.title("Resume Parsing")
st.write("Upload a resume in PDF format to extract information")

uploaded_file = st.file_uploader("Choose a file")
context = ""

if uploaded_file is not None:
    bytearray = uploaded_file.read()
    pdf = pymupdf.open(stream=bytearray, filetype="pdf")

    context = ""
    for page in pdf:
        context = context + "\n\n" + page.get_text()

    pdf.close()

    # st.write(context)

# 질문 프롬프트를 작성한다
question = """
You are tasked with parsing a job resume. 
Your goal is to extract relevant information in a valid structured 'JSON' format.
Do not write preambles or explanations.
"""

if st.button("Pagese PDF"):
    with st.spinner("Parsing Resume..."):
        response = ask_llm(context=context, question=question)

    with st.spinner("Vaildating JSON..."):
        response = validate_json(response)

    st.write("**Extracted Information")
    st.write(response)

    st.write("You can copy the JSON output and use it in your application.")

    st.balloons()