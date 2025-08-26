# qwen_ocr_stream_guarded_save.py
# 실행: python qwen_ocr_stream_guarded_save.py
# 요구: Ollama(11434) 실행 중, pip install requests

import os, re, json, base64, requests
from collections import Counter
from pathlib import Path

# ---- 고정 설정 ----
MODEL = "qwen2.5vl:7b"             # Modelfile 쓰면 "qwen-ocr"
IMAGE_PATH = r"C:\test\test.png"    # 고정 경로
URL = "http://127.0.0.1:11434/api/generate"

# 출력 한계 가드
MAX_CHARS  = 12000
MAX_LINES  = 300
MAX_SECONDS = 180

# 반복 토큰 가드
REPEAT_WINDOW_CHARS = 800
REPEAT_TOKEN_MINLEN = 2
REPEAT_TOKEN_LIMIT  = 25

PROMPT = (
    "이 이미지는 영수증/증빙 문서입니다.\n"
    "출력 규칙:\n"
    "- 줄 단위 텍스트만 추출\n"
    "- 동일 문구 1회 이상 반복 금지\n"
    "- 표/워터마크/로고/배경문구는 무시\n"
    "- 반드시 JSON 한 번만 출력\n"
    "- 출력 끝에 <eot> 추가\n"
    '응답 형식(반드시 준수): JSON {"lines":["...","..."]} <eot>'
)

def b64(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"이미지 파일이 없습니다: {path}")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

# 반복 토큰 감지로 강제종료 (핵심!!!!)
def too_repetitive_tail(text: str) -> bool:
    # print('반복 토큰 감지')
    tail = text[-REPEAT_WINDOW_CHARS:]
    tokens = re.findall(rf"[가-힣A-Za-z0-9\-_]{{{REPEAT_TOKEN_MINLEN},}}", tail)
    if not tokens:
        return False
    cnt = Counter(tokens).most_common(1)[0][1]
    return cnt > REPEAT_TOKEN_LIMIT

def strip_code_fences(s: str) -> str:
    # ```json ... ``` 또는 ``` ... ``` 제거
    if s.strip().startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", s.strip())
        s = re.sub(r"\s*```$", "", s.strip())
    return s

def stream_ocr() -> str:
    payload = {
        "model": MODEL,
        "prompt": PROMPT,
        "images": [b64(IMAGE_PATH)],
        "stream": True,
    }
    buf = ""
    lines_seen = 0

    with requests.post(URL, json=payload, stream=True, timeout=(5, MAX_SECONDS)) as r:
        r.raise_for_status()
        print("---- 스트리밍 시작 ----")
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue

            if "response" in obj:
                chunk = obj["response"]
                print(chunk, end="", flush=True)
                buf += chunk

                if "<eot>" in buf.lower():
                    print("\n---- <eot> 감지, 스트림 종료 ----")
                    break

                lines_seen += chunk.count("\n")
                if len(buf) >= MAX_CHARS or lines_seen >= MAX_LINES:
                    print("\n---- 강제 중단(출력 한계 초과) ----")
                    break

                if too_repetitive_tail(buf):
                    print("\n---- 강제 중단(반복 패턴 과다 감지) ----")
                    break

            if obj.get("done"):
                print("\n---- 스트림 정상 종료 ----")
                break
    return buf

def try_parse_json_block(text: str):
    # 코드펜스 제거 후 시도
    t = strip_code_fences(text)

    # {"lines":[...]} 우선
    m = re.search(r'\{[^{}]*"lines"\s*:\s*\[[\s\S]*?\][^{}]*\}', t)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass

    # 아무 JSON 객체라도 마지막부터
    objs = re.findall(r'\{[\s\S]*?\}', t)
    for obj in reversed(objs):
        try:
            return json.loads(obj)
        except Exception:
            continue

    return None

def fallback_lines(text: str):
    # 코드펜스 제거
    t = strip_code_fences(text)
    raw = re.split(r"\r?\n", t)
    out, seen = [], set()
    for ln in raw:
        ln = ln.strip().replace("\u200b", "")
        if not ln:
            continue
        if "<eot>" in ln.lower():
            ln = ln.split("<eot>")[0].strip()
        if len(re.sub(r"\W+", "", ln)) <= 1:
            continue
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    return out

def save_json(result: dict) -> Path:
    # JSON 파일을 스크립트 파일 옆에 생성
    script_path = Path(__file__).resolve()
    out_path = script_path.with_suffix(".ocr.json")

    if out_path.exists():
        # 기존 파일 읽어서 lines 확장
        with open(out_path, "r", encoding="utf-8") as f:
            try:
                old_data = json.load(f)
            except json.JSONDecodeError:
                old_data = {"lines": []}
    else:
        old_data = {"lines": []}

    # 기존 lines + 신규 lines 합치기 (중복 방지는 여기서 선택 가능)
    all_lines = old_data.get("lines", [])
    all_lines.extend(result.get("lines", []))

    new_data = {"lines": all_lines}

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    return out_path

def main():
    try:
        streamed = stream_ocr()
    except requests.exceptions.ReadTimeout:
        print("\n---- 강제 중단(읽기 타임아웃) ----")
        streamed = ""
    except Exception as e:
        print(f"\n[오류] {e}")
        return

    data = try_parse_json_block(streamed)
    if not (isinstance(data, dict) and "lines" in data and isinstance(data["lines"], list)):
        data = {"lines": fallback_lines(streamed)}

    # 최종 중복 제거
    uniq, seen = [], set()
    for s in data.get("lines", []):
        s = str(s).strip()
        if not s or s.lower() == "<eot>":
            continue
        if s not in seen:
            seen.add(s)
            uniq.append(s)

    result = {"lines": uniq}

    # 저장
    out_file = save_json(result)
    print("\n==== 최종 JSON ====")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n✅ 저장 완료: {out_file}")

if __name__ == "__main__":
    main()
