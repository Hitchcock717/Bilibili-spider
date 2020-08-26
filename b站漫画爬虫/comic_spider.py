#!/usr/bin/python3.8
# -*- coding:utf-8 -*-
"""
comic spider
process: 第一页18本漫画书前10页回复的总和
"""
import requests
import json
import math


class ComicSpider(object):

    def __init__(self):
        # requests header
        self.payloadHeader = {
            'Host': 'manga.bilibili.com',
            'Content-Type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        }
        self.timeout = 10

    def get_comic_books(self):
        post_url = 'https://manga.bilibili.com/twirp/comic.v1.Comic/ClassPage?device=pc&platform=web'
        # unknown comic books tolcount
        comic_ids = []
        guess = 2
        for i in range(1, guess):
            data = {
                'area_id': -1,
                'is_finish': -1,
                'is_free': -1,
                'order': 0,
                'page_num': i,
                'page_size': 18,
                'style_id': -1
            }

            r = requests.post(post_url, data=json.dumps(data), headers=self.payloadHeader, timeout=self.timeout)
            r_data = json.loads(r.text)['data']
            for d in r_data:
                # print('漫画书籍id为%s' % d['season_id'])
                comic_ids.append(d['season_id'])
        return comic_ids

    def get_comic_comments(self):
        ids = self.get_comic_books()
        main_members, sub_members = [], []
        """
        :param
        pn: page number
        type: 22
        oid: comic id
        sort: 2
        :return
        {mid,uname,sex}
        """
        # main comments
        for id in ids:
            # request first page to get total page num
            f_url = 'https://api.bilibili.com/x/v2/reply?' + 'pn=' + '1' + '&type=' + '22' + '&oid=' + str(id) + '&sort=' + '2'
            r = requests.get(f_url, timeout=self.timeout)
            tol_page = math.ceil(int(json.loads(r.text)['data']['page']['count']) // 20)
            print('主回复总页数为%s' % tol_page)
            for n in range(3, 10):
                d_url = 'https://api.bilibili.com/x/v2/reply?' + 'pn=' + str(n) + '&type=' + '22' + '&oid=' + str(id) + '&sort=' + '2'
                rr = requests.get(d_url, timeout=self.timeout)
                for reply in json.loads(rr.text)['data']['replies']:
                    main_reply = {}
                    """
                    mid: member id
                    uname: member name
                    sex: member sex
                    """
                    main_reply['id'], main_reply['name'], main_reply['sex'] = reply['member']['mid'], reply['member']['uname'], reply['member']['sex']
                    main_members.append(main_reply)
                    # judge whether main member has subreplies
                    # if subreplies num > 3, folding;
                    # if not, directly display
                    if not reply['replies'] or reply['replies'] == 'null':
                        sub_members = []
                    elif len(reply['replies']) < 3 or reply['rcount'] == 3:
                        for rep in reply['replies']:
                            sub_reply = {}
                            sub_reply['id'], sub_reply['name'], sub_reply['sex'] = rep['member']['mid'], rep['member']['uname'], rep['member']['sex']
                            sub_members.append(sub_reply)
                    else:  # request folding comments
                        sub_members = self.get_comic_subcomments(id, reply['member']['mid'])
        main_members.extend(sub_members)
        return main_members

    def get_comic_subcomments(self, mid, main_mid):
        ff_url = 'https://api.bilibili.com/x/v2/reply?pn=1' + '&type=' + '22' + '&oid=' + str(mid) + '&ps=' + '10' + '&root=' + main_mid
        r = requests.get(ff_url, timeout=self.timeout)
        tol_page = math.ceil(int(json.loads(r.text)['data']['page']['count']) // 10)
        # print('子回复总页数为%s' % tol_page)
        sub_members = []
        for nn in range(1, 2):
            fff_url = 'https://api.bilibili.com/x/v2/reply?pn=' + str(nn) + '&type=' + '22' + '&oid=' + str(mid) + '&ps=' + '10' + '&root=' + main_mid
            rr = requests.get(fff_url, timeout=self.timeout)
            for reply in json.loads(rr.text)['data']['replies']:
                sub_reply = {}
                sub_reply['id'], sub_reply['name'], sub_reply['sex'] = reply['member']['mid'], reply['member']['uname'], reply['member']['sex']
                sub_members.append(sub_reply)
        return sub_members

    def get_collected_comics(self):
        users = self.get_comic_comments()
        user_doc = []
        for user in users:
            url = 'https://api.bilibili.com/x/space/bangumi/follow/list?type=1&follow_status=0&pn=1&ps=15&vmid=' + user['id']
            r = requests.get(url, timeout=self.timeout)
            print(json.loads(r.text))
            try:
                if json.loads(r.text)['message'] == '用户隐私设置未公开':
                    user['collected'] = 'null'
                else:
                    page_count = math.ceil(int(json.loads(r.text)['data']['total']) // 15)
                    # get comic names
                    comic_infos = []
                    for page in range(1, page_count):
                        dd_url = 'https://api.bilibili.com/x/space/bangumi/follow/list?type=1&follow_status=0&pn=' + str(page) + '&ps=15&vmid=' + user['id']
                        rr = requests.get(dd_url, timeout=self.timeout)
                        for li in json.loads(rr.text)['data']['list']:
                            comic_info = {}
                            comic_info['comic_souce'] = li['areas'][0]['name']
                            comic_info['comic_title'] = li['title']
                            comic_infos.append(comic_info)
                    user['collected'] = comic_infos
            except Exception as e:
                print('抓取收藏漫画信息报错为%s' % e)

            # get subscribed tags
            t_url = 'https://space.bilibili.com/ajax/tags/getSubList?mid=' + user['id']
            rrr = requests.get(t_url, timeout=self.timeout)
            user_tags = []
            try:
                if json.loads(rrr.text)['status'] == False:
                    user['tag'] = 'null'
                else:
                    for tag in json.loads(rrr.text)['data']['tags']:
                        user_tags.append(tag['name'])
                    user['tag'] = user_tags
            except Exception as e:
                print('抓取标签信息报错为%s' % e)

            user_doc.append(user)
        print(user_doc)
        return user_doc

    def save(self, file):
        import codecs
        f = codecs.open(file, 'a+', encoding='utf-8')
        data = self.get_collected_comics()
        f.write(str(data))
        f.flush()
        f.close()

    # if you want to crawl more info...
    def get_comic_parts(self):
        # comic_intro
        url = 'https://manga.bilibili.com/twirp/comic.v1.Comic/ComicDetail?device=pc&platform=web'
        data = {
            'comic_id': 25492
        }
        # japan comic rank
        url1 = 'https://manga.bilibili.com/twirp/comic.v1.Comic/HomeHot?device=pc&platform=web'
        data1 = {
            'type': 3
        }
        # recommended comics
        url2 = 'https://manga.bilibili.com/twirp/comic.v1.Comic/MoreRecommend?device=pc&platform=web'
        data2 = {
            'comic_id': 25492
        }

        r = requests.post(url, data=json.dumps(data), headers=self.payloadHeader, timeout=self.timeout)
        print(r.text)


if __name__ == '__main__':
    comic = ComicSpider()
    comic.save(file="/Users/linjue/Desktop/comic_data.txt")

