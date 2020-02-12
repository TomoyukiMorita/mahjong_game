#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 手牌
# 
# 手牌からシャンテン数を求める
#

from typing import Any, List, Tuple, Optional
import numpy as np
import enum
import copy
from paidef import Color,PKuro,PAka,Kaze,aka2kuro_and_count
from blockdef import Block
from cppfunc import calc_shanten
from yaku_check_v2 import yaku_check_max, AgariState, State4YakuCheck


class Tehai:  # 手牌
    __pais : List[PAka] # 鳴いていない牌またはShu
    __tsumo_pai: Optional[PAka] # ツモ牌
    __naki_blocks: List[Optional[Block]] # 鳴いている牌のグループ
    __agari_state : AgariState # 上がり状態
    __machis : List[PKuro] # 待ち牌

    def __init__(self, pais: List[PAka], tsumo_pai: Optional[PAka] = None, naki_blocks: List[Optional[Block]] = []):
        self.__pais = pais  # 鳴いていない牌またはShu
        self.__naki_blocks = naki_blocks  # 鳴いている牌のグループ

        self.__agari_state = None
        self.__machis = []

        self.__pais.sort()

        self.__tsumo_pai = None
        if tsumo_pai is not None:
            self.tsumo(tsumo_pai)

    def tsumo(self, pai: PAka):  # ツモる
        self.__tsumo_pai = pai
        self.__calc_shanten()

    # 捨てる
    # i : 左からi番目を捨てる（ツモ切りは-1）
    def sute(self, i: int):
        if i == -1:  # ツモ切り
            dahai = self.__tsumo_pai
        else:  # 手出し
            if not i > -100:
                pass
            dahai = self.__pais[i]
            self.__pais[i] = self.__tsumo_pai
        self.__tsumo_pai = None
        self.__pais.sort()
        self.__calc_shanten()
        self.__calc_machis()
        return dahai

    def __calc_shanten(self) -> None:  # シャンテン数を求める
        akas = copy.copy(self.__pais)
        if self.__tsumo_pai is not None:
            akas.append(self.__tsumo_pai)
        kuros, jk = aka2kuro_and_count(akas)
        self.__shanten_state = calc_shanten(kuros)

    def __calc_machis(self) -> None:  # 待ちを求める
        if self.tsumo_pai is not None and self.__shanten_state["min"] == 0:
            machis = machi_check(self.__shanten_state["blockss"])
        else:
            machis = []
        self.__machis = machis

    # Cha.get_agari_state()から呼び出される
    def get_agari_state(self, state4yc: State4YakuCheck) -> AgariState:
        if not self.__shanten_state["min"] == -1:
            self.__agari_state = AgariState()
            return self.__agari_state
        pakas = self.__pais + [self.__tsumo_pai]
        pkuros, nAka = aka2kuro_and_count(pakas)
        blockss = [blocks + self.__naki_blocks for blocks in self.__shanten_state["blockss"]]

        if self.__shanten_state["normal"] == -1:
            state4yc.agari_type = State4YakuCheck.Agari_type.NORMAL
        elif self.__shanten_state["kokusi"] == -1:
            state4yc.agari_type = State4YakuCheck.Agari_type.KOKUSI
        elif self.__shanten_state["chitoi"] == -1:
            state4yc.agari_type = State4YakuCheck.Agari_type.CHITOI

        self.__agari_state = yaku_check_max(pkuros, self.__tsumo_pai.kuro, blockss, state4yc, nAka)
        return self.__agari_state

    def __repr__(self):
        return "<" + "".join([str(p) for p in self.__pais]) + " " + str(self.__tsumo_pai) + str(
            self.__naki_blocks) + ">"

    @property
    def machis(self) -> List[PKuro]:
        return self.__machis

    @property
    def agari_state(self) -> AgariState:
        return self.__agari_state

    @property
    def pais(self) -> List[PAka]:
        return self.__pais

    @property
    def tsumo_pai(self) -> Optional[PAka]:
        return self.__tsumo_pai

    @property
    def naki_blocks(self) -> List[Optional[Block]]:
        return self.__naki_blocks

    @property
    def shanten_state(self) -> dict:
        return self.__shanten_state

    @property
    def isMenzen(self) -> bool:  # 門前かどうか
        return len(self.naki_blocks) == 0


# TODO : 国士無双聴牌だとバグる
# テンパイしている手牌に対して待ちハイを返す
def machi_check(blockss: List[List[Block]]) -> List[PKuro]:
    machis = []

    for blocks in blockss:
        # トイツを抽出
        toitsus = [b for b in blocks if b.kind == Block.KIND.TOITSU]

        if len(toitsus) == 2:  # トイツが2つある場合→シャボ待ち
            for toitsu in toitsus:
                machis.append(PKuro.color_num2pai(toitsu.color, toitsu.num))

        elif len(toitsus) == 1:  # トイツが1つだけある場合→両面、カンチャン、ペンちゃん待ち
            tahtsu = [b for b in blocks if b.kind in [Block.KIND.RYANMEN, Block.KIND.KANCHAN]][0]
            # 両面・ペンチャン
            if tahtsu.kind == Block.KIND.RYANMEN:
                if tahtsu.num == 1:
                    machis.append(PKuro.color_num2pai(tahtsu.color, tahtsu.num + 2))
                elif tahtsu.num == 8:
                    machis.append(PKuro.color_num2pai(tahtsu.color, tahtsu.num - 1))
                else:
                    machis.append(PKuro.color_num2pai(tahtsu.color, tahtsu.num - 1))
                    machis.append(PKuro.color_num2pai(tahtsu.color, tahtsu.num + 2))

            # カンチャン
            elif tahtsu.kind == Block.KIND.KANCHAN:
                machis.append(PKuro.color_num2pai(tahtsu.color, tahtsu.num + 1))

        elif len(toitsus) == 0:  # トイツがない場合→単騎待ち
            koritsu = [b for b in blocks if b.kind == Block.KIND.KORITSU][0]
            machis.append(PKuro.color_num2pai(koritsu.color, koritsu.num))

    machis = list(set(machis))  # 重複を削除
    machis.sort()  # ソート

    return machis


if __name__ == "__main__":
    from func4debug import *

    pais = str2pais("123567m123p44z56s7s")
    tehai = Tehai(pais=pais[:-1], tsumo_pai=pais[-1])
    state4yc = State4YakuCheck()
    state4yc.isTsumoing = True
    agari_state = tehai.get_agari_state(state4yc)
    print(agari_state)
