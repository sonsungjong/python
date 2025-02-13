### Question Answering using LLM
from langchain_ollama import ChatOllama

from langchain_core.prompts import (SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate)

from langchain_core.output_parsers import StrOutputParser

base_url = "http://localhost:11434"
model = 'llama3.2:1b'

llm = ChatOllama(base_url=base_url, model=model)

system_prompt = SystemMessagePromptTemplate.from_template("""You are helpful AI assistant who answer user question based on the provided context.""")

question_format = """Answer user question based on the provided context ONLY! If you do not know the answer, just say "I don't know".
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

# 함수 제작
def ask_llm(context, question):
    return qna_chain.invoke({'context':context, 'question':question})

