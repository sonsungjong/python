import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import time

if not torch.cuda.is_available():
    raise EnvironmentError("GPU가 필요합니다. 현재 시스템에서 GPU를 사용할 수 없습니다.")

model_id = 'Bllossom/llama-3.2-Korean-Bllossom-3B'

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
).to('cuda')  # 모델을 GPU로 이동
tokenizer.pad_token = tokenizer.eos_token

# 모델 최대 토큰 길이 확인
print('입력 최대 길이: ',tokenizer.model_max_length)

system_prompt = "Your name is '지니'. Please respond to my words in formal Korean."
conversation_history = [
    {"role": "system", "content": f"{system_prompt}"}
]

while True:
    user_prompt = input('입력하세요 (종료하려면 "exit" 입력)>> ')
    # 소요 시간 측정 시작
    start_time = time.time()

    if user_prompt.lower() == "exit":
        break

    # 입력 내용 추가
    conversation_history.append({"role": "user", "content":f"{user_prompt}"})

    recent_history = conversation_history[-50:]             # 최근 50개의 대화까지만 반영

    # 대화를 모델 입력 형식에 맞게 변환 (GPU로 이동)
    input_ids = tokenizer.apply_chat_template(
        recent_history,
        add_generation_prompt=True,
        return_tensors="pt",
        padding=True,           # 패딩 추가
        truncation=True,             # 입력 길이가 너무 길면 잘라냄
    ).to('cuda')

    # 종료 토큰 정의
    terminators = [
        tokenizer.convert_tokens_to_ids("<|end_of_text|>"),
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    # 모델을 사용해 응답 생성
    outputs = model.generate(
        input_ids,
        max_new_tokens = 1024,
        eos_token_id=terminators,
        pad_token_id=tokenizer.pad_token_id,          # 패딩 토큰
        do_sample=True,
        temperature=0.7,                # 창의성
        top_p=0.9
    )

    # 모델의 응답을 디코딩해서 출력
    model_response = tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)
    print(model_response)

    # 시간 측정 끝
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'소요 시간: {elapsed_time:.2f}초')

    # 모델의 응답을 대화 기록에 추가
    conversation_history.append({"role":"assistant", "content":model_response})

# pip install transformers torch accelerate>=0.26.0