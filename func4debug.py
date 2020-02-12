# デバッグ用関数

from paidef import *


# 牌の文字列を牌コードリストに変換する
def str2pais(str_pais: str) -> List[PAka]:
    list_str_pais = list(str_pais)
    pais = []
    nums = []
    for c in list_str_pais:  # 1文字づつ取り出し
        if c in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            nums.append(int(c))
        else:
            color = None
            if c == "m":
                color = Color.MANZU
            elif c == "p":
                color = Color.PINZU
            elif c == "s":
                color = Color.SOHZU
            elif c == "j" or c == "z":
                color = Color.JIHAI
            for num in nums:
                if num == 0:
                    pais.append(PAka(33 + color))
                else:
                    pais.append(PAka.color_num2pai(color, num))
            nums = []
    return pais


if __name__ == "__main__":
    pais = str2pais("479m1399p35s1345z9s")
    print(pais)

    print()
