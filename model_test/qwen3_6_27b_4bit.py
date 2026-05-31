# ----------------------------------------------------------------------
"""
llama.cpp 설치 및 빌드 가이드 (Linux + CUDA)
1. llama.cpp 소스 다운로드
git clone https://github.com/ggerganov/llama.cpp.git ~/llama.cpp
cd ~/llama.cpp

2. 빌드 (CUDA 지원 활성화)
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release -j$(nproc)
"""

# 압축 및 해제
# tar -czvf llama.cpp.tar.gz llama.cpp/
# tar -xzvf llama.cpp.tar.gz

# llama.cpp 서버를 통한 Qwen3.6-27B-Q4_K_M.gguf + mmproj-BF16.gguf 추론
# 서버 실행:
'''
~/llama.cpp/build/bin/llama-server \
  -m ~/.cache/huggingface/hub/models--unsloth--Qwen3.6-27B-GGUF/snapshots/*/Qwen3.6-27B-Q4_K_M.gguf \
  --mmproj ~/.cache/huggingface/hub/models--unsloth--Qwen3.6-27B-GGUF/snapshots/*/mmproj-BF16.gguf \
  -ngl 999 --port 11435 -c 32768 --reasoning off
'''
# 서버 종료:
# Ctrl+C 또는
# pkill -f llama-server
# 또는 PID로 종료: kill $(pgrep -f llama-server)

import os
import base64
import subprocess
import requests
from huggingface_hub import hf_hub_download

llama_server_path = os.path.expanduser("~/llama.cpp/build/bin/llama-server")

SERVER_PORT = os.getenv("QWEN36_PORT", "11435")
SERVER_URL = f"http://127.0.0.1:{SERVER_PORT}"
SERVER_LOG = os.getenv("QWEN36_SERVER_LOG", "/tmp/qwen3_6_27b_llama_server.log")

REPO_ID = os.getenv("QWEN36_REPO_ID", "unsloth/Qwen3.6-27B-GGUF")
MODEL_FILENAME = os.getenv("QWEN36_MODEL_FILENAME", "Qwen3.6-27B-Q4_K_M.gguf")
MMPROJ_FILENAME = os.getenv("QWEN36_MMPROJ_FILENAME", "mmproj-BF16.gguf")
CONTEXT_SIZE = os.getenv("QWEN36_CONTEXT", "32768")
N_GPU_LAYERS = os.getenv("QWEN36_NGL", "999")
REASONING_MODE = os.getenv("QWEN36_REASONING", "off")

SERVER_PROCESS = None

# 이미지 확장자에 따른 MIME 타입 반환
def get_image_mime_type(image_path):
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp'
    }
    return mime_types.get(ext, 'image/png')

# imagefile to base64
def local_image_to_base64(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at: {image_path}")
    with open(image_path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
    return encoded_string


def get_model_paths():
    """huggingface_hub을 통해 모델 경로 가져오기 (없으면 다운로드)"""
    print(f"Hugging Face 모델 확인/다운로드: {REPO_ID}")
    model_path = hf_hub_download(repo_id=REPO_ID, filename=MODEL_FILENAME)
    mmproj_path = hf_hub_download(repo_id=REPO_ID, filename=MMPROJ_FILENAME)
    print(f"모델 파일: {os.path.basename(model_path)}")
    print(f"mmproj 파일: {os.path.basename(mmproj_path)}")
    return model_path, mmproj_path


def check_server():
    """서버 상태 확인 및 자동 시작"""
    global SERVER_PROCESS
    import time
    
    # 1차 연결 시도
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("llama-server 연결 성공 (이미 실행 중)")
            return True
    except:
        pass
    
    # 2차 연결 시도
    time.sleep(1)
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("llama-server 연결 성공 (이미 실행 중)")
            return True
    except:
        pass
    
    # 서버 시작
    print("llama-server 시작 중...")
    model_path, mmproj_path = get_model_paths()
    
    
    if not os.path.exists(llama_server_path):
        print(f"llama-server를 찾을 수 없습니다: {llama_server_path}")
        return False
    
    cmd = [
        llama_server_path,
        "-m", model_path,
        "--mmproj", mmproj_path,
        "-ngl", N_GPU_LAYERS,
        "--host", "127.0.0.1",
        "--port", SERVER_PORT,
        "-c", CONTEXT_SIZE,      # 컨텍스트 길이 제한 (메모리 절약: 262k -> 32k)
        "--reasoning", REASONING_MODE,
        # "-fa"               # Flash Attention 강제 활성화
    ]
    
    print("실행 명령:", " ".join(cmd))
    print(f"llama-server 로그: {SERVER_LOG}")
    log_file = open(SERVER_LOG, "a", encoding="utf-8")
    log_file.write("\n\n--- qwen3.6 llama-server start ---\n")
    log_file.write(" ".join(cmd) + "\n")
    log_file.flush()
    SERVER_PROCESS = subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT)
    
    # 서버 시작 대기
    print("서버 로딩 대기 중...")
    for i in range(180):
        try:
            response = requests.get(f"{SERVER_URL}/health", timeout=2)
            if response.status_code == 200:
                print("llama-server 시작 완료")
                return True
        except:
            pass
        time.sleep(1)
        if (i + 1) % 30 == 0:
            print(f"  {i+1}초 대기 중...")
    
    print("서버 시작 실패")
    return False


def stop_server():
    """llama-server 종료"""
    global SERVER_PROCESS
    if SERVER_PROCESS is None:
        return

    print("\nllama-server 종료 중...")
    try:
        SERVER_PROCESS.terminate()
        SERVER_PROCESS.wait(timeout=30)
        print("✓ llama-server 종료 완료")
    except subprocess.TimeoutExpired:
        SERVER_PROCESS.kill()
        print("llama-server 강제 종료 완료")
    except Exception as e:
        print(f"서버 종료 실패: {e}")
    finally:
        SERVER_PROCESS = None


def analyze_image(image_path, prompt="Read all the text in the image line by line."):
    """이미지 분석 요청"""
    if not os.path.exists(image_path):
        print(f"파일을 찾을 수 없습니다: {image_path}")
        return None
    
    base64_image = local_image_to_base64(image_path)
    mime_type = get_image_mime_type(image_path)
    
    print(f'추론 시작: {os.path.basename(image_path)}')
    
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
# "content": [
#   {"type": "text", "text": "각 이미지의 텍스트를 순서대로 읽어줘."},
#   {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
#   {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
#   {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
#             ]
            }
        ],
        "temperature": 0.1,      # OCR: 낮은 온도로 정확성 향상
        "top_p": 0.9,
        "top_k": 40,
        "max_tokens": 8192,
        "repeat_penalty": 1.1     # 반복 방지
    }
    
    try:
        response = requests.post(
            f"{SERVER_URL}/v1/chat/completions",
            json=payload,
            timeout=900
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"에러: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"요청 실패: {e}")
        return None


def main():
    if not check_server():
        return
    print("이미지 파일 경로를 입력하세요.")
    print("종료하려면 'exit', 'quit', 또는 '/bye' 입력")
    
    try:
        while True:
            try:
                user_input = input("[이미지 경로] >>> ").strip()
                
                if user_input.lower() in ['exit', 'quit', '/bye', 'q']:
                    print("종료합니다.")
                    break
                
                if not user_input:
                    continue
                
                # 상대 경로를 절대 경로로 변환
                if not os.path.isabs(user_input):
                    user_input = os.path.abspath(user_input)
                
                result = analyze_image(user_input)
                
                if result:
                    print("\n" + "-" * 50)
                    print("[결과]")
                    print("-" * 50)
                    print(result)
                    print("-" * 50 + "\n")
                    
            except KeyboardInterrupt:
                print("\n\n종료합니다.")
                break
            except Exception as e:
                print(f"오류 발생: {e}")
    finally:
        # 어떤 상황에서도 서버 종료
        stop_server()


if __name__ == "__main__":
    main()
