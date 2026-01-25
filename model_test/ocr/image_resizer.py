import os
import math
from PIL import Image
import sys

def downscale_image(in_path: str, max_pixels=2_000_000):
    """
    이미지 해상도가 max_pixels를 초과하면 비율 유지하며 축소하여 저장
    파일명_resized.ext 형태로 저장됨
    """
    try:
        # 파일 존재 확인
        if not os.path.exists(in_path):
            print(f"파일을 찾을 수 없습니다: {in_path}")
            return

        img = Image.open(in_path).convert("RGB")
        w, h = img.size
        n = w * h
        
        # 원본 정보 출력
        print(f"원본: {os.path.basename(in_path)} ({w}x{h}, {n:,} pixels)")

        if n > max_pixels:
            scale = math.sqrt(max_pixels / n)
            new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
            
            print(f" -> 리사이즈 진행: {new_w}x{new_h} (약 {int(scale*100)}%)")
            img = img.resize((new_w, new_h), Image.LANCZOS)
            
            # 저장 경로 생성 (파일명_resized.ext)
            base, ext = os.path.splitext(in_path)
            out_path = f"{base}_resized{ext}"
            
            img.save(out_path, optimize=True)
            print(f" -> 저장 완료: {os.path.basename(out_path)}")
            return out_path
        else:
            print(f" -> 리사이즈 불필요 (기준 {max_pixels:,} pixels 이하)")
            return in_path
            
    except Exception as e:
        print(f"이미지 처리 실패: {e}")
        return None

def main():
    print("=" * 60)
    print("이미지 리사이저 (200만 화소 기준 축소)")
    print("사용법: python image_resizer.py [이미지파일명]")
    print("=" * 60)
    
    # 인자로 파일명 받거나 입력받기
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        target_file = input("이미지 파일명을 입력하세요: ").strip()

    # 경로 처리 (현재 폴더 기준이라고 가정)
    if not os.path.exists(target_file):
         # 혹시 그냥 파일명만 입력했을 경우를 대비해 현재 폴더 체크
         target_file = os.path.join(os.path.dirname(__file__), target_file)

    downscale_image(target_file)

if __name__ == "__main__":
    main()
