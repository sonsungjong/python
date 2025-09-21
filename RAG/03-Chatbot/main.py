# streamlit run main.py
import streamlit as st
from langchain_core.messages.chat import ChatMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from langchain import hub
# from langchain_teddynote import load_prompt
import yaml

load_dotenv()

st.title("나의 챗봇")

# 처음 1번만 실행
if "messages" not in st.session_state:
    # 대화 기록
    st.session_state["messages"] = []

# 사이드바 생성
with st.sidebar:
    clear_btn = st.button("대화 초기화")        # 대화기록 초기화
    selected_prompt = st.selectbox("프롬프트를 선택해 주세요", ("기본모드", "SNS 게시글", "요약"), index=0)

# 기록된 대화 출력
def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)

# 새로운 대화 추가
def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))

def create_chain(prompt_type):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "당신은 친절한 AI 어시스턴트 입니다."),
            ("user", "#Question:\n{question}")
        ]
    )
    if prompt_type == "SNS 게시글":
        # 프롬프트 파일에서 불러오기
        with open("prompts/sns.yaml", "r", encoding="utf-8") as f:
            sns_prompt_data = yaml.safe_load(f)
        prompt = ChatPromptTemplate.from_template(sns_prompt_data["template"])
    elif prompt_type == "요약":
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "당신은 친절한 AI 요약 어시스턴트입니다. 사용자가 입력한 문장을을 간결하게 요약해 주세요."),
                ("user", "#요약할 내용:\n{question}")
            ]
        )
    
    # llm = ChatOllama(model="llama3.2:1b", temperature=0)
    llm = ChatOllama(model="gpt-oss:20b", temperature=0)
    chain = prompt | llm | StrOutputParser()
    return chain

print_messages()

# 사용자의 입력
user_input = st.chat_input("궁금한 내용을 물어보세요^^")

# 사용자가 입력하면
if user_input:
    # 사용자 입력
    st.chat_message("user").write(user_input)
    add_message("user", user_input)
    # 체인 생성
    chain = create_chain(selected_prompt)
    # 답변
    # ai_answer = chain.invoke({"question": user_input})
    ai_answer = ""
    response = chain.stream({"question":user_input})
    with st.chat_message("assistant"):
        # 빈공간을 만들어서 토큰을 스트리밍으로 출력한다
        container = st.empty()
        for token in response:
            ai_answer += token
            container.markdown(ai_answer)

    # AI 답변
    add_message("assistant", ai_answer)
    