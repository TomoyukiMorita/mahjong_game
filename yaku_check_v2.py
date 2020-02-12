from typing import Any, List, Tuple, Optional
import numpy as np
import random
import enum
import copy

from paidef import Color, PKuro, Kaze
from blockdef import Block

#
# 上がり形から役をチェックする
#
#
#


yaku_state_initial = dict(reach=False, ippatsu=False, tsumo=False, jikaze=False, bakaze=False, haku=False, hatsu=False,
                          chun=False, tanyao=False, pinhu=False,
                          ipeko=False, haiteitsumo=False, haiteiron=False, rinshan=False, daburi=False,
                          sanshokudojun=False, sanshokudoko=False, sananko=False, ittsu=False,
                          chinitsu=False, toitoi=False, chanta=False, sankantsu=False, honitsu=False, ryanpeko=False,
                          junchan=False, chitoitsu=False, shosangen=False, honroto=False, renho=False,
                          suanko=False, daisangen=False, kokushi=False, ryuiso=False, tsuiso=False, chinroto=False,
                          sukantsu=False, shosushi=False, daisusi=False, churen=False, chiho=False, tenho=False)

han_menzen = dict(reach=1, ippatsu=1, tsumo=1, jikaze=1, bakaze=1, haku=1, hatsu=1, chun=1, tanyao=1, pinhu=1,
                  ipeko=1, haiteitsumo=1, haiteiron=1, rinshan=1, daburi=2, sanshokudojun=2, sanshokudoko=2, sananko=2,
                  ittsu=2,
                  toitoi=2, chanta=2, sankantsu=2, chitoitsu=2, shosangen=2, honroto=2, honitsu=3, ryanpeko=3,
                  junchan=3, chinitsu=6, renho=6,
                  suanko=13, daisangen=13, kokushi=13, ryuiso=13, tsuiso=13, chinroto=13, sukantsu=13, shosushi=13,
                  daisusi=13, churen=13, chiho=13, tenho=13)

han_naki = dict(reach=0, ippatsu=0, tsumo=0, jikaze=1, bakaze=1, haku=1, hatsu=1, chun=1, tanyao=1, pinhu=0,
                ipeko=0, haiteitsumo=1, haiteiron=1, rinshan=1, daburi=0, sanshokudojun=1, sanshokudoko=2, sananko=2,
                ittsu=1,
                toitoi=2, chanta=1, sankantsu=2, chitoitsu=0, shosangen=2, honroto=2, honitsu=2, ryanpeko=2, junchan=2,
                chinitsu=5, renho=6,
                suanko=13, daisangen=13, kokushi=13, ryuiso=13, tsuiso=13, chinroto=13, sukantsu=13, shosushi=13,
                daisusi=13, churen=13, chiho=13, tenho=13)

yaku_name = dict(reach="立直", ippatsu="一発", tsumo="門前清自摸和", jikaze="自風", bakaze="場風", haku="白", hatsu="発", chun="中",
                 tanyao="断么九", pinhu="平和",
                 ipeko="一盃口", haiteitsumo="海底摸月", haiteiron="河底撈魚", rinshan="嶺上開花", daburi="両立直", sanshokudojun="三色同順",
                 sanshokudoko="三色同刻", sananko="三暗刻", ittsu="一気通貫",
                 chinitsu="清一色", toitoi="対々和", chanta="混全帯么九", sankantsu="三槓子", ryanpeko="二盃口", junchan="純全帯么九",
                 chitoitsu="七対子", shosangen="小三元", honroto="混老頭", honitsu="混一色", renho="人和",
                 suanko="四暗刻", daisangen="大三元", kokushi="国士無双", ryuiso="緑一色", tsuiso="字一色", chinroto="清老頭",
                 sukantsu="四槓子", shosushi="小四喜", daisusi="大四喜", churen="九蓮宝燈", chiho="地和", tenho="天和")

machi_state_initial = dict(ryanmen=False, tanki=False, kanchan=False, penchan=False, shabo=False, pinhu=False)

dora_nums_initial = dict(dora_omote=0, dora_ura=0, dora_aka=0)
dora_name = dict(dora_omote="表ドラ", dora_ura="裏ドラ", dora_aka="赤ドラ")


class AgariState:  # 上がり状態
    can_agari: bool  # 上がれるかどうか
    is_tsumo : bool # ツモアガリかどうか
    yaku_state: dict  # 役の状態
    han: int  # 飜数
    hu: int  # 符
    ten: int  # 点数
    pay_oya: Optional[int]  # 親の支払い(ツモの場合)
    pay_ko: Optional[int]  # 子の支払(ツモの場合)
    name: str  # 名前
    han_wo_dora: int  # 飜数（ドラを除く）
    dora_nums: dict  # ドラの枚数（辞書）

    def __init__(self):
        self.can_agari = False
        self.is_tsumo = True
        self.yaku_state = yaku_state_initial
        self.han = 0
        self.hu = 0
        self.ten = 0
        self.pay_oya = 0
        self.pay_ko = 0
        self.name = ""
        self.han_wo_dora = 0
        self.dora_nums = dora_nums_initial


class State4YakuCheck:
    class Agari_type(enum.IntEnum):
        NORMAL = 0  # 普通手
        KOKUSHI = 1  # 国士無双
        CHITOI = 2  # 七対 (二盃口は一般とする)

    def __init__(self):
        self.isOya = False
        self.isMenzen = True
        self.isReach = False
        self.isDaburi = False
        self.isTsumoing = False
        self.isIppatsu = False
        self.isHaiteitsumo = False
        self.isHaiteiron = False
        self.isRinshan = False
        self.isTenho = False
        self.isChiho = False
        self.isRenho = False
        self.bakaze = Kaze.TON
        self.jikaze = Kaze.TON
        self.doras_omote = []
        self.doras_ura = []
        self.agari_type = State4YakuCheck.Agari_type.NORMAL
        self.nAka = 0  # 赤ドラの枚数


def get_ketame(n, k):  # 数字nのk桁目(10**kの位)を取得する
    return np.mod((n / 10 ** k), 10).astype(np.int)


# 切り上げ
def roundup(x, k):
    return np.ceil(x / 10 ** (-k)) * 10 ** (-k)


# 手牌が上がれるか判定する
# tehai
# agari_type : 上がりのタイプ 0:一般 1:国士 2:七対 (二盃口は一般とする)
def yaku_check_max(pais: List[PKuro], tsumo: PKuro, blockss: List[List[Block]], state4yc: State4YakuCheck, nAka: int) -> AgariState:
    dora_nums = count_doras(pais, state4yc, nAka)

    agari_state_max = AgariState()
    for blocks in blockss:
        agari_state = calc_tensu_blocks(pais, tsumo, blocks, dora_nums, state4yc)
        if agari_state.can_agari:
            if agari_state.ten > agari_state_max.ten:
                agari_state_max = agari_state

    return agari_state_max


# 点数計算
def calc_tensu_blocks(pais: List[PKuro], tsumo: PKuro, blocks: List[Block], dora_nums: dict,
                      state4yc: State4YakuCheck) -> AgariState:
    machi_state = find_machikei(blocks, tsumo, state4yc.bakaze, state4yc.jikaze, state4yc.isMenzen)
    yaku_state = find_yaku(pais, blocks, machi_state, state4yc)
    han, han_wo_dora = count_han(yaku_state, state4yc.isMenzen, dora_nums)
    hu = hukeisan(blocks, machi_state, state4yc)
    ten, payKo, payOya, name = calc_tensu_from_hu(hu, han, state4yc.isOya, state4yc.isTsumoing)
    canAgari = (han_wo_dora >= 1)  # 1翻縛りで上がれるかどうか

    agari_state = AgariState()
    agari_state.can_agari = canAgari
    agari_state.is_tsumo = state4yc.isTsumoing
    agari_state.yaku_state = yaku_state
    agari_state.han = han
    agari_state.hu = hu
    agari_state.ten = ten
    agari_state.pay_oya = payOya
    agari_state.pay_ko = payKo
    agari_state.name = name
    agari_state.han_wo_dora = han_wo_dora
    agari_state.dora_nums = dora_nums
    return agari_state


def calc_tensu_from_hu(hu: int, han: int, isOya: bool, isTsumo: bool) -> Tuple[int,  Optional[int], Optional[int], str]:
    pay_ko : Optional[int]= None
    pay_oya : Optional[int] = None

    if han >= 13:
        ten0 = 32000
        name = '役満'
    elif han >= 11:
        ten0 = 24000
        name = '三倍満'
    elif han >= 8:
        ten0 = 16000
        name = '倍満'
    elif han >= 6:
        ten0 = 12000
        name = '跳満'
    elif han >= 5 or (han == 4 and hu >= 40) or (han == 3 and hu >= 80):
        ten0 = 8000
        name = '満貫'
    else:
        ten0 = hu * 16 * 2 ** han
        name = ''

    if not isOya:  # 子の点数
        ten_ron = roundup(ten0, -2)
        if not isTsumo:  # ロン
            ten = ten_ron
        else:  # ツモ
            pay_oya = roundup(ten_ron / 2, -2)
            pay_ko = roundup(pay_oya / 2, -2)
            ten = pay_oya + pay_ko * 2

    else:  # 親の点数
        ten_ron = roundup(ten0 * 1.5, -2)
        if not isTsumo:  # ロン
            ten = ten_ron
        else:  # ツモ
            pay_ko = roundup(ten_ron / 3, -2)
            ten = pay_ko * 3

    return ten, pay_ko, pay_oya, name


def count_han(yaku_state, isMenzen: bool, dora_nums: dict) -> Tuple[int, int]:  # 飜数を数える
    han_wo_dora = 0
    for key in yaku_state.keys():
        if yaku_state[key]:
            if isMenzen:
                han_wo_dora += han_menzen[key]
            else:
                han_wo_dora += han_naki[key]
    n_dora_sum = dora_nums["omote"] + dora_nums["aka"] + dora_nums["ura"]
    han = han_wo_dora + n_dora_sum
    return han, han_wo_dora


def find_machikei(blocks: List[Block], tsumo: PKuro, bakaze: Kaze, jikaze: Kaze, isMenzen: bool) -> dict:
    tsumo_color = tsumo.color
    tsumo_num = tsumo.num

    machi_state = copy.deepcopy(machi_state_initial)

    bcodes_tsumocolor = [b.block_code % 100 for b in blocks if (b.color == tsumo_color) and not b.isSarashi]

    isCanRyanmen = False
    isCanKanchan = False
    isCanPenchan = False
    isCanShabo = False
    isCanTanki = False

    if tsumo_color == Color.JIHAI:  # ツモハイが字牌のとき
        if 40 + tsumo_num in bcodes_tsumocolor:
            machi_state["shabo"] = True
        if 10 + tsumo_num in bcodes_tsumocolor:
            machi_state["tanki"] = True
    else:  # ツモハイが字牌ではないとき
        if tsumo_num == 1:
            if 51 in bcodes_tsumocolor:
                isCanRyanmen = True
        if tsumo_num == 2:
            if 51 in bcodes_tsumocolor:
                isCanKanchan = True
            if 52 in bcodes_tsumocolor:
                isCanRyanmen = True
        if tsumo_num == 3:
            if 51 in bcodes_tsumocolor:
                isCanPenchan = True
            if 52 in bcodes_tsumocolor:
                isCanKanchan = True
            if 53 in bcodes_tsumocolor:
                isCanRyanmen = True
        if tsumo_num in np.array([4, 5, 6]):
            if 50 + tsumo_num in bcodes_tsumocolor:
                isCanRyanmen = True
            if 50 + tsumo_num - 1 in bcodes_tsumocolor:
                isCanKanchan = True
            if 50 + tsumo_num + 2 in bcodes_tsumocolor:
                isCanRyanmen = True
        if tsumo_num == 7:
            if 57 in bcodes_tsumocolor:
                isCanPenchan = True
            if 56 in bcodes_tsumocolor:
                isCanKanchan = True
            if 55 in bcodes_tsumocolor:
                isCanRyanmen = True
        if tsumo_num == 8:
            if 57 in bcodes_tsumocolor:
                isCanKanchan = True
            if 56 in bcodes_tsumocolor:
                isCanRyanmen = True
        if tsumo_num == 9:
            if 59 in bcodes_tsumocolor:
                isCanRyanmen = True
        if 40 + tsumo_num in bcodes_tsumocolor:
            isCanShabo = True
        if 10 + tsumo_num in bcodes_tsumocolor:
            isCanTanki = True

        # ピンフになるかどうか判定。
        if isMenzen and isCanRyanmen \
                and sum([b.calc_hu(bakaze, jikaze) for b in blocks]) == 0:
            machi_state["pinhu"] = True
            machi_state["ryanmen"] = True
        else:  # ピンフにならない場合は愚形を優先する
            if isCanTanki:
                machi_state["tanki"] = True
            elif isCanKanchan:
                machi_state["kanchan"] = True
            elif isCanPenchan:
                machi_state["penchan"] = True
            elif isCanShabo:
                machi_state["shabo"] = True
            elif isCanRyanmen:
                machi_state["ryanmen"] = True

    return machi_state


# 上がり形から役をチェックする
def find_yaku(pais: List[PKuro], blocks: List[Block], machi_state: dict, state4yc: State4YakuCheck) -> dict:
    yaku_state = copy.deepcopy(yaku_state_initial)

    color = [pai.color for pai in pais]
    num = [pai.num for pai in pais]

    mentsus = [b.block_code for b in blocks if b.kind in [Block.KIND.KOHTSU, Block.KIND.SHUNTSU]]
    toitsu = [b.block_code for b in blocks if b.kind == Block.KIND.TOITSU][0]

    # 手牌の形以外から決まる役
    if state4yc.isDaburi:
        yaku_state["daburi"] = True
    elif state4yc.isReach:
        yaku_state["reach"] = True
    if state4yc.isTsumoing and state4yc.isMenzen:
        yaku_state["tsumo"] = True
    if state4yc.isIppatsu:
        yaku_state["ippatsu"] = True
    if state4yc.isHaiteitsumo:
        yaku_state["haiteitsumo"] = True
    if state4yc.isHaiteiron:
        yaku_state["haiteiron"] = True
    if state4yc.isRinshan:
        yaku_state["rinshan"] = True
    if state4yc.isTenho:
        yaku_state["tenho"] = True
    if state4yc.isChiho:
        yaku_state["chiho"] = True
    if state4yc.isRenho:
        yaku_state["renho"] = True

    # 外部で判定する役
    if machi_state["pinhu"]:  # ピンフ
        yaku_state["pinhu"] = True
    if state4yc.agari_type == State4YakuCheck.Agari_type.KOKUSHI:  # 国士
        yaku_state["kokushi"] = True
        return yaku_state
    elif state4yc.agari_type == State4YakuCheck.Agari_type.CHITOI:  # チートイツ
        yaku_state["chitoitsu"] = True

    # 染め手の判定
    ucolor = np.unique(color)
    if np.size(np.intersect1d(ucolor, np.array([1, 2, 3]))) == 1:  # 染め手かどうか判定
        if Color.JIHAI in ucolor:  # 字牌があれば
            yaku_state["honitsu"] = True
        else:  # 字牌がなければ
            if np.count_nonzero(num == 1) >= 3 and \
                    np.count_nonzero(num == 2) >= 1 and \
                    np.count_nonzero(num == 3) >= 1 and \
                    np.count_nonzero(num == 4) >= 1 and \
                    np.count_nonzero(num == 5) >= 1 and \
                    np.count_nonzero(num == 6) >= 1 and \
                    np.count_nonzero(num == 7) >= 1 and \
                    np.count_nonzero(num == 8) >= 1 and \
                    np.count_nonzero(num == 9) >= 3:  # チューレン
                yaku_state["churen"] = True
            else:
                yaku_state["chinitsu"] = True  # チンイツ

    # 字一色の判定
    if np.all(np.in1d(ucolor, Color.JIHAI)):  # 字牌のみの場合
        yaku_state["tsuiso"] = True

    # 緑一色の判定
    if np.all(np.in1d(pais, np.array([PKuro.S2, PKuro.S3, PKuro.S4, PKuro.S6, PKuro.S8, PKuro.HATSU]))):
        yaku_state["ryuiso"] = True

    # 風牌の判定
    if (441 + state4yc.jikaze) in mentsus:
        yaku_state["jikaze"] = True
    if (441 + state4yc.bakaze) in mentsus:
        yaku_state["bakaze"] = True

    # スーシーホーの判定
    if np.all(np.in1d(np.array([441, 442, 443, 444]), mentsus)):
        yaku_state["daisushi"] = True
    if np.size(np.in1d(np.array([441, 442, 443, 444]), mentsus)) == 3 and \
            np.all(np.in1d(toitsu, np.array([411, 412, 413, 414]))):
        yaku_state["shosushi"] = True

    # 三元牌の判定
    if 445 in mentsus:
        yaku_state["haku"] = True
    if 446 in mentsus:
        yaku_state["hatsu"] = True
    if 447 in mentsus:
        yaku_state["chun"] = True
    if np.all(np.in1d(np.array([445, 446, 417]), blocks)) \
            or np.all(np.in1d(np.array([445, 416, 447]), blocks)) \
            or np.all(np.in1d(np.array([415, 446, 447]), blocks)):
        yaku_state["shosangen"] = True
    elif yaku_state["haku"] and yaku_state["hatsu"] and yaku_state["chun"]:
        yaku_state["daisangen"] = True

    # イーペーコー、二盃口の判定
    if state4yc.isMenzen:
        nPeko = 0
        for men in np.unique(mentsus):
            if np.count_nonzero(mentsus == men) >= 2:  # 同じメンツがあれば
                nPeko += 1
        if nPeko == 1:
            yaku_state["ipeko"] = True
        elif nPeko == 2:
            yaku_state["ryanpeko"] = True

    # 三色ドウコウの判定
    if np.all(np.in1d(np.array([141, 241, 341]), mentsus)) or \
            np.all(np.in1d(np.array([142, 242, 342]), mentsus)) or \
            np.all(np.in1d(np.array([143, 243, 343]), mentsus)) or \
            np.all(np.in1d(np.array([144, 244, 344]), mentsus)) or \
            np.all(np.in1d(np.array([145, 245, 345]), mentsus)) or \
            np.all(np.in1d(np.array([146, 246, 346]), mentsus)) or \
            np.all(np.in1d(np.array([147, 247, 347]), mentsus)) or \
            np.all(np.in1d(np.array([148, 248, 348]), mentsus)) or \
            np.all(np.in1d(np.array([149, 249, 349]), mentsus)):
        yaku_state["sanshokudoko"] = True

    # 三色同順の判定
    if np.all(np.in1d(np.array([151, 251, 351]), mentsus)) or \
            np.all(np.in1d(np.array([152, 252, 352]), mentsus)) or \
            np.all(np.in1d(np.array([153, 253, 353]), mentsus)) or \
            np.all(np.in1d(np.array([154, 254, 354]), mentsus)) or \
            np.all(np.in1d(np.array([155, 255, 355]), mentsus)) or \
            np.all(np.in1d(np.array([156, 256, 356]), mentsus)) or \
            np.all(np.in1d(np.array([157, 257, 357]), mentsus)):
        yaku_state["sanshokudojun"] = True

    # 一気通貫
    if np.all(np.in1d(np.array([151, 154, 157]), mentsus)) or \
            np.all(np.in1d(np.array([251, 254, 257]), mentsus)) or \
            np.all(np.in1d(np.array([351, 354, 357]), mentsus)):
        yaku_state["ittsu"] = True

    # 三暗刻、四暗刻の判定
    nAnko = len([b for b in blocks if not b.isSarashi and (b.kind == Block.KIND.KOHTSU)])
    if nAnko == 3:
        yaku_state["sananko"] = True
    elif nAnko == 4:
        yaku_state["suanko"] = True

    # 三槓子、四槓子の判定
    nKantsu = len([b for b in blocks if b.isSarashi and (
            b.huro_code in [Block.HuroCode.AN_KONG, Block.HuroCode.KA_KONG, Block.HuroCode.MIN_KONG])])
    if nKantsu == 3:
        yaku_state["sankantsu"] = True
    elif nKantsu == 4:
        yaku_state["sankantsu"] = True

    # トイトイ
    if len([b for b in blocks if b.kind == Block.KIND.TOITSU]) == 4:
        yaku_state["toitoi"] = True

    # タンヤオの判定
    if not np.any(np.in1d(pais, np.array(
            [PKuro.M1, PKuro.M9, PKuro.P1, PKuro.P9, PKuro.S1, PKuro.S9, PKuro.TON, PKuro.NAN, PKuro.SHA, PKuro.PE,
             PKuro.HAKU,
             PKuro.HATSU, PKuro.CHUN]))):
        yaku_state["tanyao"] = True

    # 混老頭、チャンタの判定
    if np.all(np.in1d(pais, np.array([PKuro.M1, PKuro.M9, PKuro.P1, PKuro.P9, PKuro.S1, PKuro.S9]))):
        yaku_state["chinroto"] = True
    elif np.all(np.in1d(pais, np.array(
            [PKuro.M1, PKuro.M9, PKuro.P1, PKuro.P9, PKuro.S1, PKuro.S9, PKuro.TON, PKuro.NAN, PKuro.SHA, PKuro.PE,
             PKuro.HAKU,
             PKuro.HATSU, PKuro.CHUN]))):
        yaku_state["honroto"] = True
    elif np.all(np.in1d(mentsus, np.array([141, 241, 341, 149, 249, 349, 151, 251, 351, 157, 275, 357]))) and \
            np.all(np.in1d(toitsu, np.array([111, 211, 311, 119, 219, 319]))):
        yaku_state["junchan"] = True
    elif np.all(np.in1d(mentsus, np.array(
            [141, 241, 341, 149, 249, 349, 151, 251, 351, 157, 275, 357, 441, 442, 443, 444, 445, 446, 447]))) and \
            np.all(np.in1d(toitsu, np.array([111, 211, 311, 119, 219, 319, 411, 412, 413, 414, 415, 416, 417]))):
        yaku_state["chanta"] = True

    return yaku_state


def count_doras(tehai: List[PKuro], state4yc: State4YakuCheck, nAka: int) -> dict:
    # ドラ(赤ドラを除く)
    nOmotedora = np.count_nonzero(np.in1d(tehai, state4yc.doras_omote))
    if state4yc.isReach:
        nUradora = np.count_nonzero(np.in1d(tehai, state4yc.doras_ura))
    else:
        nUradora = 0

    dora_nums = dora_nums_initial
    dora_nums["omote"] = nOmotedora
    dora_nums["aka"] = nAka
    dora_nums["ura"] = nUradora  # 表ドラ、赤ドラ、裏ドラ
    return dora_nums


def hukeisan(blocks: List[Block], machi_state: dict, state4yc: State4YakuCheck) -> int:  # 符計算

    if machi_state["pinhu"]:  # ピンフ
        if state4yc.isTsumoing:  # ツモ
            return 20
        else:
            return 30

    elif state4yc.agari_type == State4YakuCheck.Agari_type.KOKUSHI:  # 国士無双
        return 20

    elif state4yc.agari_type == State4YakuCheck.Agari_type.CHITOI:  # チートイツ
        return 25

    elif state4yc.agari_type == State4YakuCheck.Agari_type.NORMAL:  # 普通手

        hu = 20  # フーテイ

        if state4yc.isTsumoing:  # ツモ
            hu += 2
        elif state4yc.isMenzen:  # メンゼンロン
            hu += 10

        # 待ち形の符
        if machi_state["ryanmen"] or machi_state["shabo"]:
            hu += 0
        else:
            hu += 2

        # ブロックの符
        for b in blocks:
            hu += b.calc_hu(state4yc.bakaze, state4yc.jikaze)

        hu = roundup(hu, -1)  # 一の位を切り上げて十の位までにする
        if hu == 20:  # 20符なら30符にする
            hu = 30

        return hu


if __name__ == "__main__":
    pass
