# pip install fastapi
# pip install "uvicorn[standard]"
'''
fastapi : 소규모 파이썬 웹서버
"uvicorn[standard]" : 웹서버 미리보기

uvicorn 파일명:app --reload 를 터미널에 입력해서 실행

uvicorn fast_api:app --reload
'''


from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pymysql

app = FastAPI()
# 입력을 받으려면 Model과 class를 생성해야한다
class MyModel(BaseModel):
    id : str
    pwd : int

@app.get("/")
def 작명():
    return FileResponse('sample.html')

@app.get("/data")
def data():
    return {'hello':1234}


@app.post("/send")
def 입력(my_data : MyModel):
    print(my_data)
    return my_data

@app.get("/asy")
async def 비동기사용():
    await print('await 오른쪽에 있는 코드를 기다려준다')
    return 'await을 기다리는 동안에 다른 기능을 수행한다 == 비동기'