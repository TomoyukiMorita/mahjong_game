from typing import Any, List, Tuple, Optional
import subprocess
import json

from paidef import PKuro
from blockdef import Block


# シャンテン数
def calc_shanten(pais:List[PKuro]) -> dict:
    cmd = "calc_shanten.exe " + " ".join([str(int(p)) for p in pais])
    # シェルコマンドを実行し、出力文字列を受け取る
    out = (subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            shell=True).communicate()[0]).decode('utf-8')

    dic = json.loads(out)

    shanten_state = {}
    shanten_state["normal"] = dic["shanten"][0]
    shanten_state["kokusi"] = dic["shanten"][1]
    shanten_state["chitoi"] = dic["shanten"][2]
    shanten_state["min"] = min(shanten_state["normal"], shanten_state["kokusi"], shanten_state["chitoi"])
    shanten_state["blockss"] = [[Block(block_code=b + 101) for b in blocks] for blocks in dic["blockss"]]

    return shanten_state


# シャンテン数
def calc_shanten_simple(pais:List[PKuro]) -> List[int]:
    cmd = "calc_shanten_simple.exe " + " ".join([str(int(p)) for p in pais])
    # シェルコマンドを実行し、出力文字列を受け取る
    out = (subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            shell=True).communicate()[0]).decode('utf-8')

    shantens = json.loads(out)

    return shantens


# 有効打牌
def count_yuukou_desc(pais:List[PKuro]) -> dict:
    cmd = "count_yuukou_desc.exe " + " ".join([str(int(p)) for p in pais])
    # シェルコマンドを実行し、出力文字列を受け取る
    out = (subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            shell=True).communicate()[0]).decode('utf-8')

    yuukou_das = json.loads(out)

    return yuukou_das


if __name__ == "__main__":
    import func4debug

    s = func4debug.str2pais("111155559999m55p")

    # das = count_yuukou_desc(s)

    shanten_state = calc_shanten(s)

    print()
