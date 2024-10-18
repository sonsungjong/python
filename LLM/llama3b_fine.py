import torch
from transformers import AutoTokenizer, AutoModelForCausalLM                            # 라마3.2
from transformers import Trainer, TrainingArguments
import os
import time
from deep_translator import GoogleTranslator
import tkinter as tk
from tkinter import messagebox
from datasets import Dataset
import pandas as pd


torch.cuda.empty_cache()  # 불필요한 메모리를 해제

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if not torch.cuda.is_available():
    root = tk.Tk()
    root.withdraw()  # 메시지 박스 외에 tkinter 창이 나타나지 않도록 설정
    messagebox.showwarning("경고", "GPU가 필요합니다. 현재 시스템에서 GPU를 사용할 수 없습니다 => CPU로 대체합니다.")
else:
    root = tk.Tk()
    root.withdraw()  # 메시지 박스 외에 tkinter 창이 나타나지 않도록 설정
    messagebox.showwarning("안내", "GPU를 사용합니다.")

os.environ["HUGGINGFACE_HUB_TOKEN"] = "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"
model_id = "meta-llama/Llama-3.2-3B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    token=os.environ["HUGGINGFACE_HUB_TOKEN"]
).to(device)  # 모델을 GPU로 이동
tokenizer.pad_token = tokenizer.eos_token

# 모델 최대 토큰 길이 확인
print('입력 최대 길이: ',tokenizer.model_max_length)

# =================== 파인튜닝 ======================
# 1. Pandas 데이터 준비
data = {
    "prompt": ["주인:", "주인아내:"],
    "completion": ["동동이", "깜찍이"]
}
df = pd.DataFrame(data)

dataset = Dataset.from_pandas(df)
def format_dataset(example):
    prompt = example["prompt"]
    completion = example["completion"]
    input_text = f"{prompt} {completion}"
    return {
        "input_ids": tokenizer(input_text, truncation=True, padding='max_length', max_length=tokenizer.model_max_length, return_tensors="pt")["input_ids"].squeeze()
    }

dataset = dataset.map(format_dataset)

# 4. 파인튜닝 인자 설정
training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=1,
    num_train_epochs=3,
    logging_dir="./logs",
    logging_steps=10,
    save_steps=100,
    save_total_limit=2,
    learning_rate=5e-5,
)

# 5. Trainer 정의
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset
)

# 6. 파인튜닝 수행
trainer.train()
# ===== 파인튜닝 완료 =====


system_prompt = """
Your name is '지니'.
"""
conversation_history = [
    {"role": "system", "content": f"{system_prompt}"}
]

while True:
    user_prompt = input('한국어로 입력하세요 (종료하려면 "exit" 입력)>> ')
    # 소요 시간 측정 시작
    if user_prompt.lower() == "exit":
        break

    start_time = time.time()
    user_prompt_translate = GoogleTranslator(source='ko', target='en')
    user_prompt_ko = user_prompt_translate.translate(user_prompt)
    print('영어->한국어 번역결과:',user_prompt_ko)

    # 영어로 번역된 내용 추가
    conversation_history.append({"role": "user", "content":f"{user_prompt_ko}"})

    recent_history = conversation_history[-50:]             # 최근 50개의 대화까지만 반영

    # 대화를 모델 입력 형식에 맞게 변환 (GPU로 이동)
    input_ids = tokenizer.apply_chat_template(
        recent_history,
        add_generation_prompt=True,
        return_tensors="pt",
        padding=True,           # 패딩 추가
        truncation=True,             # 입력 길이가 너무 길면 잘라냄
    ).to(device)

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

    # 모델 응답을 저장
    model_response = tokenizer.decode(outputs[0][input_ids.shape[-1]:], skip_special_tokens=True)
    print('\n==================라마3.2:\n',model_response,'\n===============\n')

    # 모델 응답을 한국어로 번역
    # translator = GoogleTranslator(target='ko')
    
    translator = GoogleTranslator(source='en', target='ko')
    ko_result = translator.translate(model_response)
    print('\n==============번역:\n',ko_result,'\n==============\n')
    
    # 시간 측정 끝
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'소요 시간: {elapsed_time:.2f}초')

    # 모델의 응답을 대화 기록에 추가
    conversation_history.append({"role":"assistant", "content":model_response})

# pip install deep_translator
# https://lonaru-burnout.tistory.com/16    (CUDA와 cuDNN 설치)
# pip install transformers torch accelerate>=0.26.0
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124