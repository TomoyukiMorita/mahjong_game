#!/usr/bin/env python
# -*- coding: utf-8 -*-


import numpy as np
import time
import cProfile
from paidef import *
from cppfunc import calc_shanten


def main():

    print("Loading Problems...")

    # data = np.loadtxt("problems/p_normal_10000.txt",delimiter=" ") # 普通
    data = np.loadtxt("problems/p_tin_10000.txt",delimiter=" ") # チンイツ

    prob_shus = []
    prob_shans = []

    for row in data:
        row = row.astype(np.int)
        shus = row[0:14]
        
        prob_shus.append(shus)
        prob_shans.append(row[14:])

    # prob_shans = np.array(prob_shans).tolist()

    print("Loaded " +str(len(prob_shans))+" Problems")

    start_time = time.time()

    nOK =0
    nNG =0

    iProbStart = 0
    nProb = 1000
    # nProb = len(prob_shus) # 問題数=MAX

    print("Solving " +str(nProb)+" Problems")

    for i in range(iProbStart,iProbStart+nProb):
        shus = prob_shus[i]
        shans_answer = prob_shans[i]

        shanten_state = calc_shanten(shus)

        shans_myanswer = np.array([shanten_state["normal"],shanten_state["kokusi"],shanten_state["chitoi"]])

        if all(shans_myanswer == shans_answer):
            nOK +=1
            # print("No"+str(i)+" OK")
        else:
            nNG +=1
            print("No"+str(i)+" NG")

            str_tehai = " ".join([shu_name[shu] for shu in shus])
            strs_blockss = [ "".join(map(str,blocks)) for blocks in shanten_state["blockss"] ]
            print(str_tehai +":"+ str(shans_answer)+":"+str(shans_myanswer) + str(strs_blockss))

    passed_time = time.time() - start_time

    print("OK:" + str(nOK)+",NG:"+str(nNG))
    print("TOTAL TIME:" + "{:.3g}".format(passed_time)+"s")
    print("TIME /Prob:" + "{:.3g}".format(passed_time/nProb*1000)+"ms")


cProfile.run('main()')
# main()