# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['opencv c: && cd c:\\Users\\Administrator\\Desktop\\py && cmd \\C C:\\Users\\Administrator\\anaconda3\\python.exe', 'c:\\Users\\Administrator\\.vscode\\extensions\\ms-python.python-2022.8.0\\pythonFiles\\lib\\python\\debugpy\\launcher', '49831', 'c:\\Users\\Administrator\\Desktop\\py\\cv1.py', '3.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='python',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
