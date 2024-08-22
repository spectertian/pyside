from PyInstaller.utils.hooks import collect_data_files, collect_submodules

qt_plugins = [
    'platforms',
    'platformthemes',
    'styles',
    'imageformats',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icons/*', 'icons/'),
        ('screenshots/*', 'screenshots/'),
    ],
    hiddenimports=collect_submodules('PySide6'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='截图工具',
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
    icon='icons/link.png'
)

# Add Qt plugins
for plugin in qt_plugins:
    plugin_data = collect_data_files('PySide6', include_py_files=True, subdir=plugin)
    exe.add_data(plugin_data)