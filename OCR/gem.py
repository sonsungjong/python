import base64
from PIL import Image
import io

def image_to_base64(path: str) -> str:
    """
    이미지 파일 경로를 받아 base64 문자열로 변환 후 반환합니다.
    """
    with open(path, "rb") as f:
        img_bytes = f.read()
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    return b64

def print_image_base64(path: str, prefix: bool = True):
    """
    이미지 파일 경로를 받아 base64 문자열을 콘솔에 출력합니다.
    prefix=True 이면 'data:image/png;base64,...' 형태로 반환.
    """
    b64 = image_to_base64(path)
    if prefix:
        # 확장자에 맞춰 MIME 타입 붙이기 (png/jpg만 간단 처리)
        mime = "image/png" if path.lower().endswith("png") else "image/jpeg"
        print(f"data:{mime};base64,{b64}")
    else:
        print(b64)



def get_size_from_base64(image_b64: str):
    # "data:image/png;base64,..." 형태도 처리
    if "," in image_b64:
        image_b64 = image_b64.split(",", 1)[1]
    img = Image.open(io.BytesIO(base64.b64decode(image_b64)))
    return img.size  # (W, H)

def normalize_bbox_xyxy(x1, y1, x2, y2, W, H, ndigits=4):
    x1n, y1n = x1 / W, y1 / H
    x2n, y2n = x2 / W, y2 / H
    # 정렬/클램프
    x1n, x2n = sorted((max(0.0, min(1.0, x1n)), max(0.0, min(1.0, x2n))))
    y1n, y2n = sorted((max(0.0, min(1.0, y1n)), max(0.0, min(1.0, y2n))))
    return [round(x1n, ndigits), round(y1n, ndigits), round(x2n, ndigits), round(y2n, ndigits)]

def denormalize_bbox_xyxy(x1n, y1n, x2n, y2n, W, H):
    x1 = int(round(x1n * W)); y1 = int(round(y1n * H))
    x2 = int(round(x2n * W)); y2 = int(round(y2n * H))
    # 정렬/클램프
    x1, x2 = sorted((max(0, min(W, x1)), max(0, min(W, x2))))
    y1, y2 = sorted((max(0, min(H, y1)), max(0, min(H, y2))))
    return [x1, y1, x2, y2]