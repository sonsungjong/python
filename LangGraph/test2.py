import json, re, torch
from PIL import Image
from transformers import DonutProcessor, VisionEncoderDecoderModel

ckpt = "naver-clova-ix/donut-base-finetuned-cord-v2"
proc  = DonutProcessor.from_pretrained(ckpt)
model = VisionEncoderDecoderModel.from_pretrained(ckpt).cuda().eval()

img = Image.open("tester1.png").convert("RGB")
pix = proc(img, return_tensors="pt").pixel_values.cuda()

task_prompt = "<s_cord-v2>"                     # config 따라 다름
dec_prompt  = proc.tokenizer(task_prompt,
                              add_special_tokens=False,
                              return_tensors="pt").input_ids.cuda()

out = model.generate(pix,
                     decoder_input_ids=dec_prompt,
                     max_length=512,
                     bad_words_ids=[[proc.tokenizer.unk_token_id]])
seq = proc.batch_decode(out)[0]
print("RAW:", seq)              # ← 추가
seq = re.sub(r"<.*?>", "", seq, count=1).strip()   # 시작 토큰 제거
print(json.dumps(proc.token2json(seq), indent=2, ensure_ascii=False))
