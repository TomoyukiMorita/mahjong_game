#!/usr/bin/env python
# -*- coding: utf-8 -*-

import enum
from typing import Optional

from paidef import Color, PAka, Kaze

#
# ブロックの定義
#
# ブロックコードルール
# 1-9 : 孤立牌
# 11-19 : 対子
# 21-28 : 両面・ペンチャンターツ
# 31-37 : カンチャンターツ
# 41-49 : コーツ
# 51-59 : シュンツ


bcode_nameint = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    0, 11, 22, 33, 44, 55, 66, 77, 88, 99,
    0, 12, 23, 34, 45, 56, 67, 78, 89, 0,
    0, 13, 24, 35, 46, 57, 68, 79, 0, 0,
    0, 111, 222, 333, 444, 555, 666, 777, 888, 999,
    0, 123, 234, 345, 456, 567, 678, 789, 0, 0,
]


class Block:
    """
    牌のブロック
    """

    # タイプコード
    class KIND(enum.IntEnum):
        KORITSU = 0
        TOITSU = 1
        RYANMEN = 2
        KANCHAN = 3
        KOHTSU = 4
        SHUNTSU = 5

    # 副露コード : 0:門前, 1:チー, 2:ポン, 3:暗槓, 4:加槓, 5:明槓
    class HuroCode(enum.IntEnum):
        MENZEN = 0
        CHOW = enum.auto()
        PONG = enum.auto()
        AN_KONG = enum.auto()
        KA_KONG = enum.auto()
        MIN_KONG = enum.auto()

    # 鳴いた場所 : 0:上家, 1:対面, 2:下家
    class Naki_from(enum.IntEnum):
        KAMICHA = 0
        TOIMEN = enum.auto()
        SHIMOCHA = enum.auto()

    def __init__(self, block_code, huro_code=0  # Block.Huro_code.MENZEN
                 , naki_from=0  # Block.Naki_from.KAMICHA
                 , naki_pai: Optional[PAka] = None
                 ):
        self.block_code = block_code
        self.huro_code = huro_code  # 副露コード
        self.naki_from = naki_from  # 鳴いた場所
        self.naki_pai = naki_pai  # 鳴いた牌

        self.num = int(block_code % 10)
        self.kind = Block.KIND(int(block_code / 10) % 10)
        self.color = Color(int((block_code / 100) % 10))

    @property
    def isSarashi(self):  # 晒したかどうか
        return self.huro_code != self.HuroCode.MENZEN

    def __repr__(self):
        color_name = ["", "m", "p", "s", "z"]
        md = self.block_code % 100
        return str(bcode_nameint[int(md)]) + color_name[self.color.value]

    def __int__(self):
        return self.block_code

    def calc_hu(self, bakaze: Kaze, jikaze: Kaze) -> int:  # 符計算
        # アタマの符。天鳳ルール準拠（ダブ東、ダブ南は4符）
        if self.kind == self.KIND.TOITSU:
            hu = 0
            if self.color == Color.JIHAI:
                if self.num in [PAka.HAKU.num, PAka.HATSU.num, PAka.CHUN.num, bakaze.paka.num]:
                    hu += 2
                if self.num == jikaze.pkuro.num:
                    hu += 2
            return hu

        elif self.kind == self.KIND.KOHTSU:  # コーツ
            hu = 0
            if self.huro_code == self.HuroCode.PONG:  # ミンコ
                hu = 2
            elif self.huro_code == self.HuroCode.MENZEN:  # アンコ
                hu = 4
            elif self.huro_code in [self.HuroCode.KA_KONG, self.HuroCode.MIN_KONG]:  # 明槓
                hu = 8
            elif self.huro_code == self.HuroCode.AN_KONG:  # 暗槓
                hu = 16

            # 么九牌は2倍
            if (self.color == Color.JIHAI) or ((self.color != Color.JIHAI) and (self.num in [1, 9])):
                return hu * 2
            else:
                return hu

        elif self.kind == self.KIND.SHUNTSU:  # シュンツは0符
            return 0
