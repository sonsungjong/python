# unsloth
# mmproj-BF16.gguf
# gemma-4-31B-it-Q8_0.gguf
# gemma-4-31B-it-Q4_K_M.gguf
# gemma-4-31B-it-Q5_K_M.gguf

# llama.cpp 설치
# git clone https://github.com/ggerganov/llama.cpp ~/llama.cpp
# cd ~/llama.cpp
# git pull
# cmake -B build -DGGML_CUDA=ON
# cmake --build build --config Release -j$(nproc)

# llama-server 띄우기
# ./build/bin/llama-server -m gemma-4-31B-it-Q4_K_M.gguf --mmproj mmproj-BF16.gguf
# OpenAI API 로 호출

"""
from huggingface_hub import hf_hub_download

# Q4_K_M 양자화 모델
hf_hub_download(
    repo_id="unsloth/gemma-4-31B-it-GGUF",
    filename="gemma-4-31B-it-Q4_K_M.gguf",
)

# mmproj (multimodal projector)
hf_hub_download(
    repo_id="unsloth/gemma-4-31B-it-GGUF",
    filename="mmproj-BF16.gguf",
)

# Q8_0 양자화 모델
hf_hub_download(
    repo_id="unsloth/gemma-4-31B-it-GGUF",
    filename="gemma-4-31B-it-Q8_0.gguf",
)

# Q5_K_M 양자화 모델
hf_hub_download(
    repo_id="unsloth/gemma-4-31B-it-GGUF",
    filename="gemma-4-31B-it-Q5_K_M.gguf",
)
"""

from transformers import AutoProcessor, AutoModelForCausalLM, TextStreamer

MODEL_ID = "google/gemma-4-31B-it"
MAX_HISTORY = 1  # 기억할 대화 턴 수

# 모델 로드 (최초 1회)
print("모델 로딩 중...")
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype="auto",
    device_map="auto"
)
print("로딩 완료! 대화를 시작합니다. (종료: 'quit' 또는 'exit')\n")

history = []  # {"role": "user"/"assistant", "content": "..."}

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ("quit", "exit", "q"):
        print("종료합니다.")
        break
    if not user_input:
        continue

    # 대화 기록 추가
    history.append({"role": "user", "content": user_input})

    # 최근 MAX_HISTORY 턴만 유지 (system 메시지 + 최근 N턴)
    recent = history[-(MAX_HISTORY * 2):]
    messages = [{"role": "system", "content": "You are a helpful assistant. Respond in Korean."}] + recent

    # 입력 처리
    text = processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
        # enable_thinking=True,
    )
    inputs = processor(text=text, return_tensors="pt").to(model.device)
    input_len = inputs["input_ids"].shape[-1]

    # 응답 생성 (스트리밍)
    streamer = TextStreamer(
        processor, 
        skip_prompt=True, 
        skip_special_tokens=True
    )
    print("\n모델응답: ", end="", flush=True)
    outputs = model.generate(**inputs, max_new_tokens=4092, streamer=streamer)
    response = processor.decode(
        outputs[0][input_len:], 
        skip_special_tokens=True
    )
    print()

    # 어시스턴트 응답도 기록에 추가
    history.append({"role": "assistant", "content": response})

