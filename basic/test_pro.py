import os
import subprocess
import hwp5

g_file_name = r"sample"         # 파일이름 (확장자 제외)

g_target_path = r"D:\\python\\python\\basic\\"          # 폴더 경로
g_hwpx_path = g_target_path + g_file_name + r".hwpx"        # hwpx 파일 경로
g_zip_path = g_target_path + g_file_name + r".zip"          # zip 파일 경로
g_bandizip_path = r"C:\\Program Files\\Bandizip\\Bandizip.exe"          # 반디집 경로
g_bandizip_folder = g_target_path + r"zip_folder"                   # 반디집 압축해제 경로



def hwpx_to_zip(hwpx_file, zip_path, bandizip_path, result_folder):
    # 반디집을 통해 compound 파일의 압축을 해제하는 명령어
    command = f'"{bandizip_path}" x -y -o:"{result_folder}" "{zip_path}"'

    # hwp, hwpx의 확장자를 변환하는 운영체제 명령어 (zip파일로 변환)
    try:
        base = os.path.splitext(hwpx_file)[0]
        os.rename(hwpx_file, base + ".zip")
    except:
        print(f"zip 파일로 변환 중 오류 발생")

    # CLI명령어로 반디집으로 압축해제
    try:
        subprocess.run(command, shell=True, check=True)
        print("ZIP 파일이 성공적으로 압축 해제되었습니다.")
        os.remove(zip_path)
        print("압축해제 후 파일 삭제했습니다")
    except subprocess.CalledProcessError as e:
        print(f"오류가 발생했습니다. 반환 코드: {e.returncode}")
    
# 압축 해제 후 파일과 폴더명을 리스트로 반환
def print_folder(folder):
    lst = []
    try:
        lst = os.listdir(folder)
    except:
        print("폴더가 없습니다")
    return lst


# hwp, hwpx의 확장자를 변환하는 cmd 함수 (텍스트 파일이나 hwp 파일로 변환가능)
def hwpx_to_file(hwpx_file, file_path):
    # pip install pyhwp
    command = f'hwp5txt --output "{file_path}" "{hwpx_file}"'
    try:
        subprocess.run(command, shell=True, check=True)
        print("HWP 파일이 성공적으로 변환되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"오류가 발생했습니다. 반환 코드: {e.returncode}")


hwpx_to_zip(g_hwpx_path, g_zip_path, g_bandizip_path, g_bandizip_folder)
contents = print_folder(g_bandizip_folder)
print(contents)