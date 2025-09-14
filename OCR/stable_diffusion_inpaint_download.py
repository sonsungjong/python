# stable-diffusion-v1-5/stable-diffusion-v1-5
from huggingface_hub import snapshot_download



# 모델이 저장될 로컬 경로

local_path = "C:/segment-anything/stable-diffusion-v1-5"



# 모델 다운로드 실행

snapshot_download(repo_id="stable-diffusion-v1-5/stable-diffusion-v1-5", local_dir=local_path)