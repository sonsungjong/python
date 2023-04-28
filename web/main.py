from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# uvicorn main:app --reload 명령어로 main.py실행
app = FastAPI()

# 정적 파일 경로 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    # index.html 파일 읽어오기
    with open("static/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html, status_code=200)

@app.get("/api/data")
async def get_data():
    # 데이터 처리 및 변환
    return {"FastAPI": "예제코드"}
