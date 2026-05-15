# os 호출로 단순화... 테스트 필요

# exe build:
# pyinstaller --onefile --windowed --name "DRMopen" drm_open_default.py
#
# DRM client installed PC:
# This tool asks Windows to open the selected file with the default associated app.
# If the DRM client is integrated through file association, shell extension, or Office/HWP plugin,
# that normal opening path is usually the one most likely to work.

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


FILETYPES = [
    ("지원 파일", "*.hwp;*.hwpx;*.xls;*.xlsx;*.doc;*.docx;*.ppt;*.pptx;*.txt;*.pdf;*.jpg;*.jpeg;*.png"),
    ("한글 파일", "*.hwp;*.hwpx"),
    ("엑셀 파일", "*.xls;*.xlsx"),
    ("워드 파일", "*.doc;*.docx"),
    ("파워포인트 파일", "*.ppt;*.pptx"),
    ("텍스트 파일", "*.txt"),
    ("PDF 파일", "*.pdf"),
    ("이미지 파일", "*.jpg;*.jpeg;*.png"),
    ("모든 파일", "*.*"),
]


class DrmOpenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DRM 문서 열기")
        self.root.geometry("700x420")
        self.root.resizable(True, True)

        self._build_ui()

    def _build_ui(self):
        frame_top = tk.Frame(self.root, padx=10, pady=10)
        frame_top.pack(fill=tk.X)

        tk.Label(frame_top, text="파일 경로:").pack(side=tk.LEFT)

        self.entry_path = tk.Entry(frame_top)
        self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

        btn_browse = tk.Button(frame_top, text="찾아보기", command=self._browse_file)
        btn_browse.pack(side=tk.LEFT)

        frame_btn = tk.Frame(self.root, padx=10, pady=5)
        frame_btn.pack(fill=tk.X)

        self.btn_open = tk.Button(
            frame_btn, text="기본 프로그램으로 열기", width=22, command=self._on_open
        )
        self.btn_open.pack(side=tk.LEFT)

        frame_log = tk.Frame(self.root, padx=10, pady=5)
        frame_log.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame_log, text="로그:").pack(anchor=tk.W)
        self.log_text = scrolledtext.ScrolledText(frame_log, height=14, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _browse_file(self):
        path = filedialog.askopenfilename(filetypes=FILETYPES)
        if path:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, path)

    def _log(self, msg):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _set_buttons(self, enabled):
        self.btn_open.configure(state=tk.NORMAL if enabled else tk.DISABLED)

    def _get_file_path(self):
        path = self.entry_path.get().strip().strip('"')
        if not path:
            messagebox.showwarning("경고", "파일을 선택하세요.")
            return None

        abs_path = os.path.abspath(path)
        if not os.path.isfile(abs_path):
            messagebox.showerror("오류", f"파일이 존재하지 않습니다:\n{abs_path}")
            return None

        return abs_path

    def _on_open(self):
        abs_path = self._get_file_path()
        if abs_path is None:
            return

        self._set_buttons(False)
        threading.Thread(target=self._run_open, args=(abs_path,), daemon=True).start()

    def _run_open(self, abs_path):
        try:
            self._log("[열기] Windows 기본 연결 프로그램으로 실행 요청 중...")
            os.startfile(abs_path)
            self._log(f"[열기] 요청 완료: {abs_path}")
        except OSError as e:
            self._log(f"[에러] 기본 연결 프로그램으로 열 수 없습니다: {e}")
            self.root.after(
                0,
                messagebox.showerror,
                "오류",
                f"파일을 열 수 없습니다:\n{abs_path}\n\n{e}",
            )
        except Exception as e:
            self._log(f"[에러] {e}")
            self.root.after(0, messagebox.showerror, "오류", str(e))
        finally:
            self.root.after(0, self._set_buttons, True)


if __name__ == "__main__":
    root = tk.Tk()
    app = DrmOpenApp(root)
    root.mainloop()
