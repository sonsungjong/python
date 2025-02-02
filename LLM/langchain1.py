from langchain_ollama import ChatOllama

base_url = "http://localhost:11434"
model = 'llama3.2:1b'
# model = 'llama3.2-vision:11b'
# model = 'llava:7b'

llm = ChatOllama(base_url=base_url, model=model)

question = {"prompt":"tell me about earth"}
response = llm.invoke(question)
print(response.content)