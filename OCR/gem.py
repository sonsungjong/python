from PIL import Image

def normalize_bbox(x1, y1, x2, y2, image_path):
    img = Image.open(image_path)
    w, h = img.size  # (width, height)
    return [
        round(x1 / w, 4),
        round(y1 / h, 4),
        round(x2 / w, 4),
        round(y2 / h, 4)
    ]

# 사용 예시
bbox = normalize_bbox(120, 200, 340, 260, "./")
print(bbox)  # [0.0938, 0.2083, 0.2656, 0.2708]