from PIL import Image, ImageDraw
import math

# 캔버스 설정 및 여백 (좌측 상단, 우측 하단 여백 32픽셀)
img_size = (256, 256)
margin = 32

# 256x256 투명 배경 이미지 생성 (RGBA 모드)
img = Image.new("RGBA", img_size, (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 렌즈(원) 파라미터 설정
lens_radius = 75
center = (lens_radius + margin, lens_radius + margin)  # (75+32, 75+32) = (107, 107)

angle = math.radians(45)  # 45도 방향

# 우측 하단 여백이 32픽셀이 되도록 목표 좌표는 (224, 224) = (256-32, 256-32)
# 45도 방향에서 center[0] + (lens_radius + handle_length)*cos45 = 224
handle_length = ((224 - center[0]) / math.cos(angle)) - lens_radius  # 약 90 픽셀 정도

# 선 두께를 16픽셀로 설정
line_width = 16

# 렌즈(원) 그리기: 중심을 기준으로 하는 바운딩 박스 계산
left = center[0] - lens_radius
top = center[1] - lens_radius
right = center[0] + lens_radius
bottom = center[1] + lens_radius
lens_bbox = (left, top, right, bottom)
draw.ellipse(lens_bbox, outline="white", width=line_width)

# 손잡이 그리기: 렌즈 경계상의 45도 방향에서 시작해 손잡이 길이만큼 연장
start_x = center[0] + lens_radius * math.cos(angle)
start_y = center[1] + lens_radius * math.sin(angle)
start = (start_x, start_y)

end_x = center[0] + (lens_radius + handle_length) * math.cos(angle)
end_y = center[1] + (lens_radius + handle_length) * math.sin(angle)
end = (end_x, end_y)
draw.line((start, end), fill="white", width=line_width)

# 결과 PNG 파일로 저장 및 표시
img.save("search_icon_adjusted4.png")
img.show()
