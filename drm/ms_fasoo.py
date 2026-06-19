# python -m pip install pywin32
# MS오피스 설치된 컴퓨터에서 가능

import win32com.client as win32
import win32clipboard
import base64
import os
import time
import zipfile
from xml.etree import ElementTree as ET


PKG_NS_URI = "http://schemas.microsoft.com/office/2006/xmlPackage"
CONTENT_TYPES_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
DEFAULT_CONTENT_TYPES = {
    "bin": "application/vnd.openxmlformats-officedocument.obfuscatedFont",
    "bmp": "image/bmp",
    "emf": "image/x-emf",
    "gif": "image/gif",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "png": "image/png",
    "rels": "application/vnd.openxmlformats-package.relationships+xml",
    "tif": "image/tiff",
    "tiff": "image/tiff",
    "wdp": "image/vnd.ms-photo",
    "wmf": "image/x-wmf",
    "xml": "application/xml",
}


def xml_local_name(tag):
    return tag.rsplit("}", 1)[-1]


def pkg_attr(element, name):
    return element.attrib.get(f"{{{PKG_NS_URI}}}{name}") or element.attrib.get(name)


def first_pkg_child(element, name):
    for child in element:
        if xml_local_name(child.tag) == name:
            return child
    return None


def save_flat_opc_as_docx(flat_opc_xml, save_path):
    root = ET.fromstring(flat_opc_xml)
    if os.path.exists(save_path):
        os.remove(save_path)

    xml_parts = extract_flat_opc_xml_parts(flat_opc_xml)
    overrides = {}
    defaults = {}
    with zipfile.ZipFile(save_path, "w", zipfile.ZIP_DEFLATED) as docx:
        for part in root:
            if xml_local_name(part.tag) != "part":
                continue

            name = pkg_attr(part, "name")
            if not name:
                continue
            part_name = name if name.startswith("/") else "/" + name
            name = name.lstrip("/")
            content_type = pkg_attr(part, "contentType")
            if content_type:
                ext = os.path.splitext(name)[1].lower().lstrip(".")
                if ext in DEFAULT_CONTENT_TYPES and DEFAULT_CONTENT_TYPES[ext] == content_type:
                    defaults[ext] = content_type
                else:
                    overrides[part_name] = content_type

            xml_data = first_pkg_child(part, "xmlData")
            binary_data = first_pkg_child(part, "binaryData")

            if xml_data is not None:
                payload = xml_parts.get(part_name, "").encode("utf-8")
            elif binary_data is not None and binary_data.text:
                encoded = "".join(binary_data.itertext()).strip()
                payload = base64.b64decode(encoded)
            else:
                payload = b""

            docx.writestr(name, payload)

        if "[Content_Types].xml" not in docx.namelist():
            types = ET.Element(f"{{{CONTENT_TYPES_NS}}}Types")
            for ext, content_type in sorted({**DEFAULT_CONTENT_TYPES, **defaults}.items()):
                default = ET.SubElement(types, f"{{{CONTENT_TYPES_NS}}}Default")
                default.set("Extension", ext)
                default.set("ContentType", content_type)
            for part_name, content_type in sorted(overrides.items()):
                override = ET.SubElement(types, f"{{{CONTENT_TYPES_NS}}}Override")
                override.set("PartName", part_name)
                override.set("ContentType", content_type)
            payload = ET.tostring(types, encoding="utf-8", xml_declaration=True)
            docx.writestr("[Content_Types].xml", payload)

        required_parts = {"[Content_Types].xml", "_rels/.rels", "word/document.xml"}
        missing = required_parts.difference(docx.namelist())
        if missing:
            raise RuntimeError(f"DOCX 필수 파트가 없습니다: {', '.join(sorted(missing))}")


def extract_flat_opc_xml_parts(flat_opc_xml):
    parts = {}
    pos = 0
    while True:
        part_start = flat_opc_xml.find("<pkg:part", pos)
        if part_start == -1:
            break
        header_end = flat_opc_xml.find(">", part_start)
        part_end = flat_opc_xml.find("</pkg:part>", header_end)
        if header_end == -1 or part_end == -1:
            break

        header = flat_opc_xml[part_start:header_end + 1]
        name = None
        for attr in ('pkg:name="', 'name="'):
            attr_start = header.find(attr)
            if attr_start != -1:
                attr_start += len(attr)
                attr_end = header.find('"', attr_start)
                name = header[attr_start:attr_end]
                break

        xml_start_tag = "<pkg:xmlData>"
        xml_end_tag = "</pkg:xmlData>"
        xml_start = flat_opc_xml.find(xml_start_tag, header_end, part_end)
        if name and xml_start != -1:
            xml_start += len(xml_start_tag)
            xml_end = flat_opc_xml.find(xml_end_tag, xml_start, part_end)
            if xml_end != -1:
                parts[name if name.startswith("/") else "/" + name] = flat_opc_xml[xml_start:xml_end]

        pos = part_end + len("</pkg:part>")
    return parts


def get_document_word_open_xml(doc):
    try:
        return doc.WordOpenXML
    except Exception:
        return doc.Range().WordOpenXML


def save_word_range_as_rtf(doc, save_path):
    if os.path.exists(save_path):
        os.remove(save_path)

    doc.Range().Copy()
    time.sleep(0.5)

    rtf_format = win32clipboard.RegisterClipboardFormat("Rich Text Format")
    win32clipboard.OpenClipboard()
    try:
        if not win32clipboard.IsClipboardFormatAvailable(rtf_format):
            raise RuntimeError("클립보드에서 RTF 데이터를 찾지 못했습니다.")
        data = win32clipboard.GetClipboardData(rtf_format)
        if isinstance(data, str):
            data = data.encode("ansi", errors="replace")
        with open(save_path, "wb") as f:
            f.write(data)
    finally:
        win32clipboard.CloseClipboard()

def read_drm_excel(file_path):
    excel = None
    wb = None
    try:
        # 엑셀 어플리케이션 실행 (백그라운드)
        excel = win32.gencache.EnsureDispatch("Excel.Application")
        excel.Visible = True        # 창 떠야함
        excel.DisplayAlerts = False # 저장할까요? 같은 팝업 무시

        abs_path = os.path.abspath(file_path)
        print(f"엑셀 여는 중: {abs_path}")
        
        # 여기서 DRM 해제됨 (PC에 권한이 있다면)
        wb = excel.Workbooks.Open(abs_path)
        ws = wb.ActiveSheet

        # 예시: A1 셀 값 읽기
        val = ws.Range("A1").Value
        print(f"A1 셀 내용: {val}")

        # DRM 우회 저장: .iso 확장자로 저장 → Fasoo 무시
        # 다른 PC에서 .iso → .xlsx 로 이름 변경 후 열기
        save_path = os.path.splitext(abs_path)[0] + ".iso"

        if os.path.exists(save_path):
            os.remove(save_path)

        print("SaveCopyAs로 복사본 저장 중...")
        wb.SaveCopyAs(save_path)
        print(f"ISO 확장자로 저장 완료: {save_path}")

    except Exception as e:
        print(f"에러 발생: {e}")
    finally:
        if wb:
            wb.Close(False)
        if excel:
            excel.Quit()


def read_drm_word(file_path):
    word = None
    doc = None
    try:
        word = win32.gencache.EnsureDispatch("Word.Application")
        word.Visible = True
        
        abs_path = os.path.abspath(file_path)
        
        # 문서 열기 (DRM 해제)
        doc = word.Documents.Open(abs_path)
        
        # 전체 텍스트 추출
        full_text = doc.Content.Text
        print(f"문서 내용(일부): {full_text[:100]}...")

        # DRM 우회 저장: .iso 확장자로 저장 → Fasoo 무시
        # 다른 PC에서 .iso → .docx 로 이름 변경 후 열기
        save_path = os.path.splitext(abs_path)[0] + ".iso"

        if os.path.exists(save_path):
            os.remove(save_path)

        ext = os.path.splitext(abs_path)[1].lower()
        if ext == ".docx":
            print("WordOpenXML로 DOCX 패키지 생성 중...")
            save_flat_opc_as_docx(get_document_word_open_xml(doc), save_path)
        else:
            print("RTF 기반 DOC 파일 생성 중...")
            save_word_range_as_rtf(doc, save_path)

        print(f"ISO 확장자로 저장 완료: {save_path}")

        doc.Close(False)
        doc = None

    except Exception as e:
        print(f"에러: {e}")
    finally:
        if doc:
            doc.Close(False)
        if word:
            word.Quit()


def read_drm_txt(file_path):
    word = None
    doc = None
    try:
        word = win32.gencache.EnsureDispatch("Word.Application")
        word.Visible = True

        abs_path = os.path.abspath(file_path)
        doc = word.Documents.Open(abs_path)

        save_path = os.path.splitext(abs_path)[0] + ".iso"
        if os.path.exists(save_path):
            os.remove(save_path)

        with open(save_path, "w", encoding="utf-8-sig") as f:
            f.write(doc.Content.Text)

        print(f"ISO 확장자로 저장 완료: {save_path}")
        doc.Close(False)
        doc = None
    except Exception as e:
        print(f"에러: {e}")
    finally:
        if doc:
            doc.Close(False)
        if word:
            word.Quit()


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

        # DRM 우회 저장: .iso 확장자로 저장 → Fasoo 무시
        # 다른 PC에서 .iso → .pptx 로 이름 변경 후 열기
        save_path = os.path.splitext(abs_path)[0] + ".iso"
        presentation.SaveAs(save_path, 24)  # 24 = ppSaveAsOpenXMLPresentation (.pptx 포맷)
        print(f"ISO 확장자로 저장 완료: {save_path}")

        presentation.Close()

    except Exception as e:
        print(f"에러 발생: {e}")
    finally:
        if ppt_app:
            ppt_app.Quit()


def main():
    file_path = input("파일 경로를 입력하세요: ").strip().strip('"').strip("'")
    if not file_path:
        print("파일 경로가 입력되지 않았습니다.")
        return

    abs_path = os.path.abspath(file_path)
    if not os.path.isfile(abs_path):
        fallback_path = os.path.abspath(os.path.basename(file_path))
        if os.path.isfile(fallback_path):
            print(f"입력한 경로에는 파일이 없어 현재 폴더의 같은 파일명을 사용합니다: {fallback_path}")
            abs_path = fallback_path
        else:
            print(f"파일이 존재하지 않습니다: {abs_path}")
            print("현재 폴더에 같은 이름의 파일도 없습니다.")
            return

    ext = os.path.splitext(abs_path)[1].lower()

    if ext in (".xls", ".xlsx"):
        read_drm_excel(abs_path)
    elif ext in (".doc", ".docx"):
        read_drm_word(abs_path)
    elif ext == ".txt":
        read_drm_txt(abs_path)
    elif ext in (".ppt", ".pptx"):
        read_drm_ppt(abs_path)
    else:
        print(f"지원하지 않는 확장자입니다: {ext}")


if __name__ == "__main__":
    main()
