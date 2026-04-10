# llama.cpp 설치
# git clone https://github.com/ggerganov/llama.cpp ~/llama.cpp
# cd ~/llama.cpp
# git pull
# cmake -B build -DGGML_CUDA=ON
# cmake --build build --config Release -j$(nproc)

# llama-server 띄우기
# ~/llama.cpp/build/bin/llama-server -m gemma-4-31B-it-Q4_K_M.gguf --mmproj mmproj-BF16.gguf
# OpenAI API 로 호출
# pip install -U transformers librosa accelerate

# llama.cpp 업데이트 전까지 exaone 전용
# git clone https://github.com/nuxlear/llama.cpp.git ~/llama.cpp-exaone
# cd ~/llama.cpp-exaone
# git fetch origin
# git checkout add-exaone4_5
# git pull origin add-exaone4_5
# cmake -B build -DGGML_CUDA=ON
# cmake --build build --config Release -j$(nproc)

import os
from llama_cpp import Llama
from transformers import AutoProcessor, AutoModelForCausalLM, TextStreamer
from openai import OpenAI
from PIL import Image

"""
from huggingface_hub import hf_hub_download

# Q4_K_M 양자화 모델
hf_hub_download(
    repo_id="LGAI-EXAONE/EXAONE-4.5-33B-GGUF",
    filename="EXAONE-4.5-33B-Q4_K_M.gguf",
)

# mmproj (multimodal projector)
hf_hub_download(
    repo_id="LGAI-EXAONE/EXAONE-4.5-33B-GGUF",
    filename="mmproj-EXAONE-4.5-33B-BF16.gguf",
)
"""

"""
~/llama.cpp-exaone/build/bin/llama-server \
    -m ~/.cache/huggingface/hub/models--LGAI-EXAONE--EXAONE-4.5-33B-GGUF/snapshots/*/EXAONE-4.5-33B-Q4_K_M.gguf \
    -mm ~/.cache/huggingface/hub/models--LGAI-EXAONE--EXAONE-4.5-33B-GGUF/snapshots/*/mmproj-EXAONE-4.5-33B-BF16.gguf \
    -ngl 999 -cb \
    -c 262144 -n 32768 \
    -fa on -sm row \
    --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0 \
    --presence-penalty 1.5 \
    --no-context-shift \
    --port 54545 \
    -a EXAONE-4.5-33B \
    --jinja
"""


client = OpenAI(
    base_url="http://localhost:54545/v1",
    api_key="EMPTY",
)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url":{
                    "url": "https://github.com/Aim-Highest/EXAONE-4.5/blob/main/assets/exaone45_input2.png?raw=true",
                },
            },
            {
                "type": "text",
                "text": "2025년 겨울에 출시된 모델은 2024년 여름에 출시된 모델보다 얼마나 더 큰가요?"
            },
        ]
    }
]

response = client.chat.completions.create(
    model="EXAONE-4.5-33B",
    messages=messages,
    max_tokens=32768,
    temperature=0.6,
    top_p=0.95,
    presence_penalty=1.5,
    # top_k=20,
    extra_body={
        "top_k": 20,
        "chat_template_kwargs": {
            "enable_thinking": True,  # default: True
        }
    }, 
)

print(response.choices[0].message.content)
