# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_dynamic_libs

# Create error handling wrapper
with open('error_wrapper.py', 'w') as f:
    f.write('''
import sys
import traceback

try:
    import main
except Exception as e:
    print("Error occurred while running the application:")
    print(traceback.format_exc())
    input("Press Enter to exit...")
    sys.exit(1)
''')

block_cipher = None

# Collect CadQuery and OCP dependencies
binaries = []
binaries.extend(collect_dynamic_libs('cadquery'))
binaries.extend(collect_dynamic_libs('OCP'))

a = Analysis(
    ['error_wrapper.py'],  
    pathex=[],
    binaries=binaries,
    datas=[],
    hiddenimports=[
        'cadquery',
        'numpy',
        'tkinter',
        'tkinter.ttk',
        'PIL',
        'OCP',
        'OCP.TopoDS',
        'OCP.gp',
        'OCP.BRepBuilderAPI',
        'OCP.BRepAlgoAPI',
        'OCP.BRepPrimAPI'
    ],
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
    name='ConnectorGenerator',
    debug=True,  
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
