"""
================================================================================
GGUF 모델 생성 가이드 (직접 양자화 버전)
================================================================================

Hugging Face 모델을 다운로드 후 직접 GGUF로 변환하고 양자화하여 사용합니다.
llama-server를 사용하면 모델을 한 번만 로딩하므로 매우 빠릅니다.

================================================================================
1. 설치 및 환경 구성
================================================================================

1-1. llama.cpp 설치 및 빌드
----------------------------
cd /home/user/source
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
mkdir -p build && cd build
cmake .. -DGGML_CUDA=ON -DLLAMA_CURL=OFF
cmake --build . --config Release -j$(nproc)

빌드 완료 후 다음 실행 파일들이 생성됩니다:
- bin/llama-cli       : 명령줄 추론 도구
- bin/llama-server    : HTTP API 서버
- bin/llama-quantize  : 모델 양자화 도구

1-2. Python 패키지 설치
------------------------
pip install requests pillow

================================================================================
2. 모델 변환 및 양자화 (한 번만 실행)
================================================================================

2-1. Hugging Face 모델 → F16 GGUF 변환
---------------------------------------
cd /home/user/source/llama.cpp
python convert_hf_to_gguf.py \
  ~/.cache/huggingface/hub/models--Qwen--Qwen3-VL-30B-A3B-Instruct/snapshots/[해시]/ \
  --outfile /home/user/models/qwen3-vl-30b-f16.gguf \
  --outtype f16

2-2. F16 → Q4_K_M 양자화 (70% 압축)
------------------------------------
./build/bin/llama-quantize \
  /home/user/models/qwen3-vl-30b-f16.gguf \
  /home/user/models/qwen3-vl-30b-Q4_K_M.gguf \
  Q4_K_M

양자화 옵션:
- Q4_K_M : 4bit, 균형 (권장, 70% 압축)
- Q5_K_M : 5bit, 고품질
- Q8_0   : 8bit, 최고품질
- Q2_K   : 2bit, 최대압축

다른 모델 예시:
- Qwen3-VL-32B-Thinking
- GPT-OSS-20B
- Exaone-4-32B
모두 동일한 방법으로 변환 가능

================================================================================
3. 여러 모델을 다른 포트로 동시 실행하기
================================================================================

3-1. 모델 1: Qwen3-VL-30B (포트 8080)
--------------------------------------
/home/user/source/llama.cpp/build/bin/llama-server \
  -m /home/user/models/qwen3-vl-30b-Q4_K_M.gguf \
  -ngl -1 \
  --host 0.0.0.0 \
  --port 8080 \
  -c 4096 \
  > /tmp/llama-server-8080.log 2>&1 &

3-2. 모델 2: Qwen3-VL-32B-Thinking (포트 8081)
-----------------------------------------------
/home/user/source/llama.cpp/build/bin/llama-server \
  -m /home/user/models/qwen3-vl-32b-Q4_K_M.gguf \
  -ngl -1 \
  --host 0.0.0.0 \
  --port 8081 \
  -c 4096 \
  > /tmp/llama-server-8081.log 2>&1 &

3-3. 모델 3: GPT-OSS-20B (포트 8082)
-------------------------------------
/home/user/source/llama.cpp/build/bin/llama-server \
  -m /home/user/models/gpt-oss-20b-Q4_K_M.gguf \
  -ngl -1 \
  --host 0.0.0.0 \
  --port 8082 \
  -c 4096 \
  > /tmp/llama-server-8082.log 2>&1 &

3-4. 서버 상태 확인
-------------------
curl http://localhost:8080/health  # 모델 1
curl http://localhost:8081/health  # 모델 2
curl http://localhost:8082/health  # 모델 3

# 실행 중인 모든 서버 확인
ps aux | grep llama-server

# 로그 확인
tail -f /tmp/llama-server-8080.log

3-5. 서버 종료
--------------
# 특정 포트 서버만 종료
pkill -f "llama-server.*8080"

# 모든 llama-server 종료
pkill llama-server

================================================================================
4. Python에서 사용하기
================================================================================

4-1. 기본 텍스트 생성
---------------------
import requests

response = requests.post("http://localhost:8080/v1/chat/completions", json={
    "messages": [{"role": "user", "content": "안녕하세요"}],
    "temperature": 0.7,
    "max_tokens": 512
})
print(response.json()["choices"][0]["message"]["content"])

4-2. 이미지 + 텍스트 (Vision 모델)
-----------------------------------
import base64

with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

response = requests.post("http://localhost:8080/v1/chat/completions", json={
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "이미지의 텍스트를 추출해줘"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
        ]
    }],
    "max_tokens": 512
})

4-3. 여러 모델 동시 사용
------------------------
# 각 모델에 맞는 포트로 요청
model1 = requests.post("http://localhost:8080/v1/chat/completions", ...)  # Qwen3-VL-30B-A3B-Instruct
model2 = requests.post("http://localhost:8081/v1/chat/completions", ...)  # Qwen3-VL-32B-Instruct
model3 = requests.post("http://localhost:8082/v1/chat/completions", ...)  # Qwen3-VL-32B-Thinking

================================================================================
5. 성능 최적화 팁
================================================================================

5-1. GPU 메모리 부족 시
------------------------
- 일부 레이어만 GPU로: -ngl 40 (전체 레이어의 일부만)
- 더 작은 양자화: Q2_K 사용

5-2. 속도 향상
--------------
- 배치 크기 증가: -b 2048
- 컨텍스트 축소: -c 2048 (기본 4096)
- Flash Attention 활성화: --flash-attn

5-3. 메모리 절약
----------------
- mmap 사용 (기본 활성화됨)
- 낮은 양자화: Q4_K_M 대신 Q2_K

================================================================================
6. 문제 해결
================================================================================

Q: "unknown model architecture" 에러
A: llama.cpp를 최신 버전으로 업데이트하세요.
   git pull && cmake --build build --config Release

================================================================================
"""
import subprocess
from pathlib import Path
import requests
import json
import sys

LLAMA_CLI = "/home/user/source/llama.cpp/build/bin/llama-cli"
LLAMA_SERVER = "/home/user/source/llama.cpp/build/bin/llama-server"
MODEL_PATH = "/home/user/models/qwen3-vl-30b-Q4_K_M.gguf"
SERVER_URL = "http://localhost:8080"


def check_server_running() -> bool:
    """llama-server가 실행 중인지 확인"""
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_server():
    """llama-server를 백그라운드로 시작"""
    print("\n서버를 시작하는 중... (15초 정도 소요)")
    print(f"명령어: {LLAMA_SERVER} -m {MODEL_PATH} -ngl -1 --port 8080 -c 4096")
    
    cmd = [
        LLAMA_SERVER,
        "-m", MODEL_PATH,
        "-ngl", "-1",
        "--host", "0.0.0.0",
        "--port", "8080",
        "-c", "4096"
    ]
    
    # 백그라운드로 실행
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # 서버가 준비될 때까지 대기
    import time
    for i in range(30):
        time.sleep(1)
        if check_server_running():
            print("✅ 서버 시작 완료!\n")
            return True
        print(f"대기 중... {i+1}/30")
    
    print("❌ 서버 시작 실패")
    return False


def extract_text_from_image_api(image_path: str, prompt: str = "이미지에 있는 모든 텍스트를 추출해줘.") -> str:
    """
    llama-server HTTP API를 사용하여 이미지에서 텍스트 추출
    """
    # 이미지를 base64로 인코딩
    import base64
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    # API 요청
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]
            }
        ],
        "temperature": 0.7,
        "max_tokens": 512
    }
    
    response = requests.post(f"{SERVER_URL}/v1/chat/completions", json=payload, timeout=60)
    
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"❌ 에러: {response.status_code} - {response.text}"


def extract_text_from_image_cli(image_path: str, prompt: str = "이미지에 있는 모든 텍스트를 추출해줘.") -> str:
    """
    llama-cli를 사용하여 이미지에서 텍스트 추출 (서버 없이)
    """
    cmd = [
        LLAMA_CLI,
        "-m", MODEL_PATH,
        "-p", prompt,
        "--image", image_path,
        "-ngl", "-1",
        "-n", "512",
        "--no-cnv",
        "-c", "4096",
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


def main():
    print("=" * 80)
    print("Qwen3-VL-30B GGUF OCR (직접 양자화 버전)")
    print("=" * 80)
    print(f"모델: {MODEL_PATH}")
    
    # 서버 실행 확인
    use_server = False
    if check_server_running():
        print("✅ llama-server가 이미 실행 중입니다.")
        use_server = True
    else:
        print("⚠️  llama-server가 실행되지 않았습니다.")
        choice = input("서버를 시작하시겠습니까? (y/n, 권장: y): ").strip().lower()
        
        if choice == 'y':
            if start_server():
                use_server = True
            else:
                print("서버 시작 실패. llama-cli 모드로 실행합니다 (느림).")
        else:
            print("llama-cli 모드로 실행합니다 (매번 15초 로딩).")
    
    print("=" * 80 + "\n")
    
    while True:
        # 이미지 경로 입력
        image_path_str = input("이미지 경로를 입력하세요 (종료: q): ").strip()
        
        # 종료 조건
        if image_path_str.lower() in ['q', 'quit', 'exit']:
            print("프로그램을 종료합니다.")
            break
        
        if not image_path_str:
            print("경로를 입력해주세요.\n")
            continue
        
        image_path = Path(image_path_str)
        
        # 경로 검증
        if not image_path.exists():
            print(f"❌ 이미지를 찾을 수 없습니다: {image_path}\n")
            continue
        
        print(f"\n처리 중: {image_path}")
        print("-" * 80)
        
        # 텍스트 추출
        if use_server:
            print("🚀 서버 API로 추론 중...")
            output = extract_text_from_image_api(str(image_path))
        else:
            print("⏳ llama-cli로 추론 중... (15초 소요)")
            output = extract_text_from_image_cli(str(image_path))
        
        print("\n" + "=" * 80)
        print("추출된 텍스트")
        print("=" * 80)
        print(output)
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()