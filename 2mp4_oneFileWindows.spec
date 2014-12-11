# -*- mode: python -*-
# pyinstaller 2mp4_oneFileWindows.spec
a = Analysis(['2mp4.py'],
             pathex=['PATH\\TO\\2mp4'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
extra_tree = Tree('./libs', prefix='libs', excludes=None)
print extra_tree
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          [('-S', None, 'OPTION')],
          a.binaries + extra_tree,
          a.zipfiles,
          a.datas,
          name='2mp4.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          icon='libs\\app.ico')
