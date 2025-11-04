# -*- mode: python ; coding: utf-8 -*-
import os
import glob
from PyInstaller.utils.hooks import collect_submodules  # (필요시)

block_cipher = None

# custom_cursors 폴더 내 모든 파일을 datas로 수집
datas = [
    (path, 'custom_cursors')
    for path in glob.glob(os.path.join('custom_cursors', '*'))
]

a = Analysis(
    ['mabinogiCursor.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='mabinogiCursor',
    debug=False,
    strip=False,
    upx=True,
    console=False,                 # 콘솔 창 없이 실행
    disable_windowed_traceback=False,
    icon=os.path.join('custom_cursors', 'icon.ico'),
)
