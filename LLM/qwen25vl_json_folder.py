import os, re, json, base64, requests
from collections import Counter
from pathlib import Path
import unicodedata, difflib

# ---- 고정 설정 ----
MODEL = "qwen2.5vl:7b"             # Modelfile 쓰면 "qwen-ocr"
FOLDER_PATH = r"C:\line"    # 이미지 폴더 경로
URL = "http://127.0.0.1:11434/api/generate"
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tif", ".tiff")

# 출력 한계 가드
MAX_CHARS  = 48000
MAX_LINES  = 1000
MAX_SECONDS = 180

# 반복 토큰 가드
REPEAT_WINDOW_CHARS = 800
REPEAT_TOKEN_MINLEN = 2             # 글자수
REPEAT_TOKEN_LIMIT  = 25

PROMPT = (
    "이 이미지는 영수증/증빙 문서입니다.\n"
    "출력 규칙:\n"
    "- 줄 단위 텍스트만 추출\n"
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


def _norm_token(s: str) -> str:
    # 유사도 검사용 정규화: 한글 자모/폭 통합, 공백/콤마 제거, 소문자
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", "", s)
    s = s.replace(",", "")
    return s.lower()

def detect_semantic_loop(buf: str,
                         window_chars: int = 8000,
                         window_tokens: int = 150,
                         hit_count: int = 40,
                         sim_ratio: float = 0.92):
    """
    버퍼 꼬리에서 주소/라벨처럼 거의 같은 문구가 반복되는지 감지.
    - 최근 window_chars에서 따옴표 안 토큰 추출
    - 정규화 후 최빈 토큰이 hit_count 이상이면 트리거
    - 또는 최근 토큰과의 유사도(sim_ratio 이상) 토큰이 window에서 hit_count 이상이면 트리거
    """
    tail = buf[-window_chars:]
    tokens = re.findall(r'"([^"]+)"', tail)
    if not tokens:
        return False, None

    last = tokens[-window_tokens:] if len(tokens) > window_tokens else tokens
    normed = [_norm_token(t) for t in last]

    from collections import Counter
    tok, cnt = Counter(normed).most_common(1)[0]
    if cnt >= hit_count:
        # 원문 예시도 함께 보여주기
        sample = last[normed.index(tok)]
        return True, f'반복 토큰 {cnt}회("{sample}")'

    recent = normed[-1]
    sim = sum(1 for t in normed if difflib.SequenceMatcher(None, recent, t).ratio() >= sim_ratio)
    if sim >= hit_count:
        sample = last[-1]
        return True, f'유사 토큰 {sim}회("{sample}")'

    return False, None


def stream_ocr(img_file) -> str:
    payload = {
        "model": MODEL,
        "prompt": PROMPT,
        "images": [b64(img_file)],
        "stream": True,
        "options": {
            "temperature": 0,
            "num_ctx": 8192,
            "stop": ["<eot>"]
        }
    }
    buf = ""
    lines_seen = 0

    # 동일 청크 반복 감지
    repeat_count = 0
    last_chunk = ""

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
                    print("\n---- 강제 중단(eot) ----")
                    break

                hit, reason = detect_semantic_loop(buf)
                if hit:
                    end_reason = f"\n---- 강제 중단 (유사 문구 반복 감지: {reason}) ----"
                    print(end_reason)
                    break

                # === 여기부터 무한루프 방지 추가 ===
                tail = buf[-4000:]  # 최근 4000자만 검사

                # 1) JSON 배열 내 "0" 항목 반복 감지: 200개 이상이면 종료
                zero_items = re.findall(r'"\s*0\s*"\s*,', tail)
                if len(zero_items) >= 200:
                    print("\n---- 강제 중단(JSON \"0\" 200개 이상 반복) ----")
                    break

                # 2) 따옴표 안 토큰 중 최근 80개를 봐서 80% 이상이 '0'일 때
                tokens = re.findall(r'"([^"]+)"', tail)
                if tokens:
                    last_n = tokens[-80:] if len(tokens) > 80 else tokens
                    zeros = sum(1 for t in last_n if t.strip() == "0")
                    if zeros >= max(50, int(len(last_n) * 0.8)):
                        print("\n---- 강제 중단(최근 토큰의 80% 이상이 '0') ----")
                        break

                # 3) 꼬리 800자 이상이 0/쉼표/공백/대괄호/백슬래시만으로 구성되면 종료
                if len(tail) >= 800 and re.fullmatch(r'[\s0,"\[\],\\]+', tail):
                    print("\n---- 강제 중단(꼬리 800자 이상이 0/구두점만) ----")
                    break
                # === 무한루프 방지 추가 끝 ===

                # 동일 chunk가 연속 200회 나오면 중단
                norm = chunk.strip()
                if norm and norm == last_chunk:
                    repeat_count += 1
                else:
                    repeat_count = 0
                last_chunk = norm
                if repeat_count >= 200:
                    print("\n---- 강제 중단(같은 토큰 200회 연속) ----")
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
    i = buf.lower().rfind("<eot>")
    if i != -1:
        buf = buf[:i]
    return buf


def try_parse_json_block(text: str):
    # 코드펜스 제거
    t = strip_code_fences(text).strip()

    # 1) 직접 JSON 객체 시도
    try:
        obj = json.loads(t)
        # {"lines":[...]} 그대로면 반환
        if isinstance(obj, dict) and "lines" in obj:
            return obj
        # ["a","b"] 리스트만 있으면 감싸기
        if isinstance(obj, list) and all(isinstance(x, str) for x in obj):
            return {"lines": obj}
        # 문자열 JSON이면 다시 파싱
        if isinstance(obj, str):
            try:
                inner = json.loads(obj)
                if isinstance(inner, dict) and "lines" in inner:
                    return inner
                if isinstance(inner, list) and all(isinstance(x, str) for x in inner):
                    return {"lines": inner}
            except Exception:
                pass
    except Exception:
        pass

    # 2) 텍스트 안에서 {...} 블록 찾아 역순으로 시도
    objs = re.findall(r'\{[\s\S]*?\}', t)
    for obj_text in reversed(objs):
        try:
            cand = json.loads(obj_text)
            if isinstance(cand, dict) and "lines" in cand:
                return cand
        except Exception:
            continue

    # 3) 실패하면 None 반환 (main에서 fallback_lines로 처리)
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

def save_json(result: dict, img_file: str) -> Path:
    # 스크립트(.py) 옆에 <이미지이름>.ocr.json 로 저장/append
    script_dir = Path(__file__).resolve().parent
    base = Path(img_file).stem
    out_path = script_dir / f"output/{base}.ocr.json"            # 각자 파일로 저장
    # out_path = script_dir / f"qwen.ocr.json"              # 하나의 파일에 저장

    # 폴더 없으면 생성
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists():
        with open(out_path, "r", encoding="utf-8") as f:
            try:
                old_data = json.load(f)
            except json.JSONDecodeError:
                old_data = {"lines": []}
    else:
        old_data = {"lines": []}

    all_lines = old_data.get("lines", [])
    all_lines.extend(result.get("lines", []))
    new_data = {"lines": all_lines}

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    return out_path

def main():
    folder = Path(FOLDER_PATH)
    if not folder.is_dir():
        print(f"폴더가 없습니다: {FOLDER_PATH}")
        return

    # 폴더 내 이미지 목록
    imgs = [str(p) for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS]
    if not imgs:
        print(f"이미지가 없습니다: {FOLDER_PATH}")
        return

    print(f"총 {len(imgs)}개 이미지 처리 예정.")
    for img in imgs:
        try:
            streamed = stream_ocr(img)
        except requests.exceptions.ReadTimeout:
            print(f"\n---- 강제 중단(읽기 타임아웃): {img} ----")
            continue
        except Exception as e:
            print(f"\n[오류] {img} -> {e}")
            continue

        data = try_parse_json_block(streamed)
        if not (isinstance(data, dict) and "lines" in data and isinstance(data["lines"], list)):
            data = {"lines": fallback_lines(streamed)}

        # 최종 중복 제거
        uniq, seen = [], set()
        for s in data.get("lines", []):
            s = str(s).strip()

            # --- (1) 항목이 '{"lines":[...]}' 같은 JSON 문자열이면 언랩해서 펼침
            if s.startswith("{") and s.endswith("}"):
                try:
                    inner = json.loads(s)
                    if isinstance(inner, dict) and isinstance(inner.get("lines"), list):
                        for t in inner["lines"]:
                            t = str(t)
                            # --- (2) 개행/컨트롤 제거 + 공백 정리
                            t = re.sub(r"[\r\n\u2028\u2029\u000b\u000c]+", " ", t)
                            t = re.sub(r"\s{2,}", " ", t).strip()
                            if not t or t.lower() == "<eot>":
                                continue
                            if t not in seen:
                                seen.add(t)
                                uniq.append(t)
                        continue
                except Exception:
                    pass

            # --- 일반 항목: (2) 개행/컨트롤 제거 + 공백 정리
            s = re.sub(r"[\r\n\u2028\u2029\u000b\u000c]+", " ", s)
            s = re.sub(r"\s{2,}", " ", s).strip()
            if not s or s.lower() == "<eot>":
                continue
            if s not in seen:
                seen.add(s)
                uniq.append(s)

        result = {"lines": uniq}
        _blob = "".join(result["lines"])

        # "lines"가 2번 이상 나오거나 내부 "{\"lines\":[" 패턴이 보이면만 실행
        if _blob.count("lines") >= 2 or '{\\"lines\\":[' in _blob or '{"lines":[' in _blob:
            t = _blob.replace('\\"', '"')  # \" -> "

            # 1) 앞부분: 처음 나오는 {"lines":[ 까지 싹 잘라냄 (문자열 모드 그대로)
            t = re.sub(r'.*?\{"lines"\s*:\s*\[', '', t, flags=re.S)

            # 2) 뒷부분: ]} 이후는 버림
            t = re.sub(r'\]\}.*$', '', t, flags=re.S)

            # 3) 이제 t는 "값","값","값"... 형태. 따옴표 안의 값들만 뽑음.
            parts = re.findall(r'"([^"]+)"', t)

            # 4) 정리(개행/공백/중복/<eot> 제거) 후 배열 재구성
            seen, cleaned = set(), []
            for x in parts:
                x = re.sub(r'[\r\n\u2028\u2029\u000b\u000c]+', ' ', x)
                x = re.sub(r'\s{2,}', ' ', x).strip()
                if not x or x.lower() == '<eot>':
                    continue
                if x not in seen:
                    seen.add(x)
                    cleaned.append(x)

            result = {"lines": cleaned}
        

        # 이미지별 JSON 저장(append)
        out_file = save_json(result, img)
        print("\n==== 최종 JSON ====")
        print(json.dumps(result, ensure_ascii=False))
        print(f"\n✅ 저장 완료: {out_file}")

if __name__ == "__main__":
    main()