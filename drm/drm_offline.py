# ============================================================
# Fasoo DRM 오프라인 복호화 도구
# ============================================================
# 사용법: extract_fasoo.py로 추출한 파일을 이 스크립트와 같은
#         폴더에 넣고 실행
#
# 1단계: extract_fasoo.py를 DRM 클라이언트 PC에서 실행
# 2단계: fasoo_extract 폴더를 오프라인 PC로 복사
# 3단계: 이 스크립트 실행
# ============================================================

import os
import sys
import glob
import json
import ctypes
import ctypes.wintypes
import shutil
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading


class FasooDrmDecryptor:
    """추출된 Fasoo DLL을 이용한 복호화 엔진"""

    def __init__(self, extract_dir="fasoo_extract"):
        self.extract_dir = extract_dir
        self.dll_handle = None
        self.dll_path = None
        self.log_callback = print

    def set_log(self, callback):
        self.log_callback = callback

    def log(self, msg):
        self.log_callback(msg)

    def find_dlls(self):
        """추출된 디렉토리에서 DLL 파일 목록 반환"""
        dlls = []
        for root, dirs, files in os.walk(self.extract_dir):
            for f in files:
                if f.lower().endswith('.dll'):
                    dlls.append(os.path.join(root, f))
        return dlls

    def try_load_dll(self, dll_path):
        """DLL 로드 시도"""
        try:
            # DLL이 있는 디렉토리를 PATH에 추가
            dll_dir = os.path.dirname(dll_path)
            os.environ["PATH"] = dll_dir + ";" + os.environ.get("PATH", "")

            # DLL 의존성도 같은 폴더에서 찾도록 설정
            try:
                ctypes.windll.kernel32.SetDllDirectoryW(dll_dir)
            except:
                pass

            handle = ctypes.windll.LoadLibrary(dll_path)
            self.log(f"  [OK] 로드 성공: {os.path.basename(dll_path)}")

            # Export 함수 목록 확인 (Windows API)
            self._list_exports(handle, dll_path)
            return handle
        except OSError as e:
            self.log(f"  [--] 로드 실패: {os.path.basename(dll_path)}: {e}")
            return None

    def _list_exports(self, handle, dll_path):
        """로드된 DLL의 export 함수 중 decrypt 관련 찾기"""
        # 알려진 Fasoo API 함수명
        known_funcs = [
            "FSD_Open", "FSD_Close", "FSD_Read", "FSD_Write",
            "FSD_Decrypt", "FSD_Encrypt",
            "FSDecrypt", "FSEncrypt",
            "DecryptFile", "EncryptFile",
            "OpenSecureFile", "CloseSecureFile",
            "FxDecrypt", "FxEncrypt",
            "DRMDecrypt", "DRMEncrypt",
            "SL_Open", "SL_Decrypt",
            "InitDRM", "UninitDRM",
            "Initialize", "Uninitialize",
            "DecryptDocument", "OpenDocument",
            "FSD_DecryptFile", "FSD_EncryptFile",
            "ConvertToPlain", "ConvertFromPlain",
        ]

        found_funcs = []
        for func_name in known_funcs:
            try:
                addr = ctypes.windll.kernel32.GetProcAddress(handle, func_name.encode())
                if addr:
                    found_funcs.append(func_name)
                    self.log(f"    함수 발견: {func_name}")
            except:
                pass

        return found_funcs

    def discover_and_load(self):
        """모든 DLL을 시도하여 사용 가능한 것을 찾기"""
        self.log("추출된 DLL 검색 중...")
        dlls = self.find_dlls()

        if not dlls:
            self.log("[에러] fasoo_extract 폴더에 DLL이 없습니다.")
            self.log("       extract_fasoo.py를 DRM PC에서 먼저 실행하세요.")
            return False

        self.log(f"발견된 DLL: {len(dlls)}개")

        for dll_path in dlls:
            handle = self.try_load_dll(dll_path)
            if handle:
                self.dll_handle = handle
                self.dll_path = dll_path
                # 첫 번째 성공한 DLL 사용 (나중에 선택 가능)

        if self.dll_handle:
            self.log(f"\n사용할 DLL: {self.dll_path}")
            return True
        else:
            self.log("\n[경고] 로드 가능한 DLL을 찾지 못했습니다.")
            self.log("       DRM PC에서 extract_fasoo.py를 관리자 권한으로 실행해보세요.")
            return False

    def decrypt_file(self, drm_path, output_path):
        """DRM 파일 복호화 시도"""
        self.log(f"\n복호화 시도: {drm_path}")

        # DRM 파일 헤더 확인
        with open(drm_path, "rb") as f:
            header = f.read(256)

        if b"DRMONE" not in header[:64]:
            self.log("[경고] Fasoo DRM 파일이 아닌 것 같습니다.")
            return False

        self.log("  Fasoo DRM 헤더 확인됨")

        if not self.dll_handle:
            self.log("[에러] DLL이 로드되지 않았습니다.")
            return False

        # 다양한 API 호출 시도
        success = False

        # 시도 1: FSD_DecryptFile(input, output)
        for func_name in ["FSD_DecryptFile", "DecryptFile", "ConvertToPlain",
                          "FSDecrypt", "FxDecrypt", "DRMDecrypt"]:
            try:
                func = getattr(self.dll_handle, func_name)
                # 다양한 호출 규약 시도
                for args in [
                    (drm_path.encode(), output_path.encode()),
                    (drm_path.encode("utf-16-le"), output_path.encode("utf-16-le")),
                    (ctypes.c_wchar_p(drm_path), ctypes.c_wchar_p(output_path)),
                ]:
                    try:
                        result = func(*args)
                        if os.path.isfile(output_path) and os.path.getsize(output_path) > 0:
                            self.log(f"  [성공] {func_name}으로 복호화 완료!")
                            success = True
                            break
                    except Exception as e:
                        continue
                if success:
                    break
            except AttributeError:
                continue

        if not success:
            # 시도 2: Initialize + Open + Read 패턴
            for init_name in ["InitDRM", "Initialize", "FSD_Init"]:
                try:
                    init_func = getattr(self.dll_handle, init_name)
                    init_func()
                    self.log(f"  {init_name} 호출 성공")
                except:
                    continue

            # 시도 3: COM-like 패턴
            self.log("  [정보] 자동 복호화 실패. 수동 설정이 필요할 수 있습니다.")
            self.log("         manifest.json의 함수 목록을 확인하세요.")

        return success


class OfflineDrmApp:
    """오프라인 PC용 DRM 복호화 GUI"""

    FILETYPES = [
        ("지원 파일", "*.hwp;*.hwpx;*.xls;*.xlsx;*.doc;*.docx;*.ppt;*.pptx;*.txt;*.pdf;*.jpg;*.jpeg;*.png"),
        ("모든 파일", "*.*"),
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("DRM 오프라인 복호화 도구")
        self.root.geometry("750x550")
        self.root.resizable(True, True)

        self.decryptor = FasooDrmDecryptor()
        self._build_ui()

        # 시작 시 DLL 자동 검색
        self.root.after(500, self._auto_discover)

    def _build_ui(self):
        # DLL 경로
        frame_dll = tk.Frame(self.root, padx=10, pady=5)
        frame_dll.pack(fill=tk.X)
        tk.Label(frame_dll, text="DLL 폴더:").pack(side=tk.LEFT)
        self.entry_dll = tk.Entry(frame_dll)
        self.entry_dll.insert(0, "fasoo_extract")
        self.entry_dll.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Button(frame_dll, text="변경", command=self._browse_dll).pack(side=tk.LEFT)
        tk.Button(frame_dll, text="DLL 로드", command=self._load_dlls).pack(side=tk.LEFT, padx=5)

        # 파일 선택
        frame_file = tk.Frame(self.root, padx=10, pady=5)
        frame_file.pack(fill=tk.X)
        tk.Label(frame_file, text="DRM 파일:").pack(side=tk.LEFT)
        self.entry_path = tk.Entry(frame_file)
        self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Button(frame_file, text="찾아보기", command=self._browse_file).pack(side=tk.LEFT)

        # 버튼
        frame_btn = tk.Frame(self.root, padx=10, pady=5)
        frame_btn.pack(fill=tk.X)
        self.btn_decrypt = tk.Button(
            frame_btn, text="복호화 (.iso로 저장)", width=20,
            command=self._on_decrypt, state=tk.DISABLED
        )
        self.btn_decrypt.pack(side=tk.LEFT, padx=5)

        self.btn_strip = tk.Button(
            frame_btn, text="헤더 제거 시도", width=15,
            command=self._on_strip_header
        )
        self.btn_strip.pack(side=tk.LEFT, padx=5)

        # 로그
        frame_log = tk.Frame(self.root, padx=10, pady=5)
        frame_log.pack(fill=tk.BOTH, expand=True)
        tk.Label(frame_log, text="로그:").pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(frame_log, height=18, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _log(self, msg):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _browse_dll(self):
        path = filedialog.askdirectory()
        if path:
            self.entry_dll.delete(0, tk.END)
            self.entry_dll.insert(0, path)

    def _browse_file(self):
        path = filedialog.askopenfilename(filetypes=self.FILETYPES)
        if path:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, path)

    def _auto_discover(self):
        self._load_dlls()

    def _load_dlls(self):
        extract_dir = self.entry_dll.get().strip()
        self.decryptor.extract_dir = extract_dir
        self.decryptor.set_log(self._log)

        if not os.path.isdir(extract_dir):
            self._log(f"[경고] 폴더 없음: {extract_dir}")
            self._log("extract_fasoo.py를 DRM PC에서 먼저 실행하세요.")
            return

        if self.decryptor.discover_and_load():
            self.btn_decrypt.configure(state=tk.NORMAL)

    def _on_decrypt(self):
        drm_path = self.entry_path.get().strip()
        if not drm_path or not os.path.isfile(drm_path):
            messagebox.showwarning("경고", "DRM 파일을 선택하세요.")
            return

        output_path = os.path.splitext(drm_path)[0] + ".iso"

        def work():
            self.decryptor.decrypt_file(drm_path, output_path)

        threading.Thread(target=work, daemon=True).start()

    def _on_strip_header(self):
        """DRM 헤더 제거 시도 (본문이 암호화되지 않은 경우용)"""
        drm_path = self.entry_path.get().strip()
        if not drm_path or not os.path.isfile(drm_path):
            messagebox.showwarning("경고", "DRM 파일을 선택하세요.")
            return

        with open(drm_path, "rb") as f:
            data = f.read()

        if b"DRMONE" not in data[:64]:
            self._log("[경고] Fasoo DRM 파일이 아닙니다.")
            return

        # PK 시그니처 검색 (OOXML)
        pk_sig = b'\x50\x4B\x03\x04'
        # OLE2 시그니처 검색 (HWP, 구 Office)
        ole_sig = b'\xD0\xCF\x11\xE0'
        # PDF 시그니처
        pdf_sig = b'%PDF'

        for sig_name, sig in [("OOXML(PK)", pk_sig), ("OLE2", ole_sig), ("PDF", pdf_sig)]:
            offset = data.find(sig)
            if offset > 0:
                self._log(f"[발견] {sig_name} 시그니처 at offset 0x{offset:X}")
                output_path = os.path.splitext(drm_path)[0] + ".iso"
                with open(output_path, "wb") as f:
                    f.write(data[offset:])
                self._log(f"[저장] 헤더 제거 파일: {output_path}")
                self._log(f"  원본: {len(data):,} bytes → 결과: {len(data)-offset:,} bytes")
                return

        self._log("[실패] 본문에서 파일 시그니처를 찾지 못했습니다.")
        self._log("  → 본문이 암호화되어 있습니다. DLL 복호화가 필요합니다.")


if __name__ == "__main__":
    root = tk.Tk()
    app = OfflineDrmApp(root)
    root.mainloop()
