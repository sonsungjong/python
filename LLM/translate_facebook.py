from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
import os
import torch

# GPU가 사용 가능한 경우
if not torch.cuda.is_available():
    print("GPU가 필요합니다. 현재 시스템에서 GPU를 사용할 수 없습니다.")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

article_ko = "안녕하세요, 반갑습니다. 제 이름은 손성종 입니다."
article_en = "hello, everybody. my name is son sung jong."

translate_model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt").to(device)
translate_tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")

# 한국어를 영어로
# translate_tokenizer.src_lang = "ko_KR"
# encoded_hi = translate_tokenizer(article_ko, return_tensors="pt").to(device)
# generated_tokens = translate_model.generate(
#     **encoded_hi,
#     forced_bos_token_id=translate_tokenizer.lang_code_to_id["en_XX"]
# )
# result = translate_tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
# print(result)


# 영어를 한국어로
translate_tokenizer.src_lang = "en_XX"
encoded_hi = translate_tokenizer(article_en, return_tensors="pt").to(device)
generated_tokens = translate_model.generate(
    **encoded_hi,
    forced_bos_token_id=translate_tokenizer.lang_code_to_id["ko_KR"]
)
result = translate_tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
print(result)


# ko_KR
# en_XX
# ja_XX
# zh_CN