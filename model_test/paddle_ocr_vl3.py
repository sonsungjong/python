# PaddlePaddle/PaddleOCR-VL

'''
python -m pip install paddlepaddle-gpu==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
python -m pip install -U "paddleocr[doc-parser]"

윈도우즈 : python -m pip install https://xly-devops.cdn.bcebos.com/safetensors-nightly/safetensors-0.6.2.dev0-cp38-abi3-win_amd64.whl
리눅스 : python -m pip install https://paddle-whl.bj.bcebos.com/nightly/cu126/safetensors/safetensors-0.6.2.dev0-cp38-abi3-linux_x86_64.whl
'''

from paddleocr import PaddleOCRVL
import os

# 모델 로드 (한 번만 로드)
print("모델 로딩 중...")
pipeline = PaddleOCRVL()
print("모델 로딩 완료!")

def process_image(image_path):
    """이미지 경로를 받아서 OCR 처리"""
    if not os.path.exists(image_path):
        print(f"오류: 파일을 찾을 수 없습니다 - {image_path}")
        return
    
    print(f"\n처리 중: {image_path}")
    output = pipeline.predict(image_path)
    for res in output:
        res.print()
        res.save_to_json(save_path="output")
        res.save_to_markdown(save_path="output")
    print("처리 완료!")

if __name__ == "__main__":
    while True:
        image_path = input("\n이미지 경로를 입력하세요 (종료: q): ").strip()
        
        if image_path.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
        
        if image_path:
            process_image(image_path)
        else:
            print("경로를 입력해주세요.")
