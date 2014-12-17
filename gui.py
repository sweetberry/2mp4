# _*_ coding: utf-8 _*

__author__ = 'okuno hiroyuki'

from Tkinter import *
import Tkinter
import tkFileDialog
import tkMessageBox
import json
import os
import logging
import template
# noinspection PyUnresolvedReferences
import re

if getattr(sys, 'frozen', False):
    # frozen
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # unfrozen
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))

TEMPLATE = template.get_template()

CONFIG_FILE_PATH = template.get_config_path()
config_f = open(CONFIG_FILE_PATH, "r")
CONFIG = json.load(config_f)
config_f.close()


class ConfigWindow(Tkinter.Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        master.resizable(width=FALSE, height=FALSE)
        self.master.title('configure')
        self.video_val = StringVar()
        self.audio_val = StringVar()
        self.zoom_val = DoubleVar()
        self.fps_val = StringVar()
        self.force_val = BooleanVar()
        self.ext_val = StringVar()
        self.ffmpeg_val = StringVar()
        self.ffprobe_val = StringVar()

        self.__make_video_rows()
        self.__make_audio_rows()
        self.__make_zoom_rows()
        self.__make_fps_rows()
        self.__make_ext_rows()
        self.__make_lib_setting_rows()
        self.pack()
        return

    def __make_video_rows(self):
        Label(self, text='video : ').grid(row=0, column=0, sticky=E)
        self.video_val.set(CONFIG['video'])
        video_mb = Menubutton(self, text=self.video_val.get(), textvariable=self.video_val, relief=RAISED, width=15)
        video_mb.grid(row=0, column=1, columnspan=2, sticky=W)
        video_mb.menu = Menu(video_mb, tearoff=0)
        video_mb["menu"] = video_mb.menu
        for template_name in TEMPLATE['video'].keys():
            video_mb.menu.add_radiobutton(label=template_name, variable=self.video_val, value=template_name,
                                          command=self.__callback)
        return

    def __make_audio_rows(self):
        Label(self, text='audio : ').grid(row=1, column=0, sticky=E)
        self.audio_val.set(CONFIG['audio'])
        audio_mb = Menubutton(self, text=self.audio_val.get(), textvariable=self.audio_val, relief=RAISED, width=15)
        audio_mb.grid(row=1, column=1, columnspan=2, sticky=W)
        audio_mb.menu = Menu(audio_mb, tearoff=0)
        audio_mb["menu"] = audio_mb.menu
        for template_name in TEMPLATE['audio'].keys():
            audio_mb.menu.add_radiobutton(label=template_name, variable=self.audio_val, value=template_name,
                                          command=self.__callback)
        return

    def __make_zoom_rows(self):
        Label(self, text='zoom : ').grid(row=2, column=0, sticky=E)
        Label(self, text='%').grid(row=2, column=2, sticky=W)

        # noinspection PyUnusedLocal
        def __zoom_callback(event=None):
            try:
                temp_num = float(zoom_en.get())
            except ValueError:
                temp_num = None
            if temp_num:
                self.__set_config()
            else:
                # 消し方かっこ悪い...
                zoom_en.delete(0, 9999)
                self.zoom_val.set(CONFIG['zoom'])
            return

        self.zoom_val.set(CONFIG['zoom'])
        zoom_en = Entry(self, textvariable=self.zoom_val, width=6)
        zoom_en.grid(row=2, column=1, columnspan=2, sticky=W)
        zoom_en.bind('<Return>', __zoom_callback)
        return

    def __make_fps_rows(self):
        Label(self, text='fps : ').grid(row=3, column=0, sticky=E)

        # noinspection PyUnusedLocal
        def __fps_callback(event=None):
            try:
                temp_num = float(fps_en.get())
            except ValueError:
                temp_num = None
            if temp_num:
                self.__set_config()
            else:
                # 消し方かっこ悪い...
                fps_en.delete(0, 9999)
                self.fps_val.set(CONFIG['fps'])
            return

        self.fps_val.set(CONFIG['fps'])
        fps_en = Entry(self, textvariable=self.fps_val, width=6)
        fps_en.grid(row=3, column=1, sticky=W)
        fps_en.bind('<Return>', __fps_callback)

        # forceFPS
        force_cb = Checkbutton(self, text="Is applied\nto Video", variable=self.force_val, command=self.__callback)
        self.force_val.set(CONFIG['isForceFrameRate'])
        force_cb.grid(row=3, column=2, sticky=W)
        return

    def __make_ext_rows(self):
        Label(self, text='ext : ').grid(row=4, column=0, sticky=E)
        self.ext_val.set(CONFIG['ext'])
        ext_mb = Menubutton(self, text=self.ext_val.get(), textvariable=self.ext_val, relief=RAISED, width=15)
        ext_mb.grid(row=4, column=1, columnspan=2, sticky=W)
        ext_mb.menu = Menu(ext_mb, tearoff=0)
        ext_mb["menu"] = ext_mb.menu
        for ext_name in TEMPLATE['ext']:
            ext_mb.menu.add_radiobutton(label=ext_name, variable=self.ext_val, value=ext_name,
                                        command=self.__callback)
        return

    def __make_lib_setting_rows(self):
        labelframe = LabelFrame(self, text="Library Setting")
        labelframe.grid(row=5, column=0, columnspan=3, sticky=S, ipadx=5)

        # FFMPEG
        Label(labelframe, text='ffmpeg : ').grid(row=5, column=0, sticky=E)

        def __ffmpeg_exists(path):
            return os.path.isfile(path) and os.path.splitext(os.path.basename(path))[0] == "ffmpeg"

        def __ffmpeg_val_set():
            if __ffmpeg_exists(CONFIG['ffmpegPath']):
                self.ffmpeg_val.set("OK")
            else:
                self.ffmpeg_val.set("not found")
            return

        def __ffmpeg_callback():
            filename = tkFileDialog.askopenfilename()
            if __ffmpeg_exists(filename):
                CONFIG['ffmpegPath'] = filename
                self.__set_config()
            else:
                CONFIG['ffmpegPath'] = "ffmpeg"
                self.__set_config()
            __ffmpeg_val_set()
            return

        __ffmpeg_val_set()
        ffmpeg_bt = Button(labelframe, text=self.ffmpeg_val.get(), textvariable=self.ffmpeg_val, relief=RAISED,
                           command=__ffmpeg_callback, width=10)
        ffmpeg_bt.grid(row=5, column=1, columnspan=2, sticky=W)

        # FFPROBE
        Label(labelframe, text='ffprobe : ').grid(row=6, column=0, sticky=E)

        def __ffprobe_exists(path):
            return os.path.isfile(path) and os.path.splitext(os.path.basename(path))[0] == "ffprobe"

        def __ffprobe_val_set():
            if __ffprobe_exists(CONFIG['ffprobePath']):
                self.ffprobe_val.set("OK")
            else:
                self.ffprobe_val.set("not found")
            return

        def __ffprobe_callback():
            filename = tkFileDialog.askopenfilename()
            if __ffprobe_exists(filename):
                CONFIG['ffprobePath'] = filename
                self.__set_config()
            else:
                CONFIG['ffprobePath'] = "ffprobe"
                self.__set_config()
            __ffprobe_val_set()
            return

        __ffprobe_val_set()
        ffprobe_bt = Button(labelframe, text=self.ffprobe_val.get(), textvariable=self.ffprobe_val, relief=RAISED,
                            command=__ffprobe_callback, width=10)
        ffprobe_bt.grid(row=6, column=1, columnspan=2, sticky=W)
        return

    # noinspection PyUnusedLocal
    def __callback(self, temp=None):
        if self.video_val.get() == "rawvideo" and not (self.ext_val.get() == ".mov"):
            tkMessageBox.showwarning("残念なお知らせ", "rawvideoはmovでのみ、ご利用いただけます。")
            self.__reset_config()
        else:
            self.__set_config()

    def __set_config(self):
        CONFIG['video'] = self.video_val.get()
        CONFIG['audio'] = self.audio_val.get()
        CONFIG['zoom'] = self.zoom_val.get()
        CONFIG['fps'] = self.fps_val.get()
        CONFIG['isForceFrameRate'] = self.force_val.get()
        CONFIG['ext'] = self.ext_val.get()
        f = open(CONFIG_FILE_PATH, 'w')
        json.dump(CONFIG, f)
        f.close()
        return

    def __reset_config(self):
        self.video_val.set(CONFIG['video'])
        self.audio_val.set(CONFIG['audio'])
        self.zoom_val.set(CONFIG['zoom'])
        self.fps_val.set(CONFIG['fps'])
        self.force_val.set(CONFIG['isForceFrameRate'])
        self.ext_val.set(CONFIG['ext'])
        return


class TextHandler(logging.Handler):
    def __init__(self, text):
        logging.Handler.__init__(self)

        # Store a reference to the Text it will log to
        self.text = text
        # init LV colors
        self.text.tag_configure("DEBUG", foreground="cyan")
        self.text.tag_configure("INFO", foreground="green")
        self.text.tag_configure("WARNING", foreground="ORANGE")
        self.text.tag_configure("ERROR", foreground="red")
        self.text.tag_configure("CRITICAL", foreground="red")

    def emit(self, record):
        msg = self.format(record)
        self.text.configure(state='normal')
        self.text.insert(Tkinter.END, msg + '\n', record.levelname)
        self.text.configure(state='disabled')
        # AutoScroll to the bottom
        self.text.yview(Tkinter.END)
        self.text.update()


class LoggerWindow():
    def __init__(self, parent):
        """
        loggerWindowを作成します。
        loggerを作成して
        :param parent: Tk.root
        """
        import ScrolledText

        parent.title('2mp4 log')
        st = ScrolledText.ScrolledText(parent, state='disabled', bg="black", fg="white")
        st.configure(font='TkFixedFont')
        st.pack(side="top", fill="both", expand=True)
        self.handler = TextHandler(st)
