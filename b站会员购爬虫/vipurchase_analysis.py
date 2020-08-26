#!/usr/bin/python3.8
# -*- coding:utf-8 -*-
"""
bilibili vip analysis
"""
from pyecharts.charts import Geo, Map
from pyecharts import options as opts
from settings import Settings


class VipPurchase(object):

    def __init__(self):
        pass

    def city(self, f):
        data = Settings().read(f)
        dataa = data[0].split(',')
        sorted_city = Settings().sort(dataa)
        print(sorted_city[:10])
        city, frequency = [], []
        for c in sorted_city:
            city.append(c[0])
            frequency.append(int(c[1]))
        return sorted_city, city, frequency

    def chart(self, f):  # unsupported city map for now
        city, frequency = self.clean(f)[1], self.clean(f)[2]
        data = [[city[i], frequency[i]] for i in range(len(city))]
        map_1 = Map()
        map_1.set_global_opts(
            title_opts=opts.TitleOpts(title="2020年b站会员购商品线下分布"),
            visualmap_opts=opts.VisualMapOpts(max_=100)  # 最大数据范围
        )
        map_1.add("2020年b站会员购商品线下分布", data, maptype="china")
        map_1.render('vip.html')


if __name__ == '__main__':
    vip = VipPurchase()
    vip.time(f="/Users/linjue/Desktop/city_data.txt")