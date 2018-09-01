#!usr/bin/env python  
# -*- coding:utf-8 -*-

""" 
@author:    nico 
@file:      bloomfilter_redis.py 
@time:      2018/08/31 
"""

import math

import mmh3


class BloomFilter:
    def __init__(self, n, f, server, block_num=1, key_prefix='BLOOMFILTER'):
        """
        m:
            number of bit as least to be assign
        k:
            number of hash as least need
        :param n: number of items is going to add
        :param f: expected false positive probability
        :param server: the redis client instance
        :param block_num: number of redis block, one of block maxsize 512m , 2**32
        :param key_prefix: the block key prefix
        """
        if not (0 < f < 1):
            raise ValueError("f must be between 0 and 1.")

        if not n > 0:
            raise ValueError("n must be > 0")

        self.n = n
        self.f = f
        self.k = math.ceil(math.log(1.0 / f, 2))
        self.m = 1 << 31  # 2**32
        self.server = server
        self.key_prefix = key_prefix
        self.block_num = block_num

    def __contains__(self, item):
        item = str(item)
        key = self.__get_block_route_key(item)
        res = True
        for seed in range(self.k):
            offset = mmh3.hash(item, seed, signed=False)
            res = res & self.server.getbit(key, offset % self.m)

        return True if res else False

    def add(self, item):
        item = str(item)
        key = self.__get_block_route_key(item)
        for seed in range(self.k):
            offset = mmh3.hash(item, seed, signed=False)
            self.server.setbit(key, offset % self.m, 1)

    def __get_block_route_key(self, hashable):
        return self.key_prefix + str(sum(map(ord, hashable)) % self.block_num)


if __name__ == '__main__':
    from redis import StrictRedis

    client = StrictRedis()

    bf = BloomFilter(100000000, 0.0001, client)

    test_str = ["python", "c", "c++", "ruby"]

    for el in test_str:
        bf.add(el)
    print(list(map(lambda _:_ in bf, ['lua', 'python', 'go', 'c']))) # [False, True, False, True]