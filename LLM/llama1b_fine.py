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
from transformers import DataCollatorForSeq2Seq


torch.cuda.empty_cache()
torch.cuda.memory_summary(device=None, abbreviated=False)

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
model_id = "meta-llama/Llama-3.2-1B-Instruct"

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
# 1. 모델 경로와 파인튜닝 데이터셋 (리스트와 딕셔너리 사용)
fine_output_dir = "./result"
fine_tuned_data = [
    {"prompt": "master", "completion": "Dongdong"},
    {"prompt": "master", "completion": "Dongdong"},
    {"prompt": "master's wife", "completion": "Bingbing"},
    {"prompt": "master's wife", "completion": "Bingbing"},
    {"prompt": "The master said to his wife: Is dinner ready?", "completion": "Dongdong said to Bingbing: Is dinner ready?"},
    {"prompt": "The master's wife replied to the master: Just wait a little.", "completion": "Bingbing replied to Dongdong: Just wait a little."},
    # Additional examples
    {"prompt": "Who is the master?", "completion": "It's Dongdong."},
    {"prompt": "What is the master's name?", "completion": "It's Dongdong."},
    {"prompt": "What is the name of the master's wife?", "completion": "It's Bingbing."},
    {"prompt": "Dongdong said to Bingbing: Is dinner ready?", "completion": "Dongdong said to Bingbing: Is dinner ready?"}
]

# 2. 데이터셋 변환
fine_df = pd.DataFrame(fine_tuned_data)
fine_dataset = Dataset.from_pandas(fine_df)

# 3. 데이터 전처리
def fine_preprocess_function(examples):
    inputs = examples['prompt']
    targets = examples['completion']
    model_inputs = tokenizer(inputs, max_length=128, truncation=True, padding='max_length')  # 패딩을 적용해 길이 맞추기
    labels = tokenizer(targets, max_length=128, truncation=True, padding='max_length')  # 동일한 설정으로 패딩 적용
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

fine_tokenized_dataset = fine_dataset.map(fine_preprocess_function, batched=True)

# 데이터 수집기 설정 (패딩을 자동으로 처리)
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

# 4. 경로지정
if os.path.exists(fine_output_dir) and os.listdir(fine_output_dir):
    print('파인튜닝된 모델이 이미 존재하므로 로드합니다')
    fine_model = AutoModelForCausalLM.from_pretrained(fine_output_dir).to(device)
    tokenizer = AutoTokenizer.from_pretrained(fine_output_dir)
else:
    print('파인튜닝된 모델이 없어 새로운 모델을 생성합니다')
    fine_training_args = TrainingArguments(
        output_dir=fine_output_dir,
        eval_strategy="no",
        learning_rate=2e-5,
        per_device_train_batch_size=4,
        num_train_epochs=3,
        weight_decay=0.01,
        save_total_limit=2,
        push_to_hub=False,
    )

    # 5. 트레이너 설정
    fine_trainer = Trainer(
        model=model,
        args=fine_training_args,
        train_dataset=fine_tokenized_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator
    )

    # 6. 파인튜닝 실행
    fine_trainer.train()

    # 7. 파인튜닝된 모델을 저장
    model.save_pretrained(fine_output_dir)
    tokenizer.save_pretrained(fine_output_dir)
    print("모델 파인튜닝 및 저장이 완료되었습니다.")

    # 파인튜닝 완료 후 모델을 로드
    fine_model = AutoModelForCausalLM.from_pretrained(fine_output_dir).to(device)

print(fine_model)
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

    # 8. 파인튜닝 모델을 사용해 응답 생성
    fine_model = fine_model.to(device)
    input_ids = input_ids.to(device)

    outputs = fine_model.generate(
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