# -*- mode: python -*-

block_cipher = None


a = Analysis(['backtester.py'],
             pathex=['C:\\Users\\14387\\PycharmProjects\\Backtester'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['src'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='backtester',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )
