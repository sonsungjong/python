# pat-jj/harness-1
# ijohn07/harness-1-Q4_K_M-GGUF
# https://huggingface.co/pat-jj/harness-1
# https://huggingface.co/ijohn07/harness-1-Q4_K_M-GGUF

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

# 모델 다운로드:
'''
hf download ijohn07/harness-1-Q4_K_M-GGUF harness-1-q4_k_m.gguf
'''
# 서버 실행:
'''
~/llama.cpp/build/bin/llama-server \
  -m ~/.cache/huggingface/hub/models--ijohn07--harness-1-Q4_K_M-GGUF/snapshots/*/harness-1-q4_k_m.gguf \
  -ngl 999 \
  -fa on \
  --parallel 3 \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  -c 65536 \
  --port 11435
'''
# 서버 종료:
# Ctrl+C 또는
# pkill -f llama-server
# 또는 PID로 종료: kill $(pgrep -f llama-server)

