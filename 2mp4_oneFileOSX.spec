# -*- mode: python -*-
a = Analysis(['2mp4.py'],
             pathex=['/Users/pixel/dev/2mp4'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
extra_tree = Tree('./libs', prefix='libs', excludes=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          [('s', None, 'OPTION')],
          a.binaries + extra_tree,
          a.zipfiles,
          a.datas,
          name='2mp4',
          debug=False,
          strip=None,
          upx=True,
          console=False )
