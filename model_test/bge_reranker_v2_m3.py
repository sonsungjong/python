# 리랭킹 모델

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 모델 로드
tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-reranker-v2-m3')
model = AutoModelForSequenceClassification.from_pretrained('BAAI/bge-reranker-v2-m3')
model.eval()

# 쿼리와 문서 쌍
pairs = [
    ["RAG 시스템이란?", "RAG는 검색 증강 생성 기술입니다."],
    ["RAG 시스템이란?", "오늘 날씨가 좋습니다."]
]

# 리랭킹 점수 계산
with torch.no_grad():
    inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)
    scores = model(**inputs, return_dict=True).logits.view(-1, ).float()
    print(scores)  # 높을수록 관련성이 높음