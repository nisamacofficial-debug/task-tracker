# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Administrator\\Desktop\\TT\\PythonProject1\\tasktracker\\manage.py', '.'), ('C:\\Users\\Administrator\\Desktop\\TT\\PythonProject1\\tasktracker\\tasktracker', 'tasktracker'), ('C:\\Users\\Administrator\\Desktop\\TT\\PythonProject1\\tasktracker\\login', 'login'), ('C:\\Users\\Administrator\\Desktop\\TT\\PythonProject1\\tasktracker\\db.sqlite3', '.')],
    hiddenimports=['django', 'pywebview'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='tracker_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tracker_app',
)
