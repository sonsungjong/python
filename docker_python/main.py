# pip install -r requirements.txt

from typing import Union
# pip install fastapi
# pip install uvicorn
from fastapi import FastAPI

# uvicorn main:app --port 8000 --host 0.0.0.0
# uvicorn main:app --reload --port 8000 --host 127.0.0.1
app = FastAPI()

# localhost:8000
@app.get("/")
def read_root():
    return {"Hello": "World"}

# localhost:8000/items/1
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}