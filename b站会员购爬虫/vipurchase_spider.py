#!/usr/bin/python3.8
# -*- coding:utf-8 -*-
"""
bilibili vip
"""
from DecryptLogin import login
import json
import math
import requests
import time


class Bilibili_spider(object):

    def __init__(self, username, password):
        self.session = Bilibili_spider.login(username, password)
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        }
        self.timeout = 10

    @ staticmethod
    def login(username, password):
        lg = login.Login()
        infos_return, session = lg.bilibili(username, password, 'pc')
        return session

    def vipPurchase(self):
        data = []
        for pid in range(1, 48):  # filter unpurchasable
            start = time.time()
            url = 'https://show.bilibili.com/api/ticket/project/listV2?version=134&page=' + str(pid) + '&pagesize=16&area=-1&filter=&platform=web&p_type=%E5%85%A8%E9%83%A8%E7%B1%BB%E5%9E%8B'
            r = self.session.get(url, headers=self.headers, timeout=self.timeout)
            content = json.loads(r.text)['data']['result']
            gooods = []
            for con in content:
                goods = {}
                goods['project_name'] = con['project_name']
                goods['project_type'] = con['project_type']
                goods['city'] = con['city']
                goods['guest'] = con['guest']
                goods['project_id'] = str(con['id'])
                goods['wish'] = con['wish']
                goods['time'] = con['show_time']
                goods['price_low'] = str(con['price_low'])[:2]
                goods['price_high'] = str(con['price_high'])[:2]
                gooods.append(goods)
            data.extend(gooods)
            end = time.time()
            print('爬取一圈耗时为%s' % (end - start))
        return data

    def vipComments(self):
        data = self.vipPurchase()
        data2 = []
        for goods in data:
            start = time.time()
            temp_url = 'https://show.bilibili.com/api/ticket/comment/alllist?pageNum=1&pageSize=10&subjectId=' + goods['project_id'] + '&subjectName=' + goods['project_name'] + '&subPageSize=3&subjectType=2'
            temp_r = requests.get(temp_url, headers=self.headers, timeout=self.timeout)
            page_count = json.loads(temp_r.text)['data']['commonCount']
            goods['comments'] = page_count

            comment_page_num = math.ceil(int(page_count)/10)
            user_id, user_sex = [], []
            for ppid in range(1, 6):  # reduce
                sec_url = 'https://show.bilibili.com/api/ticket/comment/alllist?pageNum=' + str(ppid) + '&pageSize=10&subjectId=' + goods['project_id'] + '&subjectName=' + goods['project_name'] + '&subPageSize=3&subjectType=2'
                rr = requests.get(sec_url, headers=self.headers, timeout=self.timeout)
                for subject in json.loads(rr.text)['data']['commonList']:
                    user_info = subject['userinfo']
                    user_id.append(user_info['mid'])
                    user_sex.append(user_info['sex'])
            goods['user_id'] = user_id
            goods['user_sex'] = user_sex

            # crawl details in user account
            user_doc = []
            for user in goods['user_id']:
                temp_doc = {}
                de_url = 'https://api.bilibili.com/x/space/bangumi/follow/list?type=1&follow_status=0&pn=1&ps=15&vmid=' + \
                      str(user)
                rrr = requests.get(de_url, headers=self.headers, timeout=self.timeout)
                try:
                    if json.loads(rrr.text)['message'] == '用户隐私设置未公开':
                        temp_doc['collected'] = 'null'
                    else:
                        page_counts = math.ceil(int(json.loads(rrr.text)['data']['total']) // 15)
                        # get comic names
                        comic_infos = []
                        for page in range(1, page_counts+1):
                            dd_url = 'https://api.bilibili.com/x/space/bangumi/follow/list?type=1&follow_status=0&pn=' + str(
                                page) + '&ps=15&vmid=' + str(user)
                            rrrr = requests.get(dd_url, timeout=self.timeout)
                            for li in json.loads(rrrr.text)['data']['list']:
                                comic_info = {}
                                comic_info['comic_title'] = li['title']
                                comic_infos.append(comic_info)
                        temp_doc['collected'] = comic_infos
                except Exception as e:
                    print('抓取收藏漫画信息报错为%s' % e)

                # get subscribed tags
                t_url = 'https://space.bilibili.com/ajax/tags/getSubList?mid=' + str(user)
                rrrrr = requests.get(t_url, headers=self.headers, timeout=self.timeout)
                user_tags = []
                try:
                    if json.loads(rrrrr.text)['status'] == False:
                        temp_doc['tag'] = 'null'
                    else:
                        for tag in json.loads(rrrrr.text)['data']['tags']:
                            user_tags.append(tag['name'])
                        temp_doc['tag'] = user_tags
                except Exception as e:
                    print('抓取标签信息报错为%s' % e)

                user_doc.append(temp_doc)
            goods['user_doc'] = user_doc
            data2.append(goods)
            end = time.time()
            print('爬取一圈耗时为%s' % (end - start))
        return data2

    def save(self, file):
        import codecs
        f = codecs.open(file, 'w+', encoding='utf-8')
        data = self.vipComments()
        f.write(str(data))
        f.flush()
        f.close()


if __name__ == '__main__':
    bi = Bilibili_spider('18860927915', '********')
    bi.save(file="/Users/linjue/Desktop/vipcomment_data.txt")

