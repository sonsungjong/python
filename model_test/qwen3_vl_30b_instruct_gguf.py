# llama.cpp 서버를 통한 Qwen3-VL-30B 추론
# 서버 실행:
'''
/home/user/source/llama.cpp/build/bin/llama-server \
  -m ~/.cache/huggingface/hub/models--Qwen--Qwen3-VL-30B-A3B-Instruct-GGUF/*/*/Qwen3VL-30B-A3B-Instruct-Q4_K_M.gguf \
  --mmproj ~/.cache/huggingface/hub/models--Qwen--Qwen3-VL-30B-A3B-Instruct-GGUF/*/*/mmproj-Qwen3VL-30B-A3B-Instruct-F16.gguf \
  -ngl 999 --port 11435
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

SERVER_URL = "http://127.0.0.1:11435"
REPO_ID = "Qwen/Qwen3-VL-30B-A3B-Instruct-GGUF"
MODEL_FILENAME = "Qwen3VL-30B-A3B-Instruct-Q4_K_M.gguf"
MMPROJ_FILENAME = "mmproj-Qwen3VL-30B-A3B-Instruct-F16.gguf"
llama_server_path = "/home/user/source/llama.cpp/build/bin/llama-server"

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
    model_path = hf_hub_download(repo_id=REPO_ID, filename=MODEL_FILENAME)
    mmproj_path = hf_hub_download(repo_id=REPO_ID, filename=MMPROJ_FILENAME)
    return model_path, mmproj_path


def check_server():
    """서버 상태 확인 및 자동 시작"""
    import time
    
    # 1차 연결 시도
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("llama-server 연결 성공")
            return True
    except:
        pass
    
    # 2차 연결 시도
    time.sleep(1)
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print("llama-server 연결 성공")
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
        "-ngl", "999",
        "--port", "11435"
    ]
    
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
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
    print("\nllama-server 종료 중...")
    try:
        subprocess.run(["pkill", "-f", "llama-server"], check=False)
        print("✓ llama-server 종료 완료")
    except Exception as e:
        print(f"서버 종료 실패: {e}")


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

