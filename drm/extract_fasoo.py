# ============================================================
# Fasoo DRM 클라이언트 파일 추출 스크립트
# ============================================================
# 사용법: DRM 클라이언트가 설치된 PC에서 USB에 복사 후 실행
#   python extract_fasoo.py [출력폴더]
#   예: python extract_fasoo.py E:\fasoo_files
#
# Python 없는 PC라면 exe로 빌드:
#   pyinstaller --onefile extract_fasoo.py
# ============================================================

import os
import sys
import shutil
import glob
import json
import winreg
import ctypes
from datetime import datetime


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def safe_copy(src, dst_dir, label=""):
    """파일을 안전하게 복사하고 결과를 반환"""
    try:
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, os.path.basename(src))
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            size = os.path.getsize(src)
            log(f"  [OK] {src} ({size:,} bytes)")
            return {"src": src, "dst": dst, "size": size, "label": label}
        elif os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            log(f"  [OK] {src} (directory)")
            return {"src": src, "dst": dst, "size": 0, "label": label + " (dir)"}
    except Exception as e:
        log(f"  [FAIL] {src}: {e}")
    return None


def search_filesystem(output_dir):
    """파일시스템에서 Fasoo 관련 파일 검색"""
    log("=" * 60)
    log("STEP 1: 파일시스템 검색")
    log("=" * 60)

    results = []

    # 1. 알려진 Fasoo 설치 경로
    known_paths = [
        r"C:\Program Files\Fasoo",
        r"C:\Program Files (x86)\Fasoo",
        r"C:\Program Files\Fasoo DRM",
        r"C:\Program Files (x86)\Fasoo DRM",
        r"C:\ProgramData\Fasoo",
        r"C:\ProgramData\FasooClient",
        r"C:\Fasoo",
        # SoftCamp (다른 DRM 벤더도 확인)
        r"C:\Program Files\SoftCamp",
        r"C:\Program Files (x86)\SoftCamp",
        # MarkAny
        r"C:\Program Files\MarkAny",
        r"C:\Program Files (x86)\MarkAny",
    ]

    log("\n[1-1] 알려진 설치 경로 검색...")
    for path in known_paths:
        if os.path.exists(path):
            log(f"  *** 발견: {path}")
            r = safe_copy(path, os.path.join(output_dir, "install"), "install_dir")
            if r:
                results.append(r)

    # 2. System32/SysWOW64에서 Fasoo DLL 검색
    log("\n[1-2] System32/SysWOW64 DLL 검색...")
    sys_dirs = [
        os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32"),
        os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "SysWOW64"),
    ]

    fasoo_dll_patterns = [
        "f_*.dll", "fs_*.dll", "fd_*.dll",
        "fasoo*.dll", "fsd*.dll", "fxlib*.dll",
        "FSClient*.dll", "SLClient*.dll",
        "drmone*.dll", "DRMONE*.dll",
        "*fasoo*", "*Fasoo*", "*FASOO*",
        "*drmone*", "*DRMONE*", "*DrmOne*",
    ]

    for sys_dir in sys_dirs:
        if not os.path.exists(sys_dir):
            continue
        for pattern in fasoo_dll_patterns:
            for f in glob.glob(os.path.join(sys_dir, pattern)):
                r = safe_copy(f, os.path.join(output_dir, "system_dlls"), "system_dll")
                if r:
                    results.append(r)

    # 3. 사용자 프로필의 AppData 검색
    log("\n[1-3] AppData 검색...")
    appdata_dirs = [
        os.path.expandvars(r"%LOCALAPPDATA%\Fasoo"),
        os.path.expandvars(r"%APPDATA%\Fasoo"),
        os.path.expandvars(r"%LOCALAPPDATA%\FasooClient"),
        os.path.expandvars(r"%APPDATA%\FasooClient"),
    ]
    for path in appdata_dirs:
        if os.path.exists(path):
            log(f"  *** 발견: {path}")
            r = safe_copy(path, os.path.join(output_dir, "appdata"), "appdata")
            if r:
                results.append(r)

    # 4. 전체 Program Files 스캔 (DRM/DRMOne 키워드)
    log("\n[1-4] Program Files 전체 스캔...")
    for pf in [r"C:\Program Files", r"C:\Program Files (x86)"]:
        if not os.path.exists(pf):
            continue
        try:
            for entry in os.listdir(pf):
                entry_lower = entry.lower()
                if any(kw in entry_lower for kw in ["fasoo", "drm", "drmone", "softcamp", "markany"]):
                    full = os.path.join(pf, entry)
                    log(f"  *** 발견: {full}")
                    r = safe_copy(full, os.path.join(output_dir, "programs"), "program_dir")
                    if r:
                        results.append(r)
        except PermissionError:
            pass

    # 5. 서비스 실행 파일 검색
    log("\n[1-5] 실행 중인 프로세스의 DRM 관련 DLL 검색...")
    try:
        import subprocess
        # tasklist /m 으로 로드된 모듈 확인
        result = subprocess.run(
            ["tasklist", "/m", "/fo", "csv"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.split("\n"):
            line_lower = line.lower()
            if any(kw in line_lower for kw in ["fasoo", "drmone", "f_com", "f_sps", "fsd", "fxlib"]):
                log(f"  프로세스 모듈: {line.strip()}")
    except Exception as e:
        log(f"  프로세스 검색 실패: {e}")

    return results


def search_registry(output_dir):
    """레지스트리에서 Fasoo 관련 키 검색"""
    log("\n" + "=" * 60)
    log("STEP 2: 레지스트리 검색")
    log("=" * 60)

    reg_results = {}

    # 검색할 레지스트리 경로
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Fasoo"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Fasoo"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\DRMOne"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\DRMOne"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Fasoo"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\DRMOne"),
        # COM 객체 등록 정보
        (winreg.HKEY_CLASSES_ROOT, r"CLSID"),
    ]

    def read_reg_tree(hive, path, depth=0):
        """레지스트리 트리를 재귀적으로 읽기"""
        result = {}
        try:
            key = winreg.OpenKey(hive, path)
            # 값 읽기
            i = 0
            while True:
                try:
                    name, value, vtype = winreg.EnumValue(key, i)
                    result[name] = {"value": str(value), "type": vtype}
                    i += 1
                except OSError:
                    break

            # 하위 키 읽기 (깊이 제한)
            if depth < 3:
                j = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, j)
                        subpath = f"{path}\\{subkey_name}"
                        sub_result = read_reg_tree(hive, subpath, depth + 1)
                        if sub_result:
                            result[f"[{subkey_name}]"] = sub_result
                        j += 1
                    except OSError:
                        break
            winreg.CloseKey(key)
        except OSError:
            pass
        return result

    for hive, path in reg_paths:
        if path == r"CLSID":
            # CLSID는 너무 크므로 Fasoo 관련만 검색
            continue
        hive_name = {
            winreg.HKEY_LOCAL_MACHINE: "HKLM",
            winreg.HKEY_CURRENT_USER: "HKCU",
            winreg.HKEY_CLASSES_ROOT: "HKCR",
        }.get(hive, "?")

        result = read_reg_tree(hive, path)
        if result:
            key_path = f"{hive_name}\\{path}"
            log(f"  *** 발견: {key_path}")
            reg_results[key_path] = result

    # Fasoo COM 객체 검색
    log("\n[2-2] Fasoo COM 객체 검색...")
    try:
        clsid_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "CLSID")
        i = 0
        while True:
            try:
                clsid = winreg.EnumKey(clsid_key, i)
                try:
                    desc_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f"CLSID\\{clsid}")
                    desc = winreg.QueryValue(desc_key, "")
                    if desc and any(kw in desc.lower() for kw in ["fasoo", "drmone", "drm"]):
                        log(f"  COM: {clsid} = {desc}")
                        # InprocServer32 경로 가져오기
                        try:
                            srv_key = winreg.OpenKey(
                                winreg.HKEY_CLASSES_ROOT,
                                f"CLSID\\{clsid}\\InprocServer32"
                            )
                            dll_path = winreg.QueryValue(srv_key, "")
                            log(f"       DLL: {dll_path}")
                            reg_results[f"COM_{clsid}"] = {
                                "description": desc,
                                "dll": dll_path
                            }
                            # 해당 DLL 복사
                            if os.path.isfile(dll_path):
                                safe_copy(
                                    dll_path,
                                    os.path.join(output_dir, "com_dlls"),
                                    "com_dll"
                                )
                            winreg.CloseKey(srv_key)
                        except OSError:
                            pass
                    winreg.CloseKey(desc_key)
                except OSError:
                    pass
                i += 1
            except OSError:
                break
        winreg.CloseKey(clsid_key)
    except OSError:
        log("  CLSID 검색 실패")

    # 결과 저장
    reg_file = os.path.join(output_dir, "registry_dump.json")
    with open(reg_file, "w", encoding="utf-8") as f:
        json.dump(reg_results, f, indent=2, ensure_ascii=False, default=str)
    log(f"\n  레지스트리 덤프 저장: {reg_file}")

    return reg_results


def search_loaded_dlls(output_dir):
    """현재 시스템에 로드 가능한 DRM DLL 검색"""
    log("\n" + "=" * 60)
    log("STEP 3: DRM DLL 로드 테스트")
    log("=" * 60)

    # 알려진 Fasoo DLL 이름들
    dll_names = [
        "FSD.dll", "FSClient.dll", "FxLib.dll",
        "f_Com_C.dll", "f_sps.dll", "f_crypt.dll",
        "SLClient.dll", "DRMOneClient.dll",
        "FasooLib.dll", "FasooClient.dll",
        "fdcore.dll", "fsdrm.dll",
        # memo.md에서 발견된 DLL들 추가
        "f_nxa.dll", "f_nxacc.dll", "f_im.dll",
        "f_fdcrm.dll", "f_executor.dll", "f_ckm.dll",
        "f_nxl.dll", "f_depol.dll", "f_cms.dll",
        "f_pdm.dll", "f_logcore.dll", "f_lph.dll",
        "f_distri.dll", "f_xltsm.dll", "f_sqlite3.dll",
        "f_scontainer.dll", "f_fsrc.dll", "f_dso.dll",
        "f_batenc.dll", "f_prophdr.dll", "f_md.dll",
        "f_propfm.dll", "f_csfileinfo.dll", "f_pma.dll",
        "f_psc.dll", "f_pmlist.dll", "f_protry.dll",
        "f_cblogr.dll", "f_cbl.dll", "f_cm.dll",
        "f_CAgent.dll", "f_APAgent.dll", "f_batmgr.exe",
        "f_ioh.dll", "f_shlext.dll", "f_ShellKeeper.dll",
        "f_uwpinject.dll", "f_xnusub.dll", "f_nx.dll",
        "f_mim.dll", "f_xlus2.dll",
        "fcw_crtw2.dll", "fcw_crypto2.dll", "fcw_cryptoex2.dll",
        "fcw_fipscrypto.dll", "fcw_common.dll",
        "fs_commsvr.dll", "fs_commcli.dll",
        "FasooShellMenu.dll", "snf_win.dll",
    ]

    # GetModuleFileNameW 함수 올바르게 설정
    GetModuleFileNameW = ctypes.windll.kernel32.GetModuleFileNameW
    GetModuleFileNameW.argtypes = [ctypes.wintypes.HMODULE, ctypes.wintypes.LPWSTR, ctypes.wintypes.DWORD]
    GetModuleFileNameW.restype = ctypes.wintypes.DWORD

    for dll_name in dll_names:
        try:
            handle = ctypes.windll.LoadLibrary(dll_name)
            log(f"  *** 로드 성공: {dll_name}")
            # DLL 경로 찾기
            buf = ctypes.create_unicode_buffer(512)
            hmod = ctypes.wintypes.HMODULE(handle._handle)
            GetModuleFileNameW(hmod, buf, 512)
            dll_path = buf.value
            if dll_path:
                log(f"      경로: {dll_path}")
                safe_copy(dll_path, os.path.join(output_dir, "loaded_dlls"), "loaded_dll")

            # 내보낸 함수 목록 (PE 파싱)
            try:
                list_exports(dll_path, output_dir)
            except:
                pass

            ctypes.windll.kernel32.FreeLibrary(handle._handle)
        except OSError:
            pass

    # 추가: Fasoo DRM 설치 폴더 전체 복사
    log("\n[3-2] Fasoo DRM 설치 폴더 전체 복사...")
    fasoo_dirs = [
        r"C:\Program Files\Fasoo DRM",
        r"C:\Program Files (x86)\Fasoo DRM",
        r"C:\Program Files\Fasoo",
        r"C:\Program Files (x86)\Fasoo",
    ]
    for fdir in fasoo_dirs:
        if os.path.isdir(fdir):
            log(f"  *** 전체 복사: {fdir}")
            dst = os.path.join(output_dir, "fasoo_full", os.path.basename(fdir))
            try:
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(fdir, dst)
                # 파일 목록 출력
                for root, dirs, files in os.walk(dst):
                    for f in files:
                        full = os.path.join(root, f)
                        size = os.path.getsize(full)
                        rel = os.path.relpath(full, dst)
                        log(f"    {rel} ({size:,} bytes)")
            except Exception as e:
                log(f"  [FAIL] {fdir}: {e}")


def list_exports(dll_path, output_dir):
    """DLL의 export 함수 목록 추출"""
    try:
        import subprocess
        result = subprocess.run(
            ["dumpbin", "/exports", dll_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            export_file = os.path.join(
                output_dir, "exports",
                os.path.basename(dll_path) + ".exports.txt"
            )
            os.makedirs(os.path.dirname(export_file), exist_ok=True)
            with open(export_file, "w") as f:
                f.write(result.stdout)
            log(f"      Exports 저장: {export_file}")
    except FileNotFoundError:
        # dumpbin 없으면 PE 헤더 직접 파싱
        pass


def search_license_files(output_dir):
    """라이선스/키 파일 검색"""
    log("\n" + "=" * 60)
    log("STEP 4: 라이선스/키 파일 검색")
    log("=" * 60)

    # 라이선스 파일로 의심되는 확장자/이름 패턴
    patterns = [
        "*.lic", "*.key", "*.cert", "*.pem",
        "*.dat", "*.cfg", "*.conf", "*.ini",
    ]

    search_dirs = [
        r"C:\ProgramData",
        os.path.expandvars(r"%LOCALAPPDATA%"),
        os.path.expandvars(r"%APPDATA%"),
    ]

    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
        for root, dirs, files in os.walk(search_dir):
            root_lower = root.lower()
            if any(kw in root_lower for kw in ["fasoo", "drmone", "drm"]):
                log(f"  DRM 관련 디렉토리: {root}")
                for f in files:
                    full = os.path.join(root, f)
                    r = safe_copy(full, os.path.join(output_dir, "license"), "license_file")


def create_manifest(output_dir, file_results, reg_results):
    """추출 결과 매니페스트 생성"""
    log("\n" + "=" * 60)
    log("STEP 5: 매니페스트 생성")
    log("=" * 60)

    manifest = {
        "extraction_date": datetime.now().isoformat(),
        "computer_name": os.environ.get("COMPUTERNAME", "unknown"),
        "username": os.environ.get("USERNAME", "unknown"),
        "files_extracted": [r for r in file_results if r],
        "registry_keys_found": list(reg_results.keys()),
        "output_directory": output_dir,
    }

    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False, default=str)

    log(f"  매니페스트 저장: {manifest_path}")
    log(f"\n  총 {len(manifest['files_extracted'])}개 파일 추출 완료")


def main():
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    else:
        # C드라이브에 fasoo_extract 폴더 생성
        output_dir = r"C:\fasoo_extract"

    log("=" * 60)
    log("  Fasoo DRM 클라이언트 파일 추출 도구")
    log("=" * 60)
    log(f"출력 폴더: {output_dir}")
    ensure_dir(output_dir)

    file_results = search_filesystem(output_dir)
    reg_results = search_registry(output_dir)
    search_loaded_dlls(output_dir)
    search_license_files(output_dir)
    create_manifest(output_dir, file_results, reg_results)

    log("\n" + "=" * 60)
    log("  완료! 이 폴더를 USB에 복사하여 오프라인 PC로 가져가세요.")
    log(f"  폴더: {output_dir}")
    log("=" * 60)

    input("\n아무 키나 누르면 종료...")


if __name__ == "__main__":
    main()
