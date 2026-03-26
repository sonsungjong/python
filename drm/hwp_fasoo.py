# python -m pip install pywin32
# 한글 설치된 컴퓨터에서만 가능
import win32com.client as win32
import os

def test_hwp_automation(file_path):
    # 1. 파일 경로 절대경로로 변환 (필수)
    abs_path = os.path.abspath(file_path)
    
    print("1. 한글 오토메이션 객체 생성 시도...")
    try:
        # HWPFrame.HwpObject는 한글 설치 시 레지스트리에 등록됨
        hwp = win32.gencache.EnsureDispatch("HWPFrame.HwpObject")
        
        # [중요] 보안 모듈 승인창이 뜰 수 있음 -> 화면에서 직접 '허용' 클릭 필요
        # 실제 배포시에는 '보안모듈(FilePathCheckerModule)' 등록이 필요하지만 테스트땐 수동 클릭
        hwp.RegisterModule("FilePathCheckerModule", "FilePathChecker") 
        
        # 백그라운드 실행 여부 (True면 창 안보임, 디버깅 위해 False 추천)
        hwp.XHwpWindows.Item(0).Visible = True 
        
        print(f"2. 파일 열기 시도: {abs_path}")
        # 파일 열기
        if hwp.Open(abs_path):
            print(">> 파일 열기 성공! (DRM 통과)")
        else:
            print(">> 파일 열기 실패. (파일이 없거나, 권한 문제)")
            return

        print("3. 텍스트 추출 시도...")
        # 문서 전체 텍스트 추출 초기화
        hwp.InitScan()
        
        full_text = ""
        state = 2
        while state not in [0, 1]:
            text = hwp.GetText()
            state = text[0]
            full_text += text[1]
        
        hwp.ReleaseScan()
        
        print("-" * 30)
        print(f"추출된 텍스트 길이: {len(full_text)}")
        print(f"내용 미리보기: {full_text[:100]}...")
        print("-" * 30)

        # 4. DRM 우회 저장: 확장자를 .iso로 하면 Fasoo가 무시함
        # 다른 컴퓨터에서 .iso → .hwp로 이름만 바꾸면 정상 오픈
        save_path = os.path.splitext(abs_path)[0] + ".iso"
        if hwp.SaveAs(save_path, "HWP"):
            print(f"4. ISO 확장자로 저장 성공: {save_path}")
            print("   → 다른 PC에서 확장자를 .hwp로 변경 후 열기")
        else:
            print("4. 저장 실패")

        hwp.Quit()

    except Exception as e:
        print(f"에러 발생: {e}")

# 테스트할 HWPX 파일 경로 입력
test_hwp_automation(r"C:\test\FMS-FLM_SDD.hwp")