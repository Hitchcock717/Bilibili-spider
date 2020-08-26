#!/usr/bin/python3.8
# -*- coding:utf-8 -*-
"""
comic analysis
"""

import codecs
import re
import pandas as pd


class ComicAnalysis(object):

    def __init__(self):
        pass

    def read(self, f):
        fin = codecs.open(f, 'r', encoding='utf-8')
        data = []
        for fi in fin.readlines():
            fii = fi.replace(' ', '')
            data.append(fii)
        return data

    def clean(self, f):
        raw_data = self.read(f)
        clean_data = [eval(x) for x in raw_data]
        frequency = []
        for d in clean_data[0]:
            frequency.append(d['id'])
        print('爬取评论总数为%s' % len(frequency))
        count_dict = {}
        for fre in frequency:
            if fre in count_dict:
                count_dict[fre] += 1
            else:
                count_dict[fre] = 1
        sorted_li = sorted(count_dict.items(), key=lambda item: item[1], reverse=True)
        print('参与评论用户总数为%s' % len(sorted_li))
        return clean_data[0], sorted_li

    def discover(self, f):
        data, sort = self.clean(f)[0], self.clean(f)[1]
        core_core_fans, core_fans, new_sort, new_sort_data, left, left_data, left_fans, left_left_fans = [], [], [], [], [], [], [], []
        for tup in sort:
            if tup[1] > 2:  # threshold is set
                new_sort.append(tup)
            else:
                left.append(tup)
        for new in new_sort:
            for d in data:
                if new[0] == d['id']:
                    new_sort_data.append(d)
        for old in left:
            for d in data:
                if old[0] == d['id']:
                    left_data.append(d)
        core_core_fans = self.calculate(new_sort, data, core_fans, core_core_fans)
        left_left_fans = self.calculate(left, data, left_fans, left_left_fans)
        core = len(core_core_fans)
        print('核心动漫用户数为%s' % core)
        secondary = len(new_sort) - len(core_core_fans) + len(left_left_fans)
        print('次核心动漫用户数为%s' % secondary)
        general = len(left) - len(left_left_fans)
        print('泛动漫用户数为%s' % general)
        return new_sort_data, core_core_fans, left_left_fans, left_data, core, secondary, general

    def calculate(self, new_sort, data, core_fans, core_core_fans):
        for core_fan in new_sort:
            for d in data:
                if core_fan[0] == d['id']:
                    core_fans.append(d)
        for core_core in core_fans:
            if core_core.get('collected') and core_core['collected'] != 'null' and len(core_core['collected']) > 10:
                core_core_fans.append(core_core)
        return core_core_fans

    def favorite_comics(self, f):
        total, users, lefts, lefted = self.discover(f)[0], self.discover(f)[1], self.discover(f)[2], self.discover(f)[3]
        for user in users:
            for tol in total:
                if user['id'] == tol['id']:
                    total.remove(tol)
        for left in lefts:
            total.append(left)
            lefted.remove(left)
        core_sorted_li = self.core_loved(users)
        print('核心动漫人群最喜欢看的漫画top10：%s' % core_sorted_li[:10])
        sub_sorted_li = self.core_loved(total)
        print('次动漫人群最喜欢看的漫画top10：%s' % sub_sorted_li[:10])
        low_sorted_li = self.core_loved(lefted)
        print('泛动漫人群最喜欢看的漫画top10：%s' % low_sorted_li[:10])
        return core_sorted_li, sub_sorted_li, low_sorted_li

    def core_loved(self, users):
        loved = []
        for user in users:
            if user.get('collected') and user['collected'] != 'null':
                for collect in user['collected']:
                    loved.append(collect['comic_title'])
        count_dict = {}
        for love in loved:
            if love in count_dict:
                count_dict[love] += 1
            else:
                count_dict[love] = 1
        sorted_li = sorted(count_dict.items(), key=lambda item: item[1], reverse=True)
        return sorted_li


if __name__ == '__main__':
    comic = ComicAnalysis()
    comic.favorite_comics(f='/Users/linjue/Desktop/comic_data.txt')