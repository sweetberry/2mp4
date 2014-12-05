# -*- mode: python -*-
a = Analysis(['2mp4.py'],
             pathex=['C:\\Users\\h_okuno\\PycharmProjects\\2mp4'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
extra_tree = Tree('./libs', prefix='libs', excludes=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='2mp4.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          icon='libs\\app.ico')
coll = COLLECT(exe,
               a.binaries + extra_tree,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='2mp4')
