from typing import Any, List, Tuple, Optional, Union
import enum
import random

from paidef import *
from paidef import Kaze
from tehaidef import *
import cppfunc

# 各家のクラス
from tehaidef import Tehai


class Cha:
    pass


class FieldResult:  # 場の結果
    is_agari: bool  # 上がったかどうか
    agari_player_num: int  # 上がったプレイヤーの番号
    agari_state: AgariState  # 上がり役
    ten_move: int  # 点数移動


class Field:  # 場
    chas: List[Cha]
    bakaze: Kaze
    kyoku: int
    honba: int
    num_kyotaku: int
    kan_num: int
    field_result: FieldResult

    def __init__(self, bakaze: Kaze = Kaze.TON, kyoku: int = 1, honba: int = 0, num_kyotaku: int = 0,
                 num_chas: int = 4):
        self.bakaze = bakaze  # 場風
        self.kyoku = kyoku  # 局
        self.honba = honba  # 本場
        self.num_kyotaku = num_kyotaku  # 供託棒の数

        self.tsumoban_num = 0  # 誰のツモ番か

        self.kan_num = 0  # カンされた数

        self.yama = Yama()

        self.dora_state = DoraState(self.yama)

        self.field_result = FieldResult()

        self.chas = []
        haipais = self.yama.haipai()
        for i in range(num_chas):
            cha = Cha(field=self, jikaze=Kaze(i + self.kyoku - 1))
            cha.set_haipai(pais=haipais[i])
            self.chas.append(cha)

    def calc_field_result(self, is_agari: bool, agari_player_num: int = 0) -> FieldResult:
        if is_agari:  # 上がり発生
            self.field_result.is_agari = is_agari
            self.field_result.agari_player_num = agari_player_num
            self.field_result.agari_state = self.chas[self.field_result.agari_player_num].agari_state

            ten_move = []
            if self.field_result.agari_state.is_tsumo:  # ツモアガリ
                for i in range(len(self.chas)):
                    if i == agari_player_num:
                        ten_move.append(self.field_result.agari_state.ten)
                    else:
                        if self.chas[i].isOya:
                            ten_move.append(-self.field_result.agari_state.pay_oya)
                        else:
                            ten_move.append(-self.field_result.agari_state.pay_ko)
            self.field_result.ten_move = ten_move

            return self.field_result

        else:  # 流局
            self.field_result.is_agari = is_agari

            is_tenpais = []
            tenpai_num = 0
            for cha in self.chas:
                is_tenpai = (cha.tehai.shanten_state == 0)
                is_tenpais.append(is_tenpai)
                if is_tenpai:
                    tenpai_num += 1

            ten_move = []
            for is_tenpai in is_tenpais:
                ten = 0
                if is_tenpai:
                    if tenpai_num == 1:
                        ten = 3000
                    elif tenpai_num == 2:
                        ten = 1500
                    elif tenpai_num == 3:
                        ten = 1000
                else:
                    if tenpai_num == 1:
                        ten = -1000
                    elif tenpai_num == 2:
                        ten = -1500
                    elif tenpai_num == 3:
                        ten = -3000
                ten_move.append(ten)
            self.field_result.ten_move = ten_move

            return self.field_result


class Cha:
    field: Field
    ten: int
    tehai: Optional[Tehai]
    agari_state: Optional[AgariState]

    def __init__(self, num: int = 0, field=None, ten: int = 0, jikaze: Kaze = Kaze.TON):
        self.num = num  # 着席順ナンバー(0-3)
        self.field = field  # 場
        self.ten = ten

        self.tehai: Optional[Tehai] = None
        self.isReach: bool = False
        self.isDaburi: bool = False
        self.isMenzen: bool = True
        self.jikaze: Kaze = jikaze
        self.isOya: bool = False
        self.isReaching: bool = False  # 立直宣言して打牌前かどうか（立直宣言後に打牌して初めて立直成立するため）
        self.canReach: bool = False
        self.can_tsumoagari: bool = False
        self.isTsumoing: bool = False
        self.isIppatsu: bool = False
        self.kawa: Kawa = Kawa()
        self.jumme: int = 0
        self.dapais_max: List[PKuro] = []

    def dahai(self, i_select: int):
        if i_select == -1 or self.isReach:  # ツモ切り
            self.kawa.add(self.tehai.sute(-1), self.isReaching)
            self.jumme += 1
        elif i_select in range(len(self.tehai.pais)):  # 手出し
            self.kawa.add(self.tehai.sute(i_select), self.isReaching)
            self.jumme += 1
        else:
            return False

        # 一発を消す(立直確定より前)
        if self.isReach:
            self.isIppatsu = False

        # 立直確定
        if self.isReaching:
            self.isReach = True
            self.isReaching = False
            self.isIppatsu = True

        self.isTsumoing = False

    def tsumo(self):
        self.isTsumoing = True

        # ツモの処理
        tm = self.field.yama.tsumo()
        self.tehai.tsumo(tm)

        # シャン点数の表示他
        self.can_tsumoagari = False
        self.canReach = False
        if self.isMenzen and (not self.isReach) and (not self.isReaching) \
                and self.tehai.shanten_state["min"] in [-1, 0]:
            self.canReach = True
        if self.tehai.shanten_state["min"] == -1:
            self.__get_agari_state()
            if self.agari_state.can_agari:
                self.can_tsumoagari = True

        self.calc_yuuko()

    def reach(self):
        self.canReach = False
        self.isReaching = True

    def tsumoagari(self):
        pass

    def set_haipai(self, pais: List[PAka]):  # 配牌
        self.tehai = Tehai(pais=pais)

    def __get_agari_state(self) -> None:
        state4yc = State4YakuCheck()

        state4yc.isOya = self.isOya
        state4yc.isMenzen = self.isMenzen
        state4yc.isReach = self.isReach
        state4yc.isDaburi = self.isDaburi
        state4yc.isTsumoing = self.isTsumoing
        state4yc.isIppatsu = self.isIppatsu
        state4yc.isHaiteitsumo = self.isTsumoing and (self.field.yama.tsumo_remain == 0)
        state4yc.isHaiteiron = not self.isTsumoing and (self.field.yama.tsumo_remain == 0)
        state4yc.isRinshan = False
        state4yc.isTenho = False
        state4yc.isChiho = False
        state4yc.isRenho = False
        state4yc.bakaze = self.field.bakaze
        state4yc.jikaze = self.jikaze
        state4yc.doras_omote = self.field.dora_state.omotes
        state4yc.doras_ura = self.field.dora_state.uras

        self.agari_state = self.tehai.get_agari_state(state4yc)

    # 有効打牌
    def calc_yuuko(self):
        # シャンテン数
        pakas = list(self.tehai.pais)
        pakas.append(self.tehai.tsumo_pai)
        pkuros, jk = aka2kuro_and_count(pakas)
        yuukou_das = cppfunc.count_yuukou_desc(pkuros)

        counts = [da["uke_sum"] for da in yuukou_das]
        dapais_max = [da["dapai"] for da in yuukou_das if da["uke_sum"] == max(counts)]
        dapais_max.sort()  # 本来は必要ないが、exeでソートされていないため
        self.dapais_max = dapais_max


class Yama:  # 山
    # シャッフルされていない牌
    pai_codes_initial: List[PAka] = [
        PAka.M1, PAka.M1, PAka.M1, PAka.M1,
        PAka.M2, PAka.M2, PAka.M2, PAka.M2,
        PAka.M3, PAka.M3, PAka.M3, PAka.M3,
        PAka.M4, PAka.M4, PAka.M4, PAka.M4,
        PAka.M5, PAka.M5, PAka.M5, PAka.M5A,
        PAka.M6, PAka.M6, PAka.M6, PAka.M6,
        PAka.M7, PAka.M7, PAka.M7, PAka.M7,
        PAka.M8, PAka.M8, PAka.M8, PAka.M8,
        PAka.M9, PAka.M9, PAka.M9, PAka.M9,
        PAka.P1, PAka.P1, PAka.P1, PAka.P1,
        PAka.P2, PAka.P2, PAka.P2, PAka.P2,
        PAka.P3, PAka.P3, PAka.P3, PAka.P3,
        PAka.P4, PAka.P4, PAka.P4, PAka.P4,
        PAka.P5, PAka.P5, PAka.P5, PAka.P5A,
        PAka.P6, PAka.P6, PAka.P6, PAka.P6,
        PAka.P7, PAka.P7, PAka.P7, PAka.P7,
        PAka.P8, PAka.P8, PAka.P8, PAka.P8,
        PAka.P9, PAka.P9, PAka.P9, PAka.P9,
        PAka.S1, PAka.S1, PAka.S1, PAka.S1,
        PAka.S2, PAka.S2, PAka.S2, PAka.S2,
        PAka.S3, PAka.S3, PAka.S3, PAka.S3,
        PAka.S4, PAka.S4, PAka.S4, PAka.S4,
        PAka.S5, PAka.S5, PAka.S5, PAka.S5A,
        PAka.S6, PAka.S6, PAka.S6, PAka.S6,
        PAka.S7, PAka.S7, PAka.S7, PAka.S7,
        PAka.S8, PAka.S8, PAka.S8, PAka.S8,
        PAka.S9, PAka.S9, PAka.S9, PAka.S9,
        PAka.TON, PAka.TON, PAka.TON, PAka.TON,
        PAka.NAN, PAka.NAN, PAka.NAN, PAka.NAN,
        PAka.SHA, PAka.SHA, PAka.SHA, PAka.SHA,
        PAka.PE, PAka.PE, PAka.PE, PAka.PE,
        PAka.HAKU, PAka.HAKU, PAka.HAKU, PAka.HAKU,
        PAka.HATSU, PAka.HATSU, PAka.HATSU, PAka.HATSU,
        PAka.CHUN, PAka.CHUN, PAka.CHUN, PAka.CHUN
    ]

    def __init__(self):
        self.__pais: List[PAka] = random.sample(Yama.pai_codes_initial, len(Yama.pai_codes_initial))  # 牌をシャッフル

        self.__tsumo_num: int = 0
        self.__rinshan_tsumo_num: int = 0

        self.__doras_hyoji_omote_all: List[PAka] = self.__pais[130:121:-2]
        self.__doras_hyoji_ura_all: List[PAka] = self.__pais[131:122:-2]

    @property
    def tsumo_remain(self) -> int:  # ツモの残り数
        return 136 - 14 - self.__tsumo_num - self.__rinshan_tsumo_num

    @property
    def doras_hyoji_omote_all(self) -> List[PAka]:  # ドラ表示牌表全部
        return self.__doras_hyoji_omote_all

    @property
    def doras_hyoji_ura_all(self) -> List[PAka]:  # ドラ表示牌裏全部
        return self.__doras_hyoji_ura_all

    def tsumo(self) -> PAka:  # ツモる
        pai = self.__pais[self.__tsumo_num]
        self.__tsumo_num += 1
        return pai

    def rinshan_tsumo(self) -> PAka:  # リンシャンでツモる
        pai = self.__pais[-1 - self.__rinshan_tsumo_num]
        self.__rinshan_tsumo_num += 1
        return pai

    def haipai(self) -> List[List[PAka]]:  # 配牌
        te = [[], [], [], []]
        idx = [0, 1, 2, 3, 16, 17, 18, 19, 32, 33, 34, 35, 48]
        for i in range(4):
            te[i] = [self.__pais[j + i * 4] for j in idx]
        self.__tsumo_num = 52
        return te


class Kawa:  # 河
    __pais: List[PAka]  # 捨て牌(鳴かれた牌を含める)
    __is_reachs: List[bool]  # 捨て牌が立直宣言牌かどうか
    __is_pickedups: List[bool]  # 捨て牌が鳴かれたかどうか

    def __init__(self):
        self.__pais = []
        self.__is_reachs = []
        self.__is_pickedups = []

    def add(self, pai: PAka, is_reach: bool = False):  # 加える
        self.__pais.append(pai)
        self.__is_reachs.append(is_reach)
        self.__is_pickedups.append(False)

    def pickup(self) -> PAka:  # 拾う
        self.__is_pickedups[-1] = True
        return self.__pais[-1]

    @property
    def pais(self) -> List[PAka]:
        return self.__pais

    @property
    def is_reachs(self) -> List[bool]:
        return self.__is_reachs

    @property
    def is_pickedups(self) -> List[bool]:
        return self.__is_pickedups


class DoraState:  # ドラ情報
    def __init__(self, yama: Yama):
        self.__yama: Yama = yama

        self.dora_num: int = 0  # 表ドラのめくられた数
        self.omotes_hyoji: List[PAka] = []  # 表ドラ表示牌（赤）
        self.uras_hyoji: List[PAka] = []  # 表ドラ表示牌（赤）
        self.omotes: List[PKuro] = []  # 表ドラ（黒）
        self.uras: List[PKuro] = []  # 裏ドラ（黒）
        self.mekuri()

    def mekuri(self) -> None:  # 表ドラ表示牌をめくる
        self.dora_num += 1
        self.omotes_hyoji = self.__yama.doras_hyoji_omote_all[:self.dora_num]
        self.uras_hyoji = self.__yama.doras_hyoji_ura_all[:self.dora_num]
        self.omotes = self.__hyoji2dora(self.omotes_hyoji)
        self.uras = self.__hyoji2dora(self.uras_hyoji)

    @staticmethod
    def __hyoji2dora(pais: List[PAka]) -> List[PKuro]:  # ドラ表示牌からドラの種類を返す
        kuros, nAka = aka2kuro_and_count(pais)
        dora_kuros: List[PKuro] = []
        for kuro in kuros:
            color = kuro.color
            num = kuro.num
            if color == Color.JIHAI:  # 字牌でない場合
                numd = num % 7 + 1  # 数字を1つ足す(7なら1にする)
            else:  # 字牌の場合
                numd = num % 9 + 1  # 数字を1つ足す(9なら1にする)
            dora_kuro = PKuro((color - 1) * 9 + numd - 1)
            dora_kuros.append(dora_kuro)
        return dora_kuros


if __name__ == '__main__':
    pass
