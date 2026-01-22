# python -m pip install pywin32
# MS오피스 설치된 컴퓨터에서 가능

import win32com.client as win32
import os

def read_drm_excel(file_path):
    excel = None
    try:
        # 엑셀 어플리케이션 실행 (백그라운드)
        excel = win32.gencache.EnsureDispatch("Excel.Application")
        excel.Visible = False  # 창 안 뜨게 하기
        excel.DisplayAlerts = False # 저장할까요? 같은 팝업 무시

        abs_path = os.path.abspath(file_path)
        print(f"엑셀 여는 중: {abs_path}")
        
        # 여기서 DRM 해제됨 (PC에 권한이 있다면)
        wb = excel.Workbooks.Open(abs_path)
        ws = wb.ActiveSheet

        # 예시: A1 셀 값 읽기
        val = ws.Range("A1").Value
        print(f"A1 셀 내용: {val}")

        # 전체 데이터 읽어서 리눅스로 보낼 텍스트/JSON 만들기
        # ... (데이터 추출 로직) ...

        wb.Close(False) # 저장 안 하고 닫기

    except Exception as e:
        print(f"에러 발생: {e}")
    finally:
        if excel:
            excel.Quit()


def read_drm_word(file_path):
    word = None
    try:
        word = win32.gencache.EnsureDispatch("Word.Application")
        word.Visible = False
        
        abs_path = os.path.abspath(file_path)
        
        # 문서 열기 (DRM 해제)
        doc = word.Documents.Open(abs_path)
        
        # 전체 텍스트 추출
        full_text = doc.Content.Text
        print(f"문서 내용(일부): {full_text[:100]}...")
        
        doc.Close(False)
        
    except Exception as e:
        print(f"에러: {e}")
    finally:
        if word:
            word.Quit()


import win32com.client as win32
import os

def read_drm_ppt(file_path):
    ppt_app = None
    presentation = None
    
    try:
        # 1. 파워포인트 어플리케이션 실행
        # PPT는 백그라운드 실행 시 DRM 훅이 잘 안 걸리는 경우가 있어 Visible=True가 안전함
        ppt_app = win32.gencache.EnsureDispatch("PowerPoint.Application")
        ppt_app.Visible = True 

        abs_path = os.path.abspath(file_path)
        print(f"PPT 여는 중: {abs_path}")

        # 2. 파일 열기 (여기서 DRM 해제됨)
        # WithWindow=True로 해야 DRM 모듈이 정상 동작할 확률이 높음
        presentation = ppt_app.Presentations.Open(abs_path, WithWindow=True)

        full_text = []

        # 3. 슬라이드 순회
        for i, slide in enumerate(presentation.Slides):
            print(f"--- 슬라이드 {i+1} 처리 중 ---")
            slide_text = []
            
            # 슬라이드 내의 모든 도형(Shape) 순회
            for shape in slide.Shapes:
                # 텍스트가 있는 도형인지 확인 (HasTextFrame)
                if shape.HasTextFrame:
                    if shape.TextFrame.HasText:
                        text = shape.TextFrame.TextRange.Text
                        slide_text.append(text)
                
                # (심화) 그룹화된 도형이나 표(Table) 안에 있는 텍스트는 
                # 별도 재귀 로직이 필요할 수 있으나, 기본적으로는 위 로직으로 대부분 커버됨

            # 슬라이드 별 텍스트 합치기
            full_text.append(f"[Slide {i+1}]\n" + "\n".join(slide_text))

        # 4. 결과 출력 또는 리눅스로 전송할 파일 생성
        final_content = "\n\n".join(full_text)
        print("="*30)
        print(final_content[:200] + "...") # 미리보기
        print("="*30)

        # 저장하지 않고 닫기
        presentation.Close()

    except Exception as e:
        print(f"에러 발생: {e}")
    finally:
        if ppt_app:
            # PPT 프로세스 종료
            ppt_app.Quit()


# 테스트
read_drm_excel(r"C:\test\secure_file.xlsx")
# read_drm_ppt(r"C:\Test\secure_presentation.pptx")