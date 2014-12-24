2mp4
====

日々の動画ファイル変換を支援するスクリプト。

## Description
ffmpeg用のラッパーです。

## VS. 

## Requirement
- ffmpeg & ffprobe のバイナリが必要です。  
[こちらで入手](https://www.ffmpeg.org/download.html)

## Usage
- 実行ファイルをダブルクリックで設定画面が開きます。
- videoファイルや連番入りフォルダをdropで実行します。  
- windowsの コンテキストメニュー > 送る とかに入れとくと、すごく良いです。

## Install

- for Windows
    * pyinstallerで実行ファイル化してください  
```pyinstaller 2mp4_oneFileWindows.spec ```

- for osX
    * pyinstallerで実行ファイル化してください  
```pyinstaller 2mp4.py --onefile --windowed ```
    * dist/2mp4.app/Contents/Resources/icon-windowed.icns　を置換
    * Contents/Info.plist の改行コードをCRに
    
    * もしくはautomatorで実行してください。  
![代替テキスト](libs/automatorSetting.png)

- 初回起動時にffmpeg,ffprobeのパスを通す必要があります。  
設定画面で指定してください。

## Contribution

## Licence
MIT

## Author
[sweetberry](https://github.com/sweetberry)