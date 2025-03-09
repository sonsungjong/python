# streamlit run chat_stream.py
import streamlit as st

from langchain_ollama import ChatOllama
from langchain_core.prompts import( SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder )
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.output_parsers import StrOutputParser

base_url = "http://localhost:11434"
model = "llama3.2:1b"
# user_id = "Sungjong Son"

st.title("Make Your Own Chatbot")
st.write("Chat with me!")

# 유저 아이디를 입력창으로 받게
user_id = st.text_input("아이디를 입력하세요", "Sungjong Son")

def get_session_history(session_id):
    return SQLChatMessageHistory(session_id, "sqlite:///chat_history.db")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if st.button("Start New Conversation"):
    # 버튼 클릭시 동작
    st.session_state.chat_history = []
    history = get_session_history(user_id)
    history.clear()         # 버튼을 눌러 초기화를 시켜도 동일한 아이디에 대해 계속해서 데이터를 저장해놓고 싶으면 clear를 하지 않으면 된다

# session_state에 쌓인 리스트를 하나씩 사용자아이콘으로 꾸민다
for message in st.session_state.chat_history:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# LLM Setup
llm = ChatOllama(base_url=base_url, model=model)

system = SystemMessagePromptTemplate.from_template("You are helpful assistant.")
human = HumanMessagePromptTemplate.from_template("{input}")

messages = [system, MessagesPlaceholder(variable_name='history'), human]

prompt = ChatPromptTemplate(messages=messages)

chain = prompt | llm | StrOutputParser()

runnable_with_history = RunnableWithMessageHistory(chain, get_session_history, input_messages_key='input', history_messages_key='history')

def chat_with_llm(session_id, input):
    for output in runnable_with_history.stream( {'input':input}, config={'configurable':{'session_id':session_id}} ):
        yield output


# 입력창 생성
prompt = st.chat_input("What is up?")

if prompt:
    st.session_state.chat_history.append({'role':'user', 'content':prompt})
    # 즉각적으로 화면에 추가하게 한다
    with st.chat_message("user"):
        st.markdown(prompt)

    # 즉각적으로 화면에 나오게 한다
    with st.chat_message("assistant"):
        response = st.write_stream(chat_with_llm(user_id, prompt))

    st.session_state.chat_history.append({'role':'assistant', 'content':response})

