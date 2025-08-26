import os
import re
import json
import base64
import requests
from collections import Counter

# ---- 고정 설정 ----
MODEL = "qwen2.5vl:7b"  # Modelfile로 파라미터 고정했다면 "qwen-ocr"로 변경
IMAGE_PATH = r"C:\test\tester1.png"  # 고정 경로

# 출력 한계 (안 끝나는 반복 방지)
MAX_CHARS  = 12000   # 총 생성 글자수 제한
MAX_LINES  = 300     # 개행 기준 라인 수 제한
MAX_SECONDS = 180    # 서버 읽기 타임아웃(초) (스트림 전체)

# 반복 토큰 감지 (무한 루프 차단용)
REPEAT_WINDOW_CHARS = 800     # 최근 N자에서
REPEAT_TOKEN_MINLEN = 2       # 최소 토큰 길이
REPEAT_TOKEN_LIMIT  = 25      # 동일 토큰이 이 횟수 초과하면 중단

PROMPT = (
    "이 이미지는 영수증/증빙 문서입니다.\n"
    "출력 규칙:\n"
    "- 동일 문구 1회 이상 반복 금지\n"
    "- 표/워터마크/로고/배경문구는 무시\n"
    "- 반드시 JSON 한 번만 출력\n"
    "- 출력 끝에 <eot> 추가\n"
    '응답 형식(반드시 준수): JSON {"lines":["...","..."]} <eot>'
)

URL = "http://127.0.0.1:11434/api/generate"  # Ollama REST

def b64(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"이미지 파일이 없습니다: {path}")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

def too_repetitive_tail(text: str) -> bool:
    """
    최근 REPEAT_WINDOW_CHARS 내에서 동일 토큰이 REPEAT_TOKEN_LIMIT 초과시 True.
    (영문/한글/숫자/대시/언더스코어 토큰만 집계)
    """
    tail = text[-REPEAT_WINDOW_CHARS:]
    tokens = re.findall(r"[가-힣A-Za-z0-9\-_]{%d,}" % REPEAT_TOKEN_MINLEN, tail)
    if not tokens:
        return False
    cnt = Counter(tokens)
    most_common_token, c = cnt.most_common(1)[0]
    return c > REPEAT_TOKEN_LIMIT

def stream_ocr() -> str:
    payload = {
        "model": MODEL,
        "prompt": PROMPT,
        "images": [b64(IMAGE_PATH)],
        "stream": True,
    }
    buf = ""
    lines_seen = 0

    # 연결 5초 / 읽기 MAX_SECONDS
    with requests.post(URL, json=payload, stream=True, timeout=(5, MAX_SECONDS)) as r:
        r.raise_for_status()
        print("---- 스트리밍 시작 ----")
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                # 비정상 라인은 무시
                continue

            if "response" in obj:
                chunk = obj["response"]
                print(chunk, end="", flush=True)  # 실시간 콘솔 출력
                buf += chunk

                # 종료 신호 감지
                if "<eot>" in buf.lower():
                    print("\n---- <eot> 감지, 스트림 종료 ----")
                    break

                # 길이/라인 강제 제한
                lines_seen += chunk.count("\n")
                if len(buf) >= MAX_CHARS or lines_seen >= MAX_LINES:
                    print("\n---- 강제 중단(출력 한계 초과) ----")
                    break

                # 반복 패턴 감지
                if too_repetitive_tail(buf):
                    print("\n---- 강제 중단(반복 패턴 과다 감지) ----")
                    break

            # 일부 서버는 done 신호를 별도로 보냄
            if obj.get("done"):
                print("\n---- 스트림 정상 종료 ----")
                break
    return buf

def try_parse_json_block(text: str):
    # {"lines":[ ... ]} 블록 우선 탐색
    m = re.search(r'\{[^{}]*"lines"\s*:\s*\[[\s\S]*?\][^{}]*\}', text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    # 아무 JSON 객체라도 마지막부터 시도
    objs = re.findall(r'\{[\s\S]*?\}', text)
    for obj in reversed(objs):
        try:
            return json.loads(obj)
        except Exception:
            continue
    return None

def fallback_lines(text: str):
    raw = re.split(r"\r?\n", text)
    out, seen = [], set()
    for ln in raw:
        ln = ln.strip().replace("\u200b", "")
        if not ln:
            continue
        # <eot> 뒤 제거
        if "<eot>" in ln.lower():
            ln = ln.split("<eot>")[0].strip()
        # 의미 거의 없는 잡음 제거
        if len(re.sub(r"\W+", "", ln)) <= 1:
            continue
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    return out

def main():
    try:
        streamed = stream_ocr()
    except requests.exceptions.ReadTimeout:
        print("\n---- 강제 중단(읽기 타임아웃) ----")
        streamed = ""
    except Exception as e:
        print(f"\n[오류] {e}")
        return

    # 후처리: JSON 우선
    data = try_parse_json_block(streamed)
    if not (isinstance(data, dict) and "lines" in data):
        data = {"lines": fallback_lines(streamed)}

    # 안전망: 최종 중복 제거
    uniq, seen = [], set()
    for s in data.get("lines", []):
        s = s.strip()
        if not s or s.lower() == "<eot>":
            continue
        if s not in seen:
            seen.add(s)
            uniq.append(s)

    result = {"lines": uniq}
    print("\n==== 최종 JSON ====")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
