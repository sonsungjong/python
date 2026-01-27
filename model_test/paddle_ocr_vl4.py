# PaddlePaddle/PaddleOCR-VL

'''
python -m pip install paddlepaddle-gpu==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
python -m pip install -U "paddleocr[doc-parser]"

윈도우즈 : python -m pip install https://xly-devops.cdn.bcebos.com/safetensors-nightly/safetensors-0.6.2.dev0-cp38-abi3-win_amd64.whl
리눅스 : python -m pip install https://paddle-whl.bj.bcebos.com/nightly/cu126/safetensors/safetensors-0.6.2.dev0-cp38-abi3-linux_x86_64.whl
'''

from paddleocr import PaddleOCRVL
import os
import glob
import math
from PIL import Image

# 지원하는 이미지 확장자
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp']
MAX_PIXELS = 2_000_000  # 최대 픽셀 수 (약 1414x1414)

# 모델 로드 (한 번만 로드)
print("모델 로딩 중...")
pipeline = PaddleOCRVL()
print("모델 로딩 완료!")

def downscale_image(image_path):
    """이미지가 너무 크면 리사이즈"""
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    n = w * h
    
    if n > MAX_PIXELS:
        scale = math.sqrt(MAX_PIXELS / n)
        new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
        img = img.resize((new_w, new_h), Image.LANCZOS)
        print(f"  이미지 리사이즈: {w}x{h} -> {new_w}x{new_h}")
        
        # 리사이즈된 이미지를 임시로 저장
        resized_path = image_path + ".resized.png"
        img.save(resized_path, optimize=True)
        return resized_path, True  # 리사이즈됨
    
    return image_path, False  # 원본 사용

def get_images_from_folder(folder_path):
    """폴더에서 모든 이미지 파일 경로 반환"""
    images = set()  # 중복 방지를 위해 set 사용
    for ext in IMAGE_EXTENSIONS:
        images.update(glob.glob(os.path.join(folder_path, f"*{ext}")))
    return sorted(images)

def process_image(image_path):
    """이미지 경로를 받아서 OCR 처리"""
    print(f"\n처리 중: {image_path}")
    
    # 이미지 리사이즈
    resized_path, was_resized = downscale_image(image_path)
    
    try:
        output = pipeline.predict(resized_path)
        for res in output:
            res.print()
            res.save_to_json(save_path="output")
            res.save_to_markdown(save_path="output")
    finally:
        # 리사이즈된 임시 파일 삭제
        if was_resized and os.path.exists(resized_path):
            os.remove(resized_path)
    
    print("처리 완료!")

def process_path(input_path):
    """파일 또는 폴더 경로를 받아서 처리"""
    if not os.path.exists(input_path):
        print(f"오류: 경로를 찾을 수 없습니다 - {input_path}")
        return
    
    if os.path.isdir(input_path):
        # 폴더인 경우: 모든 이미지 처리
        images = get_images_from_folder(input_path)
        if not images:
            print(f"오류: 폴더에 이미지가 없습니다 - {input_path}")
            return
        
        print(f"\n총 {len(images)}개의 이미지를 처리합니다...")
        for i, img_path in enumerate(images, 1):
            print(f"\n[{i}/{len(images)}]", end="")
            process_image(img_path)
    else:
        # 파일인 경우: 단일 이미지 처리
        process_image(input_path)

if __name__ == "__main__":
    while True:
        input_path = input("\n이미지 또는 폴더 경로를 입력하세요 (종료: q): ").strip()
        
        if input_path.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
        
        if input_path:
            process_path(input_path)
        else:
            print("경로를 입력해주세요.")
