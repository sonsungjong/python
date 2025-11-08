# pip install uv
# uv pip install langchain langchain-community langchain-text-splitters langchain-core langchain-ollama langchain-openai langchain-huggingface transformers sentence-transformers torch faiss-cpu pymupdf python-dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from typing import List
from dotenv import load_dotenv
import torch
import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# load_dotenv()

# step 1 : load document
docs = PyMuPDFLoader("SPRI_AI_Brief_2023년12월호_F.pdf").load()

# step 2 : split document
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
split_documents = text_splitter.split_documents(docs)

# step 3 : Embedding
hf_embeddings = HuggingFaceEmbeddings(model_name = "BAAI/bge-m3", model_kwargs={"device": "cuda"}, encode_kwargs={"normalize_embeddings": True},)
# hf_embeddings = SentenceTransformer("Qwen/Qwen3-Embedding-8B", model_kwargs={"device": "cuda"}, encode_kwargs={"normalize_embeddings": True},)

# step 4 : vector DB
try:
    vectorstore = FAISS.load_local(
        folder_path="faiss_db",
        index_name="faiss_index",
        embeddings=hf_embeddings,
        allow_dangerous_deserialization=True,
    )
except:
    vectorstore = FAISS.from_documents(documents=split_documents, embedding=hf_embeddings)
    vectorstore.save_local("faiss_db", "faiss_index")
# vectorstore.add_documents(new_split_documents)
# vectorstroe.save_local("faiss_db", "faiss_index")

# step 5 : Retriever Search
retriever = vectorstore.as_retriever()

# step 6 : generate prompt
prompt = PromptTemplate.from_template(
    """You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Answer in Korean.

#Question:
{question}

#Context:
{context}

#Answer:"""
)

# step 7 : LLM
# tokenizer = AutoTokenizer.from_pretrained("LGAI-EXAONE/EXAONE-4.0-1.2B")
tokenizer = AutoTokenizer.from_pretrained("LGAI-EXAONE/EXAONE-4.0-32B")
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True)
model = AutoModelForCausalLM.from_pretrained(
    "LGAI-EXAONE/EXAONE-4.0-32B",
    quantization_config=quantization_config,            # 4bit 양자화 설정
    # dtype="auto",
    device_map="cuda:0"                 # 명시적 GPU 설정
)
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=512,
    temperature=0.01,  # 거의 0에 가까운 값 (일관성 유지)
    do_sample=True,    # 샘플링 활성화
    return_full_text=False,
    # device_map 사용 시 device 파라미터 제거 (accelerate가 자동 처리)
    pad_token_id=tokenizer.eos_token_id,  # 패딩 토큰 명시적 설정
)
llm = HuggingFacePipeline(pipeline=pipe)

# step 8: chain
def format_docs(docs):
    return "\n\n".join(
        f"[page {d.metadata.get('page', 0) + 1}] {d.page_content}" for d in docs
    )
chain = (
    {"context": retriever | RunnableLambda(format_docs), "question":RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)

# CHAIN 사용
# result = chain.invoke("삼성이 만든 생성AI 의 이름은 무엇인가요?")
result = ""
for chunk in chain.stream("삼성이 만든 생성AI 의 이름은 무엇인가요?"):
    result += chunk
    print(chunk, end="", flush=True)

print(f'\n\n[FINAL] {result}')
