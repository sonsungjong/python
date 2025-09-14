# https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
# stable-diffusion-v1-5/stable-diffusion-v1-5
import os
import torch
import cv2
import numpy as np
from PIL import Image
from diffusers import StableDiffusionInpaintPipeline
from segment_anything import SamPredictor, sam_model_registry

# --- 1. 환경 설정 및 모델 로드 ---
# 로컬 모델 및 파일 경로 설정
INPAINTING_MODEL_PATH = "C:/segment-anything/stable-diffusion-v1-5/stable-diffusion-inpainting" # Stable Diffusion Inpainting 모델 경로
SAM_MODEL_PATH = "C:/segment-anything/sam_vit_h_4b8939.pth"  # Segment Anything Model 가중치 경로
INPUT_IMAGE_PATH = "C:/segment-anything/your_document.jpg"  # 워터마크가 있는 이미지 경로
OUTPUT_IMAGE_PATH = "C:/segment-anything/no_watermark.png"  # 결과 이미지 저장 경로

# GPU 사용 설정
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"사용 장치: {device}")

# 인페인팅 파이프라인 로드 (GPU 메모리 최적화를 위해 float16 사용)
pipe = StableDiffusionInpaintPipeline.from_pretrained(INPAINTING_MODEL_PATH, torch_dtype=torch.float16)
pipe = pipe.to(device)

# SAM 모델 로드 (마스크 자동 생성을 위해 사용)
sam = sam_model_registry["vit_h"](checkpoint=SAM_MODEL_PATH)
sam.to(device=device)
sam_predictor = SamPredictor(sam)

# --- 2. 워터마크 마스크 자동 생성 ---
print("마스크 자동 생성 중...")
# 원본 이미지를 OpenCV 형식으로 로드
image_cv = cv2.imread(INPUT_IMAGE_PATH)
image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
sam_predictor.set_image(image_rgb)

# 워터마크의 위치에 대한 박스를 추론하거나 수동으로 지정
# 여기서는 예시로 이미지 중앙에 워터마크가 있다고 가정합니다.
height, width = image_cv.shape[:2]
input_box = np.array([width*0.25, height*0.25, width*0.75, height*0.75])

# SAM을 사용하여 마스크 생성
masks, scores, _ = sam_predictor.predict(
    point_coords=None,
    point_labels=None,
    box=input_box[None, :],
    multimask_output=False,
)

# 생성된 마스크를 흑백 PIL 이미지로 변환
mask_image_np = (masks[0] * 255).astype(np.uint8)
mask_pil = Image.fromarray(mask_image_np, mode='L')

# --- 3. Stable Diffusion으로 워터마크 제거 (인페인팅) ---
print("Stable Diffusion으로 워터마크 제거 중...")
original_image_pil = Image.fromarray(image_rgb)
prompt = "a document, no watermark, clean, professional"

# 인페인팅 파이프라인 실행
output_image = pipe(
    prompt=prompt,
    image=original_image_pil,
    mask_image=mask_pil,
    guidance_scale=7.5,
    num_inference_steps=50,
).images[0]

# --- 4. 결과 저장 ---
output_image.save(OUTPUT_IMAGE_PATH)
print(f"워터마크가 제거된 이미지가 저장되었습니다: {OUTPUT_IMAGE_PATH}")