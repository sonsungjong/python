### Question Answering using LLM
from langchain_ollama import ChatOllama

from langchain_core.prompts import (SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate)

from langchain_core.output_parsers import StrOutputParser

# 상황에 맞는 LLM 환경 설정
base_url = "http://localhost:11434"
model = 'llama3.2:1b'

llm = ChatOllama(base_url=base_url, model=model)

# 상황에 맞는 시스템 프롬프트로 작성
system_prompt = SystemMessagePromptTemplate.from_template("""You are helpful AI assistant who answer user question based on the provided context.""")

# 상황에 맞는 휴먼프롬프트 작성
question_format = """Answer user question based on the provided context ONLY! If you do not know the answer, just say "I do not know".
### Context:
{context}

### Question:
{question}

### Answer:"""

human_prompt = HumanMessagePromptTemplate.from_template(question_format)

messages = [system_prompt, human_prompt]
template = ChatPromptTemplate(messages)

# 체인 생성
qna_chain = template | llm | StrOutputParser()

# 함수 제작 (상황에 맞는 invoke 매개변수로 작성)
def ask_llm(context, question):
    return qna_chain.invoke({'context':context, 'question':question})

