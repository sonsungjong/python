# pat-jj/harness-1
# https://huggingface.co/pat-jj/harness-1

# 서버 실행 (터미널 1):
# 사전 요구: 아래 '설정 (최초 1회)' 블록을 한 번 실행.
# source 없이 vllm serve 하면 MoE Triton 컴파일 단계에서 ptxas 오류로 실패함.
'''
source ~/source/python312/python/model_test/harness-1-vllm.env

vllm serve pat-jj/harness-1 \
  --served-model-name harness-1 \
  --host 0.0.0.0 \
  --port 11436 \
  --tensor-parallel-size 1 \
  --max-model-len 16384 \
  --max-num-seqs 2 \
  --trust-remote-code \
  --gpu-memory-utilization 0.85
'''

# 상태 확인:
'''
curl http://127.0.0.1:11436/v1/models
'''

# 클라이언트 실행 (터미널 2):
'''
python harness-1.py
'''

# 서버 종료:
"""
Ctrl+C
pkill -f "vllm serve"
kill $(pgrep -f "vllm serve")
"""

# 모델 다운로드:
'''
hf download pat-jj/harness-1
'''

# 설정 (최초 1회):
'''
mkdir -p ~/.cache/tiktoken-rs-cache
curl -fsSL https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken \
  -o ~/.cache/tiktoken-rs-cache/o200k_base.tiktoken

cat > ~/source/python312/python/model_test/harness-1-vllm.env << 'EOF'
export CUDA_HOME=/usr/local/cuda
export PATH=/usr/local/cuda/bin:$PATH
export CPATH=/usr/local/cuda/include
export LIBRARY_PATH=/usr/local/cuda/lib64:/usr/local/cuda/targets/sbsa-linux/lib
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/local/cuda/targets/sbsa-linux/lib
export TORCH_CUDA_ARCH_LIST=12.1a
export TRITON_PTXAS_PATH=/usr/local/cuda/bin/ptxas
export TIKTOKEN_RS_CACHE_DIR=~/.cache/tiktoken-rs-cache
export TIKTOKEN_ENCODINGS_BASE=~/.cache/tiktoken-rs-cache
EOF

grep -q 'harness-1 vLLM' ~/.bashrc || cat >> ~/.bashrc << 'EOF'

# harness-1 vLLM (DGX Spark GB10)
source ~/source/python312/python/model_test/harness-1-vllm.env
EOF

source ~/.bashrc
'''

import json
import sys
import urllib.error
import urllib.request

SERVER_PORT = 11436
SERVER_HOST = "127.0.0.1"
MODEL_NAME = "harness-1"
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"


def chat_completion(messages, max_tokens=4096, temperature=0.7):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    req = urllib.request.Request(
        f"{SERVER_URL.rstrip('/')}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.load(resp)


def extract_answer(message):
    content = (message.get("content") or "").strip()
    if content:
        return content
    reasoning = (message.get("reasoning_content") or "").strip()
    return reasoning or "(응답 없음)"


def check_server():
    try:
        with urllib.request.urlopen(
            f"{SERVER_URL.rstrip('/')}/v1/models", timeout=10
        ) as resp:
            models = json.load(resp)
        names = [m["id"] for m in models.get("data", [])]
        print(f"vLLM 연결: {SERVER_URL}")
        print(f"모델: {', '.join(names) or '(없음)'}")
        return True
    except urllib.error.URLError as exc:
        print(f"vLLM 연결 실패: {SERVER_URL}")
        print("위 주석 '서버 실행' 명령을 터미널 1에서 먼저 실행")
        print(exc)
        return False


def main():
    if not check_server():
        sys.exit(1)

    print("=" * 80)
    print("종료: /bye")
    print("=" * 80)

    messages = []

    while True:
        user_input = input("\n[You] >>> ").strip()
        if not user_input:
            continue
        if user_input.lower() == "/bye":
            break

        messages.append({"role": "user", "content": user_input})
        print("\n[AI] >>> ", end="", flush=True)

        try:
            result = chat_completion(messages)
            answer = extract_answer(result["choices"][0]["message"])
            print(answer)
            messages.append({"role": "assistant", "content": answer})
        except urllib.error.URLError as exc:
            print(f"\n요청 실패: {exc}")
            messages.pop()


if __name__ == "__main__":
    main()