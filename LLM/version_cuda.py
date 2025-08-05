# pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0
# pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
# pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126
import subprocess
import torch
import torchvision
import torchaudio

print("GPU와 호환 가능한 CUDA:")
try:
    out = subprocess.check_output("nvidia-smi", encoding="utf-8")
    for line in out.splitlines():
        if "CUDA Version" in line:
            print(line.strip())
except Exception as e:
    print("nvidia-smi 실행 실패:", e)

print("로컬에 설치된 CUDA:")
try:
    out = subprocess.check_output("nvcc --version", shell=True, encoding="utf-8")
    for line in out.splitlines():
        if "release" in line:
            print(line.strip())
except Exception as e:
    print("nvcc 실행 실패:", e)



print("PyTorch 버전:", torch.__version__)
print("PyTorch Vision 버전:",torchvision.__version__)
print("PyTorch Audio 버전:",torchaudio.__version__)
print("CUDA 지원 여부:", torch.cuda.is_available())
print("PyTorch가 인식한 CUDA 버전:", torch.version.cuda)
print("GPU 개수:", torch.cuda.device_count())
print("GPU 이름:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CUDA 없음")