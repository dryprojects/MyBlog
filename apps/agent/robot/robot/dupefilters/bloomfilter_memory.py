#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      bloomfilter_memory.py 
@time:      2018/08/31 
"""

import math

import mmh3
import bitarray


class BloomFilter:
    def __init__(self, n, f, block_num=1):
        """
        m:
            number of bit as least to be assign
        k:
            number of hash as least need
        :param n: number of items is going to add
        :param f: expected false positive probability
        :param block_num: number of bitarray obj, one block maxsize 16Gb on 32 bit systems
        """
        if not (0 < f < 1):
            raise ValueError("f must be between 0 and 1.")

        if not n > 0:
            raise ValueError("n must be > 0")

        self.n = n
        self.f = f
        self.k = math.ceil(math.log(1.0 / f, 2))
        self.m = math.ceil(-self.k / math.log(1 - math.exp(math.log(f) / self.k)) * n)
        self.block_num = block_num

        self.store = {i: bitarray.bitarray(self.m, endian='little') for i in range(self.block_num)}
        for el in self.store.values():
            el.setall(False)

    def __contains__(self, item):
        item = str(item)

        flag = True
        for seed in range(self.k):
            offset = mmh3.hash(item, seed, signed=False)
            flag = flag & self.store[offset % self.block_num][offset % self.m]

        return True if flag else  False

    def add(self, item):
        item = str(item)

        for seed in range(self.k):
            offset = mmh3.hash(item, seed, signed=False)
            self.store[offset % self.block_num][offset % self.m] = 1

if __name__ == "__main__":
    bf = BloomFilter(100000000, 0.0001, block_num=2)

    test_str = ["python", "c", "c++", "ruby", 1, 2, 3]

    for el in test_str:
        bf.add(el)

    print(list(map(lambda _: _ in bf, ['lua', 'python', 'go', 'c', 4, 2, 1])))  # [False, True, False, True, False, True, True]