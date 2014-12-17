# _*_ coding: utf-8 _*

__author__ = 'okuno hiroyuki'

import os
import math
import json
import subprocess
import shutil
import tempfile
import shlex
import logging
from Tkinter import *
import re
import sys
import template
import gui


# 文字コード問題のためのおまじないです。　
# 実行時にインタプリタへのoption[ -S ]必須です。
ENC = sys.getfilesystemencoding()

# noinspection PyUnresolvedReferences
sys.setdefaultencoding(ENC)

ENV_TMP = os.environ.copy()
ENV_TMP['PYTHONIOENCODING'] = ENC

logger = logging.getLogger()

if getattr(sys, 'frozen', False):
    # frozen
    BASE_DIR = os.path.dirname(sys.executable)
    # noinspection PyProtectedMember
    if sys.platform == "win32" and sys._MEIPASS:
        # noinspection PyProtectedMember
        BASE_DIR = sys._MEIPASS
    else:
        BASE_DIR = os.path.dirname(sys.executable)

else:
    # unfrozen
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))

TEMP_FOOTAGE_NAME = "TEMP_FOOTAGE_%05d"
RENAME_PATTERN = TEMP_FOOTAGE_NAME + "%s"
RAW_PAD_REG = re.compile('\d+$')
FMT_PAD_REG = re.compile('%\d+d$')
SEP_REG = re.compile('[\._]$')
ASCII_REG = re.compile(r'\A[\x00-\x7f]*\Z')
TEMPLATE = template.get_template()
config_f = open(template.get_config_path(), 'r')
CONFIG = json.load(config_f)
config_f.close()


def _get_sequence_path_dic(folder_path):
    """
    src_pathは_normalize_padding_file_nameで%4d等に正規化された状態ではいります。
    
    :param folder_path:
    :return: { src_path: { "minPad": int, "count": int }, ... }
    """
    dst_file_names_dic = {}
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            normalize_name = _normalize_padding_file_name(file_name)
            if normalize_name is not None:
                base_name = os.path.splitext(file_name)[0]
                temp_path = os.path.join(root, normalize_name)
                if temp_path not in dst_file_names_dic:
                    dst_file_names_dic[temp_path] = {
                        "minPad": int(re.search(RAW_PAD_REG, base_name).group(0)),
                        "count": 0}
                else:
                    temp_pad = int(re.search(RAW_PAD_REG, base_name).group(0))
                    if dst_file_names_dic[temp_path]["minPad"] > temp_pad:
                        dst_file_names_dic[temp_path]["minPad"] = temp_pad
                    dst_file_names_dic[temp_path]["count"] += 1
    return dst_file_names_dic


def _get_unique_path_with_pad(path):
    """
    同名パスが存在したら[_#]でパディングしたパスを返す。
    :param path:
    :return:dst_path
    """
    if os.path.isdir(path):
        dst_path = path
        pad = 2
        while os.path.lexists(dst_path):
            dst_path = path + "_" + str(pad)
            pad += 1
        return dst_path
    else:
        (dir_path, base_name) = os.path.split(path)
        (name, ext) = os.path.splitext(base_name)
        dst_path = os.path.join(dir_path, name + ext)
        pad = 2
        while os.path.lexists(dst_path):
            dst_path = os.path.join(dir_path, name + "_" + str(pad) + ext)
            pad += 1
        return dst_path


def _get_movie_stats(src_path):
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        # noinspection PyUnresolvedReferences
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # si.wShowWindow = subprocess.SW_HIDE # default
        p = subprocess.Popen([CONFIG['ffprobePath'], '-show_streams', '-print_format', 'json', src_path],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, startupinfo=si, env=ENV_TMP)
    else:
        p = subprocess.Popen([CONFIG['ffprobePath'], '-show_streams', '-print_format', 'json', src_path],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=ENV_TMP)
    out, err = p.communicate()
    # logger.debug("\n\tffprobe error:\n" + err)
    logger.debug("\n\tffprobe log:\n" + out)
    width = re.search('"width": (\d+)', out).group(1)
    height = re.search('"height": (\d+)', out).group(1)
    frame_rate = re.search('"r_frame_rate": "(\d+\.\d+|\d+)/', out).group(1)
    pix_fmt = re.search('"pix_fmt": "(.+)"', out).group(1)
    return dict({"width": width, "height": height, "frame_rate": frame_rate, "pix_fmt": pix_fmt})


def _make_dst_file_path(src_path):
    """
    paddingを消去して拡張子をmp4にしたパスを返します。
    :param src_path:
    :return dst_file_path:
    """
    (src_dir_path, src_file_name) = os.path.split(src_path)
    (base_name, ext) = os.path.splitext(src_file_name)

    # paddingを消去
    temp_name = re.sub(FMT_PAD_REG, "", base_name)
    new_name = re.sub(SEP_REG, "", temp_name)
    temp_text = "/"

    if new_name != base_name:
        temp_text = "/../"

    # 拡張子を付けて返す
    return os.path.normpath(src_dir_path + temp_text + new_name + str(CONFIG["ext"]))


def _normalize_padding_file_name(file_name):
    """
    ex. foobar.####.ext >> foobar.%4d.ext
        foobar_#####.ext >> foobar_%5d.ext
        foobar.ext >> None

    :param file_name:
    :return:
    """
    (base_name, ext) = os.path.splitext(file_name)
    padding = RAW_PAD_REG.search(base_name)
    if padding is not None:
        digit = padding.span()[1] - padding.span()[0]
        return re.sub(RAW_PAD_REG, "%" + str(digit) + "d", base_name) + ext
    else:
        return None


def _create_temp_src_footage(normalized_src_path):
    """
    TempSrcFootageを作成
    戻り値に最終ファイルのパスを返します。
    :param normalized_src_path:
    :return: temp_last_file_path
    """

    # tempFolder作ってます。
    temp_dir_path = tempfile.mkdtemp()

    (folder_path, file_name) = os.path.split(normalized_src_path)
    (base_name, ext) = os.path.splitext(file_name)
    no_pad_name = re.sub(FMT_PAD_REG, "", base_name)
    src_files_list = os.listdir(folder_path)
    index = 0

    def is_same_sequence_group(file_path):
        return re.sub(RAW_PAD_REG, "", os.path.splitext(file_path)[0]) in os.path.join(folder_path, no_pad_name)

    for srcfile_name in sorted(filter(is_same_sequence_group, src_files_list)):
        index += 1
        (name, ext) = os.path.splitext(srcfile_name)
        shutil.copy2(os.path.join(folder_path, srcfile_name),
                     os.path.join(temp_dir_path, RENAME_PATTERN % (index, ext)))

    # fpsより少ない枚数の時(結果が1秒未満)は水増しします。
    while index < float(CONFIG['fps']):
        index += 1
        (name, ext) = os.path.splitext(srcfile_name)
        shutil.copy2(os.path.join(folder_path, srcfile_name),
                     os.path.join(temp_dir_path, RENAME_PATTERN % (index, ext)))
    return os.path.join(temp_dir_path, RENAME_PATTERN % (index, ext))


def _exec_ffmpeg(src_path, dst_path, is_seq=False, start_number=None):
    dst_path_for_print = dst_path
    stats = _get_movie_stats(src_path)
    batch_string = CONFIG['ffmpegPath']
    src_path = "\"" + src_path.replace('\\', '/') + "\""
    dst_path = "\"" + dst_path.replace('\\', '/') + "\""

    # input setting
    if is_seq:
        if start_number:
            batch_string += " -start_number " + str(start_number)
        frame_rate = CONFIG['fps']
        batch_string += " -f image2 "
        batch_string += " -r " + str(frame_rate)
    else:
        if CONFIG['isForceFrameRate']:
            frame_rate = CONFIG['fps']
        else:
            frame_rate = stats["frame_rate"]
    width = str(int(math.ceil(int(stats["width"]) * CONFIG['zoom'] * 0.01 * 0.5) * 2))
    height = str(int(math.ceil(int(stats["height"]) * CONFIG['zoom'] * 0.01 * 0.5) * 2))
    if CONFIG['isForceFrameRate']:
        batch_string += " -r " + str(frame_rate)
    if is_seq and stats['pix_fmt']:
        batch_string += " -pix_fmt " + stats['pix_fmt']
    batch_string += " -i " + src_path

    # video setting
    batch_string += TEMPLATE['video'][CONFIG['video']]

    # audio setting
    batch_string += TEMPLATE['audio'][CONFIG['audio']]

    # output setting
    batch_string += " -s " + width + "x" + height
    batch_string += " -r " + str(frame_rate)
    batch_string += " -y " + dst_path
    logger.debug("\tcall ffmpeg:\n\t\t" + batch_string + "\n")

    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        # noinspection PyUnresolvedReferences
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # si.wShowWindow = subprocess.SW_HIDE # default
        p = subprocess.Popen(shlex.split(batch_string), stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, startupinfo=si)
    else:
        p = subprocess.Popen(shlex.split(batch_string), stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=False)
    logger.debug("\n\tffmpeg log:")
    for line in iter(p.stderr.readline, b''):
        logger.debug("\t" + line)

    logger.info("\n\tfinish: \n\t\t" + dst_path_for_print)


def _walk_folder(folder_path):
    for (normalized_src_path, srcOpt) in _get_sequence_path_dic(folder_path).items():
        dst_dir_path = os.path.normpath(folder_path + "/../")
        temp_dst_path = _make_dst_file_path(normalized_src_path)
        dst_path = os.path.join(dst_dir_path, os.path.basename(temp_dst_path))
        logger.info("\nfound sequence is:\t" + normalized_src_path)

        # minPad＆連番が1秒未満＆パスがasciiかチェック。
        if srcOpt["minPad"] > 4 or srcOpt["count"] < float(CONFIG['fps']) or not _is_ascii(
                normalized_src_path):

            # TempSrcFootageを作成
            last_file_path = _create_temp_src_footage(normalized_src_path)
            logger.warning(u"\n\ttempFileを作成しました:\n\t\t" + os.path.dirname(last_file_path))
            _exec_ffmpeg(_normalize_padding_file_name(last_file_path), _get_unique_path_with_pad(dst_path), is_seq=True,
                         start_number=0)

            # TempSrcFootageを削除
            logger.warning(u"\n\ttempFileを削除しました:\n\t\t" + os.path.dirname(last_file_path))
            shutil.rmtree(os.path.dirname(last_file_path))
        else:
            _exec_ffmpeg(normalized_src_path, _get_unique_path_with_pad(dst_path), is_seq=True,
                         start_number=srcOpt["minPad"])


def _is_ascii(text):
    return ASCII_REG.match(text)


def _ffmpeg_exists(path):
    return os.path.isfile(path) and os.path.splitext(os.path.basename(path))[0] == "ffmpeg"


def _ffprobe_exists(path):
    return os.path.isfile(path) and os.path.splitext(os.path.basename(path))[0] == "ffprobe"


def _is_image(path):
    return os.path.splitext(os.path.basename(path))[1] in TEMPLATE['imageWhiteList']


def _is_video(path):
    return os.path.splitext(os.path.basename(path))[1] in TEMPLATE['videoWhiteList']


def main():
    root = Tk()

    # windowsならicon表示
    if sys.platform == "win32":
        root.iconbitmap(
            default=os.path.normcase(os.path.join(BASE_DIR + '/libs/app.ico')))

    # 通常実行かconfigか分岐
    if sys.argv[1:] and _ffmpeg_exists(CONFIG['ffmpegPath']) and _ffprobe_exists(CONFIG['ffprobePath']):

        # logger open
        logger.addHandler(gui.LoggerWindow(root).handler)
        logger.setLevel(CONFIG['logLevel'])
        root.update()

        target_arg = sys.argv[1:]
        logger.info("Hello.")
        logger.debug("given args:\t" + str(target_arg))
        for input_folder_path in target_arg:
            input_folder_path = unicode(input_folder_path, ENC)
            if os.path.isdir(input_folder_path):
                _walk_folder(input_folder_path)
            else:
                src_path = input_folder_path
                logger.info("\nfound file is:\t" + src_path)
                if _is_video(src_path) or _is_image(src_path):
                    dst_path = _get_unique_path_with_pad(_make_dst_file_path(src_path))
                    _exec_ffmpeg(src_path, dst_path)
                else:
                    logger.warning("this file is not supported!:\t" + src_path)

        # 終了メッセージ
        logger.error("\n\n( ´ー｀)y-~~\n\nオワタヨン. ")
        root.mainloop()
        return
    else:
        gui.ConfigWindow(root)
        root.mainloop()
        return


if __name__ == '__main__':
    main()