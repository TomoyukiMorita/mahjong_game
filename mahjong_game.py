#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any, List, Tuple, Optional
from tkinter import *
from tkinter.ttk import *
import PIL.Image, PIL.ImageTk

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
    "man-aka5.gif", "pin-aka5.gif", "sou-aka5.gif", "ura.gif"
]

shu_image_yoko = [
    "yoko-man1.gif", "yoko-man2.gif", "yoko-man3.gif", "yoko-man4.gif", "yoko-man5.gif", "yoko-man6.gif",
    "yoko-man7.gif", "yoko-man8.gif", "yoko-man9.gif",
    "yoko-pin1.gif", "yoko-pin2.gif", "yoko-pin3.gif", "yoko-pin4.gif", "yoko-pin5.gif", "yoko-pin6.gif",
    "yoko-pin7.gif", "yoko-pin8.gif", "yoko-pin9.gif",
    "yoko-sou1.gif", "yoko-sou2.gif", "yoko-sou3.gif", "yoko-sou4.gif", "yoko-sou5.gif", "yoko-sou6.gif",
    "yoko-sou7.gif", "yoko-sou8.gif", "yoko-sou9.gif",
    "yoko-ji1-ton.gif", "yoko-ji2-nan.gif", "yoko-ji3-sha.gif", "yoko-ji4-pei.gif", "yoko-ji5-haku.gif",
    "yoko-ji6-hatsu.gif", "yoko-ji7-chun.gif",
    "yoko-man-aka5.gif", "yoko-pin-aka5.gif", "yoko-sou-aka5.gif"
]


# 卓の制御
class Taku:
    def __init__(self, num_player: int):
        self.event_change_notify = Event()  # GUIに変更を通知するためのイベント

        self.players = []
        for i in range(num_player):
            if i == 0:
                self.players.append(Player(mode=Player.Mode.MANUAL))
            else:
                self.players.append(Player(mode=Player.Mode.CPU))
        self.fieldctrl = FieldCtrl(self.players, self.event_change_notify)

    # 状態制御
    def update(self):
        self.fieldctrl.update()


# 場の制御
class FieldCtrl:
    field: Field
    turn_player: int
    cha: Cha
    agari_state: Optional[AgariState]

    class State(enum.Enum):
        DAHAI = enum.auto()
        NAKI = enum.auto()
        RESULT = enum.auto()
        END = enum.auto()

    def __init__(self, players, event_change_notify):
        # 引数から変数を初期化
        self.players = players
        self.event_change_notify = event_change_notify

        # 引数以外から変数を初期化
        self.state = None
        self.turn_player = 0

        self.__start()

    def __start(self):

        self.field = Field(bakaze=Kaze.TON, kyoku=1, honba=0, num_kyotaku=0, num_chas=len(self.players))

        for i in range(len(self.players)):
            self.players[i].set_field_cha(self.field, self.field.chas[i])

        # 第1ツモ
        self.turn_player = self.field.kyoku - 1
        self.__tsumo()
        self.state = self.State.DAHAI

    def __tsumo(self):
        self.players[self.turn_player].cha.tsumo()
        self.players[self.turn_player].state_dahai = Player.StateDahai.START  # もっといい場所がある
        self.event_change_notify.set()

    def update(self):
        if self.state == self.State.DAHAI:
            dahai_action = self.players[self.turn_player].wait_dahai()

            if dahai_action == Player.DahaiAction.TSUMOAGARI:
                self.field.calc_field_result(True, self.turn_player)
                self.state = self.State.RESULT
                self.event_change_notify.set()
                return

            elif dahai_action == Player.DahaiAction.DAHAI:
                if self.field.yama.tsumo_remain > 0:
                    self.state = self.State.NAKI
                else:
                    self.field.calc_field_result(False)
                    self.state = self.State.RESULT
                self.event_change_notify.set()
                return

            elif dahai_action == Player.DahaiAction.REACH:
                pass
                self.event_change_notify.set()

            elif dahai_action == Player.DahaiAction.KONG:
                pass  # 未実装
                self.event_change_notify.set()

        if self.state == self.State.NAKI:
            # 未実装
            self.turn_player = (self.turn_player + 1) % len(self.players)
            self.__tsumo()
            self.state = self.State.DAHAI
            self.event_change_notify.set()

        if self.state == self.State.RESULT:
            self.state = self.State.END
            self.event_change_notify.set()

        if self.state == self.State.END:
            pass


# プレイヤーの制御
class Player:
    class Mode(enum.Enum):
        MANUAL = enum.auto()
        CPU = enum.auto()

    class State(enum.Enum):
        WAIT = enum.auto()
        DAHAI = enum.auto()
        NAKI = enum.auto()

    class StateDahai(enum.Enum):
        START = enum.auto()
        WAIT_INPUT = enum.auto()
        END = enum.auto()

    class DahaiAction(enum.Enum):
        NONE = enum.auto()
        DAHAI = enum.auto()
        REACH = enum.auto()
        TSUMOAGARI = enum.auto()
        KONG = enum.auto()  # 未実装

    def __init__(self, mode=Mode.MANUAL):
        self.mode = mode
        self.state: Player.State = Player.State.WAIT
        self.__is_auto: bool = False
        self.state_dahai: Player.StateDahai = Player.StateDahai.START
        self.dahai_action: Player.DahaiAction = Player.DahaiAction.NONE
        self.field = None
        self.cha = None
        self.ten = 25000
        self.__is_result_ok = False

    @property
    def is_auto(self):
        return self.__is_auto

    @is_auto.setter
    def is_auto(self, value):
        self.__is_auto = value

    def set_field_cha(self, field, cha):
        self.field = field
        self.cha = cha

    # 状態制御
    def wait_dahai(self):
        dahai_action = self.DahaiAction.NONE

        if self.state_dahai == self.StateDahai.START:
            self.state_dahai = self.StateDahai.WAIT_INPUT

        if self.state_dahai == self.StateDahai.WAIT_INPUT:
            if self.mode == self.Mode.CPU:
                self.__dahai_cpu()
            if (self.mode == self.Mode.MANUAL) and self.__is_auto:
                self.__dahai_auto()

        if self.state_dahai == self.StateDahai.END:
            dahai_action = self.dahai_action

        return dahai_action

    # 状態制御
    def wait_result_ok(self):
        if self.mode == self.Mode.CPU:
            return True
        if self.mode == self.Mode.MANUAL:
            return self.__is_result_ok

    # イベント処理
    def result_ok(self):
        self.__is_result_ok = True

    # イベント処理
    def reach(self):
        if self.state_dahai != Player.StateDahai.WAIT_INPUT:
            return False

        self.cha.reach()

        self.dahai_action = Player.DahaiAction.REACH

        return True

    # イベント処理
    def tsumoagari(self):
        if self.state_dahai != Player.StateDahai.WAIT_INPUT:
            return False

        self.dahai_action = Player.DahaiAction.TSUMOAGARI
        self.state_dahai = Player.StateDahai.END

        return True

    # イベント処理
    def dahai(self, dahainum):
        if self.state_dahai != Player.StateDahai.WAIT_INPUT:
            return False

        self.cha.dahai(dahainum)

        self.dahai_action = Player.DahaiAction.DAHAI
        self.state_dahai = Player.StateDahai.END

        return True

    # 自動で打牌を行う
    def __dahai_auto(self):
        if self.cha.can_tsumoagari or self.cha.canReach:
            return

        dapais = self.cha.dapais_max
        dapai = dapais[random.randrange(len(dapais))]

        pakas = list(self.cha.tehai.pais)
        pakas.append(self.cha.tehai.tsumo_pai)
        pkuros, jk = aka2kuro_and_count(pakas)
        pkuros = list(pkuros)

        if dapai in pkuros:
            ida = pkuros.index(dapai)
        else:
            ida = pakas.index(dapai)

        if ida > len(self.cha.tehai.pais) - 1:  # ツモ切り
            ida = -1

        self.dahai(ida)

    # 自動で打牌を行う
    def __dahai_cpu(self):
        if self.cha.can_tsumoagari:
            self.tsumoagari()
            return
        elif self.cha.canReach:
            self.reach()
            return

        dapais = self.cha.dapais_max
        dapai = dapais[random.randrange(len(dapais))]

        pakas = list(self.cha.tehai.pais)
        pakas.append(self.cha.tehai.tsumo_pai)
        pkuros, jk = aka2kuro_and_count(pakas)
        pkuros = list(pkuros)

        if dapai in pkuros:
            ida = pkuros.index(dapai)
        else:
            ida = pakas.index(dapai)

        if ida > len(self.cha.tehai.pais) - 1:  # ツモ切り
            ida = -1

        self.dahai(ida)


class PaiClick:
    def __init__(self, win, num):
        self.__win = win
        self.__num = num

    def __call__(self, event=None):
        self.__win.dahai_clicked(self.__num)


class MainWindow(Tk):
    def __init__(self, ):
        super().__init__()
        # self.pack()
        self.geometry("640x480")
        self.title("一人麻雀シミュレータ")

        self.pai_images = []
        self.pai_images_small = []
        self.pai_images_small_yoko = []
        for i in range(38):
            filename = dir_image_button + shu_image_button[i]
            img = PhotoImage(file=filename)
            self.pai_images.append(img)
            img_small = img.subsample(2)
            self.pai_images_small.append(img_small)
            if i != 37:
                img_small_yoko = PhotoImage(file=dir_image_button + shu_image_yoko[i]).subsample(2)
                self.pai_images_small_yoko.append(img_small_yoko)

        self.__create_widgets()

        self.is_running = False

    # ウィジェットの生成
    def __create_widgets(self):

        # 情報ラベル（上）
        self.label1 = Label(self, text="None")
        self.label1.pack()

        # 河
        # self.framekawa = Frame()
        # self.framekawa.pack(side="top")
        self.frames_kawa_player = []
        self.lables_paikawa_playername = []
        self.labless_paikawa = []
        for i in range(4):
            frame_kawa_player = Frame()
            frame_kawa_player.pack(side='top')
            self.frames_kawa_player.append(self.frames_kawa_player)
            lable_paikawa_playername = Label(frame_kawa_player, text="None")
            lable_paikawa_playername.pack()
            self.lables_paikawa_playername.append(lable_paikawa_playername)
            lables_paikawa = [Label(image=self.pai_images_small[0]) for i in range(64)]
            [l.pack(in_=frame_kawa_player, side='left') for l in lables_paikawa]
            [l.lower() for l in lables_paikawa]  # 隠す
            self.labless_paikawa.append(lables_paikawa)

        # 手牌
        self.buttonsframe0 = Frame()
        self.buttonsframe0.pack(side="top")
        self.buttons_pai = [Button(self.buttonsframe0, image=self.pai_images[0]) for i in range(14)]
        [b.pack(side='left') for b in self.buttons_pai]

        # ボタン
        self.buttonsframe1 = Frame()
        self.buttonsframe1.pack(side="top")
        self.button_start = Button(self.buttonsframe1, text="start", command=self.start_clicked)
        self.button_start.pack(side="left")
        self.button_reach = Button(self.buttonsframe1, text="リーチ", command=self.reach_clicked, state="disabled")
        self.button_reach.pack(side="left")
        self.button_tsumoagari = Button(self.buttonsframe1, text="ツモ", command=self.tsumoagari_clicked,
                                        state="disabled")
        self.button_tsumoagari.pack(side="left")
        self.button_auto = Button(self.buttonsframe1, text="オート", command=self.auto_clicked, state="disabled")
        self.button_auto.pack(side="left")

        # 情報ラベル（下）
        self.labelframe2 = Frame()
        self.labelframe2.pack(side="top")
        self.label_shanten = Label(self.labelframe2, text="None")
        self.label_shanten.pack(side="left")
        self.label_machi = Label(self.labelframe2, text="None")
        self.label_machi.pack(side="left")

        # メッセージボックス
        self.txtframe = Frame()
        self.txtframe.pack(side="top")
        self.txtbox = Text(self.txtframe, width=100, height=20)
        self.txtbox.grid(row=1, column=0, sticky=(N, W, S, E))
        # Scrollbar
        self.scrollbar = Scrollbar(
            self.txtframe,
            orient=VERTICAL,
            command=self.txtbox.yview)
        self.txtbox['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.grid(row=1, column=1, sticky=(N, S))

    def start_game(self):
        if self.is_running:
            self.stop_game()

        self.taku = Taku(4)
        self.thread_sim_stop = Event()
        self.thread_sim = Thread(target=simloop, args=(self.thread_sim_stop, self.taku, self))
        self.is_running = True
        self.thread_sim.start()

    def stop_game(self):
        self.thread_sim_stop.set()
        self.thread_sim.join()
        self.thread_sim_stop.clear()
        self.is_running = False

    def start_clicked(self):
        self.start_game()

    def reach_clicked(self):
        if not self.taku.players[0].reach():
            return

        self.print("リーチ")

    def tsumoagari_clicked(self):
        if not self.taku.players[0].tsumoagari():
            return

    def dahai_clicked(self, num):
        if num == 13:  # ツモ切り
            num = -1
        if not self.taku.players[0].dahai(num):
            return

    def auto_clicked(self):
        self.taku.players[0].is_auto = not self.taku.players[0].is_auto

    def print(self, str1):
        self.txtbox.insert('end', str1 + "\n")

    # ラベルの更新
    def set_label_state(self, str1):
        self.label1["text"] = str1

    def set_label_shanten(self, str1):
        self.label_shanten["text"] = str1

    def set_label_machi(self, str1):
        self.label_machi["text"] = str1

    # 手牌の表示
    def show_tehai(self):
        tehai_pais = self.taku.players[0].cha.tehai.pais
        tm_pai = self.taku.players[0].cha.tehai.tsumo_pai
        can_tsumoagari = self.taku.players[0].cha.can_tsumoagari
        canReach = self.taku.players[0].cha.canReach

        i = 0
        for pai in tehai_pais:
            self.buttons_pai[i]["command"] = PaiClick(self, i)
            self.buttons_pai[i]["image"] = self.pai_images[pai]
            i += 1

        # ツモ牌の表示
        self.buttons_pai[i]["command"] = PaiClick(self, i)
        self.buttons_pai[i]["image"] = self.pai_images[tm_pai if tm_pai is not None else 37]

        # ボタンの有効or無効
        if can_tsumoagari:
            self.button_tsumoagari["state"] = 'normal'
        else:
            self.button_tsumoagari["state"] = 'disabled'
        if canReach:
            self.button_reach["state"] = 'normal'
        else:
            self.button_reach["state"] = 'disabled'
        self.button_auto["state"] = 'normal'

    # 河の表示
    def show_kawa(self):
        player0 = self.taku.players[0]
        field = player0.field

        j = 0
        for player in self.taku.players:
            pais = player.cha.kawa.pais
            self.lables_paikawa_playername[j]["text"] = str(player.cha.jikaze) + "家 " + str(player.ten) + "点"
            lables_paikawa = self.labless_paikawa[j]
            [l.lower() for l in lables_paikawa]
            i = 0
            for pai in pais:
                if player.cha.kawa.is_reachs[i]:
                    lables_paikawa[i]["image"] = self.pai_images_small_yoko[int(pai)]
                else:
                    lables_paikawa[i]["image"] = self.pai_images_small[int(pai)]
                lables_paikawa[i].lift()
                i += 1
            j += 1

    def show_tsumo(self):
        player = self.taku.players[0]
        field = player.field

        # 牌姿の表示
        str1 = str(field.bakaze) + str(field.kyoku) + '局,' \
               + str(player.cha.jikaze) + '家, ' \
               + str(player.cha.jumme + 1) + '順目, ドラ:' + shu_name[int(field.dora_state.omotes[0])]
        self.set_label_state(str1)

        # シャン点数の表示他
        if player.cha.tehai.shanten_state["min"] == -1:
            if player.cha.agari_state.can_agari:
                self.set_label_shanten('和了')
            else:
                self.set_label_shanten('役無し')
        elif player.cha.tehai.shanten_state["min"] == 0:
            self.set_label_shanten("聴牌")
        else:
            self.set_label_shanten(str(player.cha.tehai.shanten_state["min"]) + "向聴")

        # 有効牌の表示
        #
        if len(player.cha.dapais_max) > 0:  # 聴牌なら待ち牌を表示
            # 待ちの表示
            str1 = '何切る: '
            for pkuro in player.cha.dapais_max:
                str1 += ' ' + shu_name[pkuro]
            self.set_label_machi(str1)
        else:
            self.set_label_machi("")

    def show_machi(self):
        player = self.taku.players[0]
        field = player.field

        # シャンテン数
        machis = player.cha.tehai.machis
        if len(machis) > 0:  # 聴牌なら待ち牌を表示
            # 待ちの表示
            str1 = '待ち: '
            for pai in machis:
                str1 += ' ' + shu_name[pai]
            self.set_label_machi(str1)
        else:
            self.set_label_machi("")

    def show_result(self):

        resultwin = ResultWindow(self, self.taku)


class ResultWindow(Toplevel):
    def __init__(self, mainwin: MainWindow, taku : Taku):
        super().__init__()
        self.__mainwin = mainwin

        field_result = taku.fieldctrl.field.field_result
        if field_result.is_agari:
            tehai = taku.fieldctrl.field.chas[field_result.agari_player_num].tehai
            if field_result.agari_player_num == 0:
                str1 = 'あなたの和了です'
            else:
                str1 = str(taku.fieldctrl.field.chas[field_result.agari_player_num].jikaze) + '家の和了です'
            Label(self, text=str1).pack()

            str1 = str(taku.fieldctrl.field.bakaze) + str(taku.fieldctrl.field.kyoku) + '局,' \
                   + str(taku.fieldctrl.field.chas[field_result.agari_player_num].jikaze) + '家, ' \
                   + str(taku.fieldctrl.field.chas[field_result.agari_player_num].jumme + 1) + '順目, ドラ:' + str(taku.fieldctrl.field.dora_state.omotes[0])
            if field_result.agari_state.yaku_state["reach"]:
                str1 += ", 裏ドラ:" + str(taku.fieldctrl.field.dora_state.uras[0])
            Label(self, text=str1).pack()

            frame_tehai = Frame(self)
            frame_tehai.pack()
            for pai in tehai.pais + [tehai.tsumo_pai]:
                Label(frame_tehai, image=mainwin.pai_images[pai.value]).pack(side="left")

            str1 = ""
            agari_state = tehai.agari_state
            for key in agari_state.yaku_state.keys():
                if agari_state.yaku_state[key] == 1:
                    str1 += yaku_name[key] + ","

            if agari_state.dora_nums["omote"] >= 1:
                str1 += "ドラ" + str(agari_state.dora_nums["omote"]) + ","
            if agari_state.dora_nums["aka"] >= 1:
                str1 += "赤ドラ" + str(agari_state.dora_nums["aka"]) + ","
            if agari_state.dora_nums["ura"] >= 1:
                str1 += "裏ドラ" + str(agari_state.dora_nums["ura"]) + ","
            Label(self, text=str1).pack()

            str1 = str(agari_state.hu) + "符 " + str(agari_state.han) + "翻" \
                   + str(agari_state.name) + " " + str(agari_state.ten) + "点"
            Label(self, text=str1).pack()
        else:
            str1 = '流局です'
            Label(self, text=str1).pack()

        Button(self, text="OK", command=self.ok_clicked).pack()

    def ok_clicked(self):
        self.destroy()


def simloop(event_stop: Event, taku: Taku, gui: MainWindow):
    fieldstate_prev: Optional[FieldCtrl.State] = None

    while not event_stop.wait(10 / 1000):

        taku.update()

        if taku.event_change_notify.wait(0):
            taku.event_change_notify.clear()

            if taku.fieldctrl.state == FieldCtrl.State.DAHAI \
                    and taku.fieldctrl.turn_player == 0:
                gui.show_kawa()
                gui.show_tehai()
                gui.show_tsumo()

            elif gui.taku.fieldctrl.state == FieldCtrl.State.RESULT \
                    and fieldstate_prev != FieldCtrl.State.RESULT:
                gui.show_result()

            else:
                gui.show_kawa()
                gui.show_tehai()
                gui.show_machi()

            fieldstate_prev = gui.taku.fieldctrl.state


def main():
    win = MainWindow()
    win.mainloop()


if __name__ == '__main__':
    main()
