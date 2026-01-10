import os, re, json, base64, requests
from collections import Counter
from pathlib import Path
import unicodedata, difflib
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

# ---- ResponseItem 정의 ----
class ResponseItem(BaseModel):
    partNumber: str = Field(description="품번")
    itemCategory: str = Field(description="품목")
    productName: str = Field(description="품명")
    specifications: str = Field(description="규격")
    quantity: str = Field(description="수량")
    unitPrice: str = Field(description="단가")
    totalAmount: str = Field(description="최종금액")
    manufacturer: str = Field(description="제조사")
    size: str = Field(description="사이즈")

# ---- 고정 설정 ----
MODEL = "qwen2.5vl:7b"             # Modelfile 쓰면 "qwen-ocr"
FOLDER_PATH = r"./OCR_TEST/sample1"    # 이미지 폴더 경로
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

# JsonOutputParser 설정 (배열을 위해 pydantic_object 없이 사용)
parser = JsonOutputParser()

PROMPT = (
    "이 이미지는 견적서/거래명세서 표 문서입니다.\n\n"
    "**작업: 표의 데이터 행들을 JSON 배열로 변환 (표를 한 번만 읽고 종료)**\n\n"
    "**절차:**\n"
    "1. 표 헤더(품명, 규격, 수량, 단가, 금액) 찾기\n"
    "2. 첫 데이터 행부터 마지막 데이터 행까지 순서대로 읽기\n"
    "3. 각 행을 JSON 객체로 변환\n"
    "4. **중요: 빈 행이나 '합계' 행을 만나면 즉시 멈추고 ] <eot> 출력**\n"
    "5. **절대 같은 행을 반복하지 말 것**\n\n"
    "**컬럼 매핑:**\n"
    "품명→productName | 규격→specifications | 수량→quantity | 단가→unitPrice | 금액→totalAmount\n\n"
    "**JSON 구조 (9개 필드 필수):**\n"
    "```json\n"
    "[\n"
    "  {\n"
    '    "partNumber": "",\n'
    '    "itemCategory": "",\n'
    '    "productName": "...",\n'
    '    "specifications": "...",\n'
    '    "quantity": "...",\n'
    '    "unitPrice": "...",\n'
    '    "totalAmount": "...",\n'
    '    "manufacturer": "",\n'
    '    "size": ""\n'
    "  }\n"
    "]\n"
    "```\n\n"
    "**규칙:**\n"
    "• 표 셀 원본 그대로 (해석/수정 금지)\n"
    "• 숫자 쉼표 제거: 1,000,000 → 1000000\n"
    "• 줄바꿈 → 공백\n"
    "• 빈 셀 → \"\"\n"
    "• 외국어(영어, 이탈리아어 등)도 정확히 읽기\n"
    "• **표 끝나면 즉시 ] <eot> 출력하고 절대 추가 생성 금지**\n"
    "• **같은 항목 반복 절대 금지**\n\n"
    "출력:\n"
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

def detect_json_object_loop(buf: str, repeat_limit: int = 3):
    """
    JSON 배열에서 동일한 객체가 연속으로 반복되는지 감지
    최근 4000자를 검사하여 완성된 {...} 객체 추출 후 마지막 N개 비교
    """
    tail = buf[-4000:]
    
    # 완성된 JSON 객체들 추출
    objects = []
    depth = 0
    start_idx = -1
    
    for i, char in enumerate(tail):
        if char == '{':
            if depth == 0:
                start_idx = i
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0 and start_idx >= 0:
                obj_text = tail[start_idx:i+1]
                try:
                    obj = json.loads(obj_text)
                    if isinstance(obj, dict):
                        objects.append(obj)
                except Exception:
                    pass
                start_idx = -1
    
    if len(objects) < repeat_limit:
        return False, None
    
    # 마지막 N개 객체가 모두 동일한지 확인
    last_n = objects[-repeat_limit:]
    first = json.dumps(last_n[0], sort_keys=True, ensure_ascii=False)
    
    all_same = all(json.dumps(obj, sort_keys=True, ensure_ascii=False) == first for obj in last_n)
    
    if all_same:
        sample_name = last_n[0].get('productName', '알 수 없음')
        return True, f'동일 객체 {repeat_limit}회 반복("{sample_name}")'
    
    return False, None

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
    
    # JSON 필드명(짧은 문자열)은 무시 - 실제 데이터 반복만 감지
    if len(tok) <= 2 or tok in ['partnumber', 'itemcategory', 'productname', 
                                  'specifications', 'quantity', 'unitprice', 
                                  'totalamount', 'manufacturer', 'size', '']:
        return False, None
    
    if cnt >= hit_count:
        # 원문 예시도 함께 보여주기
        sample = last[normed.index(tok)]
        return True, f'반복 토큰 {cnt}회("{sample}")'

    recent = normed[-1]
    # 빈 문자열이나 짧은 문자열은 유사도 검사 제외
    if len(recent) <= 2:
        return False, None
        
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
            "num_predict": 16000,  # 최대 생성 토큰 수 제한 (무한루프 방지)
            "stop": ["<eot>", "] <eot>", "]\n<eot>", "합계", "총계"],  # 다양한 종료 패턴
            "repeat_penalty": 1.1  # 반복 억제
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

                # 동일 JSON 객체 반복 감지 (무한루프 방지) - 5회 이상 반복시에만
                obj_loop, obj_reason = detect_json_object_loop(buf, repeat_limit=5)
                if obj_loop:
                    print(f"\n---- 강제 중단 ({obj_reason}) ----")
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


def normalize_item(item: dict) -> dict:
    """모든 필드를 포함하도록 객체 정규화 (없는 필드는 빈 문자열)"""
    required_fields = [
        'partNumber', 'itemCategory', 'productName', 'specifications',
        'quantity', 'unitPrice', 'totalAmount', 'manufacturer', 'size'
    ]
    
    normalized = {}
    for field in required_fields:
        value = item.get(field, "")
        # None이나 null 값도 빈 문자열로 변환
        if value is None or value == "null":
            value = ""
        # 문자열이 아니면 문자열로 변환
        if not isinstance(value, str):
            value = str(value) if value else ""
        normalized[field] = value.strip()
    
    return normalized

def extract_complete_json_objects(text: str) -> list:
    """불완전한 JSON에서 완성된 객체들만 추출하고 정규화"""
    items = []
    depth = 0
    start_idx = -1
    
    for i, char in enumerate(text):
        if char == '{':
            if depth == 0:
                start_idx = i
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0 and start_idx >= 0:
                # 완성된 객체 발견
                obj_text = text[start_idx:i+1]
                try:
                    obj = json.loads(obj_text)
                    if isinstance(obj, dict):
                        # 정규화하여 모든 필드 포함
                        normalized = normalize_item(obj)
                        items.append(normalized)
                except Exception:
                    pass
                start_idx = -1
    
    return items

def try_parse_json_block(text: str):
    # 코드펜스 제거
    t = strip_code_fences(text).strip()

    # 1) 직접 JSON 파싱 시도 (배열 또는 객체)
    try:
        obj = json.loads(t)
        # 배열이면 정규화해서 반환
        if isinstance(obj, list):
            return [normalize_item(item) if isinstance(item, dict) else item for item in obj]
        # 객체면 정규화해서 배열로 반환
        if isinstance(obj, dict):
            return [normalize_item(obj)]
    except Exception:
        pass

    # 2) 불완전한 JSON 배열 복구 시도 - 완성된 객체들만 추출
    if '[' in t:
        items = extract_complete_json_objects(t)
        if items:
            return items

    # 3) 텍스트 안에서 [...] 배열 블록 찾기
    arrays = re.findall(r'\[[\s\S]*?\]', t)
    for arr_text in reversed(arrays):
        try:
            cand = json.loads(arr_text)
            if isinstance(cand, list):
                # 정규화해서 반환
                return [normalize_item(item) if isinstance(item, dict) else item for item in cand]
        except Exception:
            continue

    # 4) 마지막 시도: 완성된 객체들 추출
    items = extract_complete_json_objects(t)
    if items:
        return items

    # 5) 실패하면 None 반환
    return None

def fallback_lines(text: str):
    """파싱 실패 시 빈 배열 반환"""
    # JSON 배열 형식이 아니면 빈 배열 반환
    return []

def save_json(result: list, img_file: str) -> Path:
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
                old_data = []
    else:
        old_data = []

    # 배열 확인 및 추가
    if not isinstance(old_data, list):
        old_data = []
    if not isinstance(result, list):
        result = []
    
    all_items = old_data + result

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

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

        # JSON 파싱 시도
        data = try_parse_json_block(streamed)
        
        # 파싱 실패 시 LangChain parser 사용 시도
        if data is None:
            try:
                data = parser.parse(streamed)
            except Exception as e:
                print(f"\n[파싱 오류] {e}")
                data = fallback_lines(streamed)
        
        # 데이터가 리스트가 아니면 빈 배열로 설정
        if not isinstance(data, list):
            data = []
        
        # 결과 정리 및 중복 제거
        result = []
        seen = set()
        
        for item in data:
            if isinstance(item, dict):
                # 정규화 (모든 필드 포함, 빈 문자열 처리)
                normalized = normalize_item(item)
                
                # 개행/공백 추가 정리
                for key in normalized:
                    value = normalized[key]
                    if value:
                        # 개행/컨트롤 문자를 공백으로 변환
                        value = re.sub(r"[\r\n\u2028\u2029\u000b\u000c]+", " ", value)
                        # 연속 공백을 하나로
                        value = re.sub(r"\s{2,}", " ", value).strip()
                        normalized[key] = value
                
                # 합계/기타 행 필터링
                product_name = normalized.get("productName", "").strip().lower()
                if product_name in ["합계", "총계", "소계", "total", "subtotal", "sum"]:
                    continue
                
                # 중복 체크
                item_str = json.dumps(normalized, sort_keys=True, ensure_ascii=False)
                if item_str not in seen:
                    seen.add(item_str)
                    result.append(normalized)

        # 이미지별 JSON 저장(append)
        out_file = save_json(result, img)
        print("\n==== 최종 JSON ====")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"\n✅ 저장 완료: {out_file}")

if __name__ == "__main__":
    main()