# -*- mode: python -*-

block_cipher = None

added_files = [

                ('db/bt.db', 'db'),
                ('icon', 'icon'),
                ('ui/*.ui', 'ui'),
                ('images/*', 'images'),
                ('backtesters', 'backtesters')
            ]

add_binaries = [

                ("dlls/libeay32.dll", "."),
                ("dlls/msvcr120.dll", ".")
]

a = Analysis(['backtester.py'],
             pathex=['C:\\Users\\14387\\PycharmProjects\\backtesters'],
             binaries=add_binaries,
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=["PyQt5"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='backtester-debug',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True)

coll = COLLECT(exe,

               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='backtester-debug')
