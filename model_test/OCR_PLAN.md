견적서 분석을 위한 NODEJS 중앙서버와 FASTAPI 모델 3개.

외부와 통신하기 위한 NODEJS서버를 연다. 내부에서 돌아가는 FASTAPI서버를 3개 연다.
FASTAPI 서버는 각각 qwen3_vl_30b_4bit과 qwen3_vl_32b_4bit 와 qwen3_vl_32b_thinking 을 로딩해놓는다.
NODEJS에서 파일명과 BASE64로 이미지 정보를 받는다.
nodejs는 이미지 정보를 qwen3_vl_30b_4bit 과 qwen3_vl_32b_4bit 에 넘긴다.
받은 모델들은 이미지에 있는 텍스트를 OCR로 추출하게 한다.
둘의 결과를 받아 비교한다.
만약 비교한 두 결과가 다르다면 추출한 정보를 포함해서 qwen3_vl_thinking 에 전달해서 추출하게한다. 만약 같다면 thinking 쪽에는 보내지 않는다.
추출 응답을 받은 nodejs는 요청한 곳에 응답으로 최종 추출 결과를 전송한다.
