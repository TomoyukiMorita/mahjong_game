from typing import Any, List, Tuple, Optional
from tkinter import *
from tkinter.ttk import *
from PIL import Image, ImageTk

import numpy as np
import random
import copy
import json
from queue import Queue
from threading import Event, Thread
import time

from chadef import Cha, Field
from tehaidef import *
from yaku_check_v2 import *
from chadef import *
import cppfunc

dir_image_button = "./haiga-m/"

dir_image_button_small = "./haiga-s/"

shu_image_button = [
    "man1.gif", "man2.gif", "man3.gif", "man4.gif", "man5.gif", "man6.gif", "man7.gif", "man8.gif", "man9.gif",
    "pin1.gif", "pin2.gif", "pin3.gif", "pin4.gif", "pin5.gif", "pin6.gif", "pin7.gif", "pin8.gif", "pin9.gif",
    "sou1.gif", "sou2.gif", "sou3.gif", "sou4.gif", "sou5.gif", "sou6.gif", "sou7.gif", "sou8.gif", "sou9.gif",
    "ji1-ton.gif", "ji2-nan.gif", "ji3-sha.gif", "ji4-pei.gif", "ji5-haku.gif", "ji6-hatsu.gif", "ji7-chun.gif",
    "man-aka5.gif", "pin-aka5.gif", "sou-aka5.gif"
]

class MainWindow(Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.__master= master
        self.pack()

        pai_images = []
        pai_images_small = []
        for pai in PAka:
            img = None
            img_small = None
            if shu_image_button[pai]:
                image = dir_image_button + shu_image_button[pai]
                img = PhotoImage(file=image)
                # image_small = dir_image_button_small + shu_image_button[i]
                # img_small = PhotoImage(file=image_small)
                img_small = img.subsample(2)
            pai_images.append(img)
            pai_images_small.append(img_small)
        self.pai_images = pai_images
        self.pai_images_small = pai_images_small

        agari = AgariWindow(self)
        # agari.mainloop()

class AgariWindow(Toplevel):
    def __init__(self,master=None):
        super().__init__(master)
        self.__master = master
        self.title("agari")

        frame_tehai = Frame(self)
        frame_tehai.pack()
        for pai in [PAka.M1,PAka.HAKU,PAka.M5A] + [PAka.S5A]:
            # Label(frame_tehai, image=mainwin.pai_images[pai.value]).pack(side="left")
            Label(frame_tehai, image=master.pai_images[pai.value]).pack(side="left")

        Button(self, text="OK", command=self.ok_clicked).pack()

    def ok_clicked(self):
        self.destroy()


def main():
    # root = Tk()
    # mainwin = MainWindow(master = root)
    # root.mainloop()

    # root = Tk()
    mainwin = MainWindow()
    mainwin.mainloop()




if __name__ == '__main__':
    main()