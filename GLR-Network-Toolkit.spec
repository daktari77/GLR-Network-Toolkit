# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('docs',   'docs'),
    ],
    hiddenimports=[
        # engines
        'src.engines.scanner_engine',
        'src.engines.port_scanner_engine',
        'src.engines.traceroute_engine',
        'src.engines.dns_engine',
        'src.engines.http_inspector_engine',
        'src.engines.ssl_engine',
        'src.engines.whois_engine',
        # panels
        'src.gui.panels.monitor_panel',
        'src.gui.panels.scanner_panel',
        'src.gui.panels.port_scanner_panel',
        'src.gui.panels.troubleshoot_panel',
        # widgets
        'src.gui.widgets.scan_result_table',
        'src.gui.widgets.port_result_table',
        # utils
        'src.utils.privileges',
        'src.utils.ip_range',
        # stdlib used at runtime
        'ipaddress',
        'ssl',
        'socket',
        'subprocess',
        'threading',
        'concurrent.futures',
        'queue',
        'ctypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['scapy', 'dns', 'whois'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GLR-Network-Toolkit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='GLR-Network-Toolkit',
)
