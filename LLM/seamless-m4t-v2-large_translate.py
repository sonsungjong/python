from transformers import AutoProcessor, SeamlessM4Tv2Model

# pip install git+https://github.com/huggingface/transformers.git sentencepiece
# python3.11.6, torch2.4.0, torchaudio2.4.0, cuda124

# 프로세서와 모델 불러오기 (쿠다)
processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large").to("cuda")

text = "Hello, my dog is cute"
# 텍스트 입력 전처리 (원본 언어: "eng")
text_inputs = processor(text=text, src_lang="eng", return_tensors="pt")

# 입력 데이터를 GPU로 이동
text_inputs = {key: val.to("cuda") for key, val in text_inputs.items()}

# 텍스트-텍스트 번역: 한국어("kor")로 번역하며, generate_speech=False 옵션을 사용하여 텍스트 출력
output_tokens = model.generate(**text_inputs, tgt_lang="kor", generate_speech=False)

# 번역된 텍스트 디코딩 (스페셜 토큰 제거)
translated_text = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)

print(translated_text)
