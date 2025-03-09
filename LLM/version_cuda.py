import torch
print("PyTorch 버전:", torch.__version__)
print("CUDA 지원 여부:", torch.cuda.is_available())
print("PyTorch가 인식한 CUDA 버전:", torch.version.cuda)
print("GPU 개수:", torch.cuda.device_count())
print("GPU 이름:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CUDA 없음")