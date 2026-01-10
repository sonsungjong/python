# PaddlePaddle/PaddleOCR-VL

'''
python -m pip install paddlepaddle-gpu==3.2.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
python -m pip install -U "paddleocr[doc-parser]"

윈도우즈 : python -m pip install https://xly-devops.cdn.bcebos.com/safetensors-nightly/safetensors-0.6.2.dev0-cp38-abi3-win_amd64.whl
리눅스 : python -m pip install https://paddle-whl.bj.bcebos.com/nightly/cu126/safetensors/safetensors-0.6.2.dev0-cp38-abi3-linux_x86_64.whl
'''

import os, math, tempfile
from PIL import Image
from paddleocr import PaddleOCRVL

output_path = os.path.join(os.path.dirname(__file__), "output")

def downscale_cap(in_path: str):
    file_save = True                   # True: 파일 저장, False: 저장 안함 (임시 파일)
    max_pixels = 2_000_000

    img = Image.open(in_path).convert("RGB")
    w, h = img.size
    n = w * h
    if n > max_pixels:
        scale = math.sqrt(max_pixels / n)
        img = img.resize((max(1, int(w*scale)), max(1, int(h*scale))), Image.LANCZOS)
    
    if file_save:
        os.makedirs(output_path, exist_ok=True)
        out_path = os.path.join(output_path, os.path.basename(in_path))
        img.save(out_path, optimize=True)
        return out_path, lambda: None  # 영구 저장, cleanup 불필요
    else:
        # 임시 파일 생성
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp_path = tmp.name
        tmp.close()
        img.save(tmp_path, optimize=True)
        return tmp_path, lambda: os.remove(tmp_path)  # 임시 파일 경로와 삭제 함수 반환

pipeline = PaddleOCRVL()

img_path, cleanup = downscale_cap(r"C:\img\01^0001.png")
try:
    output = pipeline.predict(img_path)
    for res in output:
        res.print()
        res.save_to_json(save_path=output_path)
        res.save_to_markdown(save_path=output_path)
finally:
    cleanup()  # file_save=False일 때 임시파일 삭제

