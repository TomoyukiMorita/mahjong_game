#!/usr/bin/env python
# -*- coding: utf-8 -*-

import enum
import numpy as np

class Kaze(enum.IntEnum): 
    TON = 1 # 東
    NAN = 2 # 南
    SHA = 3 # 西
    PE = 4 # 北

    def __str__(self):
        return kaze_name[self.value]

kaze_name = np.array(['_','東','南','西','北'])

k = Kaze.TON

print(k)
print(str(k))

print(c)


print()