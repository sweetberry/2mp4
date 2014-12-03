# _*_ coding: utf-8 _*

import os
import sys
import json

if sys.platform == "win32":
        CONFIG_FILE_PATH = os.path.normpath(os.path.join(os.path.expandvars("${TMP}"), './2mp4_config.json'))
else:
        CONFIG_FILE_PATH = os.path.normpath(os.path.join(os.path.expandvars("${TMPDIR}"), './2mp4_config.json'))


def get_template():
    return {
        "video": {
            "h264_STD": " -c:v libx264 -preset slow -g 1 -crf 11 -bf 0 -pix_fmt yuv420p ",
            "h264_LOW": " -c:v libx264 -preset slow -g 1 -crf 23 -bf 0 -pix_fmt yuv420p ",
            "rawvideo": " -c:v rawvideo  -pix_fmt rgba "},
        "audio": {
            "none": " -an ",
            "acc": " -c:a aac -strict experimental -ab 128k -cutoff 17000 -ac 2 ",
            "copy": " -acodec copy "
        },
        "ext": [
            ".mp4",
            ".mov",
            ".m4v",
            ".avi",
            ".flv"
        ],
        "videoWhiteList": [
            ".avi",
            ".f4v",
            ".flv",
            ".mov",
            ".m4v",
            ".mp4",
            ".ogg",
            ".rm",
            ".wmv",
            ".webm"
        ],
        "imageWhiteList": [
            ".bmp",
            ".dpx",
            ".exr",
            ".gif",
            ".iff",
            ".j2k",
            ".jpg",
            ".jpeg",
            ".png",
            ".rgb",
            ".sgi",
            ".tga",
            ".tif",
            ".tiff"
        ]
    }


def get_config_path():
    if os.path.isfile(CONFIG_FILE_PATH):
        return CONFIG_FILE_PATH
    else:
        __init_config()
        return CONFIG_FILE_PATH


def __init_config():
    INIT_CONFIG = {"isForceFrameRate": 0,
               "logLevel": "DEBUG",
               "zoom": 100.0,
               "fps": "30",
               "ext": get_template()["ext"][0],
               "video": get_template()["video"].keys()[0],
               "audio": get_template()["audio"].keys()[0],
               "ffmpegPath": "ffmpeg",
               "ffprobePath": "ffprobe"}
    f = open(CONFIG_FILE_PATH, 'w')
    json.dump(INIT_CONFIG, f)
    f.close()
    return