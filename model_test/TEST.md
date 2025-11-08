OCR 성능비교

qwen3_vl_30b_4bit / qwen3_vl_32b_4bit / qwen3_vl_32b_thinking

하나의 견적서 이미지를 위 3개의 모델에서 각각 텍스트 추출하여 결과를 비교하고 싶어.
모델을 미리 3개를 로딩해놓고
input에 이미지 경로를 넣으면 먼저 이미지가 있는지 확인하고
그것을 모델에 순차적으로 전달해서 결과를 받아 추출한 결과를 각각 파일에 기록하게 해줘.
파일 경로는 실행한 파이썬 프로그램 옆에 저장할 수 있도록 기본값으로 하고 변수에 기록해서 언제든지 바꿀 수 있게해줘.

qwen3_vl_30b_4bit -> 파일명_30b.json
qwen3_vl_32b_4bit -> 파일명_32b.json
qwen3_vl_32b_thinking -> 파일명_thinking.json

견적서에서 다음과 같은 정보를 추출해 json배열로 결과를 생성할 수 있도록 프롬프트도 넣어.

List[ResponseItem]
class ResponseItem(BaseModel):
    partNumber: str          # 품번
    itemCategory: str        # 품목
    productName: str         # 품명
    specifications: str      # 규격
    quantity: str            # 수량
    unitPrice: str           # 단가
    totalAmount: str         # 최종금액
    manufacturer: str        # 제조사
    size: str                # 사이즈

