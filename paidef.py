#!/usr/bin/env python
# -*- coding: utf-8 -*-


from typing import List, Tuple, Optional
import enum


#
# 麻雀牌の定義
#

class Color(enum.IntEnum):
    """
    牌の色
    """
    NONE = 0
    MANZU = 1
    PINZU = 2
    SOHZU = 3
    JIHAI = 4


class PKuro(enum.IntEnum):
    """
    黒牌
    """
    M1 = 0
    M2 = 1
    M3 = 2
    M4 = 3
    M5 = 4
    M6 = 5
    M7 = 6
    M8 = 7
    M9 = 8
    P1 = 9
    P2 = 10
    P3 = 11
    P4 = 12
    P5 = 13
    P6 = 14
    P7 = 15
    P8 = 16
    P9 = 17
    S1 = 18
    S2 = 19
    S3 = 20
    S4 = 21
    S5 = 22
    S6 = 23
    S7 = 24
    S8 = 25
    S9 = 26
    TON = 27
    NAN = 28
    SHA = 29
    PE = 30
    HAKU = 31
    HATSU = 32
    CHUN = 33

    def __str__(self):
        return shu_name[self.value]

    @property
    def num(self):
        return shu_num[self.value]

    @property
    def color(self):
        return Color(shu_color[self.value])

    @classmethod
    def color_num2pai(cls, color: Color, num: int):
        return cls((color - 1) * 9 + num - 1)


class PAka(enum.IntEnum):
    """
    赤牌
    """
    M1 = 0
    M2 = 1
    M3 = 2
    M4 = 3
    M5 = 4
    M6 = 5
    M7 = 6
    M8 = 7
    M9 = 8
    P1 = 9
    P2 = 10
    P3 = 11
    P4 = 12
    P5 = 13
    P6 = 14
    P7 = 15
    P8 = 16
    P9 = 17
    S1 = 18
    S2 = 19
    S3 = 20
    S4 = 21
    S5 = 22
    S6 = 23
    S7 = 24
    S8 = 25
    S9 = 26
    TON = 27
    NAN = 28
    SHA = 29
    PE = 30
    HAKU = 31
    HATSU = 32
    CHUN = 33
    M5A = 34
    P5A = 35
    S5A = 36

    @classmethod
    def color_num2pai(cls, color: Color, num: int, is_aka: bool = False):
        if is_aka:
            return cls(33 + color)
        else:
            return cls((color - 1) * 9 + num - 1)

    def __lt__(self, other):
        if self.kuro.value == other.kuro.value:
            return (1 if self.is_aka else 0) < (1 if other.is_aka else 0)
        else:
            return self.kuro.value < other.kuro.value

    def __str__(self):
        return shu_name[self.value]

    @property
    def num(self):
        return self.kuro.num

    @property
    def color(self):
        return self.kuro.color

    @property
    def is_aka(self):
        return shu_is_aka[self.value]

    @property
    def kuro(self):
        if self == PAka.M5A:
            return PKuro.M5
        elif self == PAka.P5A:
            return PKuro.P5
        elif self == PAka.S5A:
            return PKuro.S5
        else:
            return PKuro(self.value)


shu_name = [
    '1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
    '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
    '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
    '東', '南', '西', '北', '白', '発', '中', '5M', '5P', '5S'
]

shu_num = [
    1, 2, 3, 4, 5, 6, 7, 8, 9,
    1, 2, 3, 4, 5, 6, 7, 8, 9,
    1, 2, 3, 4, 5, 6, 7, 8, 9,
    1, 2, 3, 4, 5, 6, 7, 5, 5, 5
]

shu_color = [
    1, 1, 1, 1, 1, 1, 1, 1, 1,
    2, 2, 2, 2, 2, 2, 2, 2, 2,
    3, 3, 3, 3, 3, 3, 3, 3, 3,
    4, 4, 4, 4, 4, 4, 4, 1, 2, 3
]

shu_is_aka = [
    False, False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, True, True, True
]


def aka2kuro_and_count(pakas: List[PAka]) -> Tuple[List[PKuro], int]:
    """
    赤牌を黒牌に変換して赤牌の枚数を返す
    """
    pkuros = []
    count = 0
    for paka in pakas:
        if paka == PAka.M5A:
            pkuros.append(PKuro.M5)
            count += 1
        elif paka == PAka.P5A:
            pkuros.append(PKuro.P5)
            count += 1
        elif paka == PAka.S5A:
            pkuros.append(PKuro.S5)
            count += 1
        else:
            pkuros.append(PKuro(paka.value))
    return pkuros, count


# def kuro2aka(pkuro: PKuro) -> PAka:
#     if pkuro == PAka.M5:
#         paka = PAka.M5A
#     elif pkuro == PAka.P5:
#         paka = PAka.P5A
#     elif pkuro == PAka.S5:
#         paka = PAka.S5A
#     else:
#         assert False, str(pkuro) + " is not aka"
#     return paka


#
# 風の定義
#

class Kaze(enum.IntEnum):
    """
    風
    """
    TON = 0  # 東
    NAN = 1  # 南
    SHA = 2  # 西
    PE = 3  # 北

    def __str__(self):
        return kaze_name[self.value]

    @property
    def pkuro(self) -> PKuro:
        return PKuro(PKuro.TON+self.value)

    @property
    def paka(self) -> PAka:
        return PAka(PKuro.TON+self.value)


kaze_name = ['東', '南', '西', '北']
