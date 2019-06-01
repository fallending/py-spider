# -*- coding: utf-8 -*-


import sys
print (sys.path)

import scrapy
import re
import io
import sys
import json
from scrapy.exceptions import CloseSpider
# from weibo.spi
from ..items import *

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class WeiboSpiderSpider(scrapy.Spider):
    name = "weibo_spider"
    allowed_domains = ["weibo.cn"]
    url = "http://weibo.cn/"

    start_urls = ['louisvuitton']

    # 爬新浪m站：https://m.weibo.cn/u/1259110474）
    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'
    # user_url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}'

    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'

    fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'

    weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'
    # weibo_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid={uid}'

    # start_users = ['1836003984']
    # start_users = ['1916986680']
    # start_users = ['1892475055']
    # start_users = ['2551034310']
    # start_users = ['1924007153']
    # start_users = ['2019842447'] # 还没爬
    # start_users = ['5813211408']
    # start_users = ['1934738161']
    # start_users = ['2826120835']
    # start_users = ['2082922603']
    start_users = ['1912136333']

    task_set = set(start_urls) # 待爬取集合
    tasked_set = set() # 已爬取集合

    def start_requests(self):
        for uid in self.start_users:
            yield scrapy.Request(self.user_url.format(uid=uid), callback=self.parse_user)

    def account_parse(self, response):
        item = response.meta["item"]
        sel = scrapy.Selector(response)
        profile_url = sel.xpath("//div[@class='ut']/a/@href").extract()[1]
        counts = sel.xpath("//div[@class='u']/div[@class='tip2']").extract_first()
        item['id'] = re.findall(u'^/(\d+)/info',profile_url)[0]
        item['tweet_stats'] = re.findall(u'微博\[(\d+)\]', counts)[0]
        item['following_stats'] = re.findall(u'关注\[(\d+)\]', counts)[0]
        item['follower_stats'] = re.findall(u'粉丝\[(\d+)\]', counts)[0]
        if int(item['tweet_stats']) < 4500 and int(item['following_stats']) > 1000 and int(item['follower_stats']) < 500:
            raise CloseSpider("僵尸粉")
        yield scrapy.Request("http://weibo.cn"+profile_url, meta={"item": item},callback=self.profile_parse)

    def profile_parse(self,response):
        item = response.meta['item']
        sel = scrapy.Selector(response)
        info = sel.xpath("//div[@class='tip']/following-sibling::div[@class='c']").extract_first()
        item["profile_pic"] = sel.xpath("//div[@class='c']/img/@src").extract_first()
        item["nick_name"] = re.findall(u'昵称:(.*?)<br>',info)[0]
        item["sex"] = re.findall(u'性别:(.*?)<br>',info) and re.findall(u'性别:(.*?)<br>',info)[0] or ''
        item["location"] = re.findall(u'地区:(.*?)<br>',info) and re.findall(u'地区:(.*?)<br>',info)[0] or ''
        item["birthday"] = re.findall(u'生日:(.*?)<br>',info) and re.findall(u'生日:(.*?)<br>',info)[0] or ''
        item["bio"] = re.findall(u'简介:(.*?)<br>',info) and re.findall(u'简介:(.*?)<br>',info)[0] or ''
        yield item

    def relationship_parse(self, response):
        item = response.meta["item"]
        sel = scrapy.Selector(response)
        uids = sel.xpath("//table/tr/td[last()]/a[last()]/@href").extract()
        new_uids = []
        for uid in uids:
            if "uid" in uid:
                new_uids.append(re.findall('uid=(\d+)&',uid)[0])
            else:
                try:
                    new_uids.append(re.findall('/(\d+)', uid)[0])
                except:
                    print('--------',uid)
                    pass
        item["relationship"].extend(new_uids)
        for i in new_uids:
            if i not in self.tasked_set:
                self.task_set.add(i)
        next_page = sel.xpath("//*[@id='pagelist']/form/div/a[text()='下页']/@href").extract_first()
        if next_page:
            yield scrapy.Request("http://weibo.cn"+next_page, meta={"item": item},callback=self.relationship_parse)
        else:
            yield item


    def parse_weibos(self, response):
        """
        解析微博列表
        :param response: Response对象
        """
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards'):
            weibos = result.get('data').get('cards')
            for weibo in weibos:
                mblog = weibo.get('mblog')
                if mblog:
                    weibo_item = WeiboItem()
                    field_map = {
                        'id': 'id',
                        'attitudes_count': 'attitudes_count',
                        'comments_count': 'comments_count',
                        'reposts_count': 'reposts_count',
                        'picture': 'original_pic',
                        'pictures': 'pics',
                        'created_at': 'created_at',
                        'source': 'source',
                        'text': 'text',
                        'raw_text': 'raw_text',
                        'thumbnail': 'thumbnail_pic',
                    }
                    for field, attr in field_map.items():
                        weibo_item[field] = mblog.get(attr)
                    weibo_item['user'] = response.meta.get('uid')
                    yield weibo_item
            # 下一页微博
            uid = response.meta.get('uid')
            page = response.meta.get('page') + 1
            yield scrapy.Request(self.weibo_url.format(uid=uid, page=page), callback=self.parse_weibos,
                          meta={'uid': uid, 'page': page})

    def parse_user(self, response):
        """
        解析用户信息
        :param response: Response对象
        """
        self.logger.debug(response)
        result = json.loads(response.text)
        if result.get('data').get('userInfo'):
            user_info = result.get('data').get('userInfo')
            user_item = UserItem()
            field_map = {
                'id': 'id',
                'name': 'screen_name',
                'avatar': 'profile_image_url',
                'cover': 'cover_image_phone',
                'gender': 'gender',
                'description': 'description',
                'fans_count': 'followers_count',
                'follows_count': 'follow_count',
                'weibos_count': 'statuses_count',
                'verified': 'verified',
                'verified_reason': 'verified_reason',
                'verified_type': 'verified_type'
            }
            for field, attr in field_map.items():
                user_item[field] = user_info.get(attr)
            yield user_item
            # 关注
            uid = user_info.get('id')
            # yield scrapy.Request(self.follow_url.format(uid=uid, page=1), callback=self.parse_follows,
            #               meta={'page': 1, 'uid': uid})
            # 粉丝
            # yield scrapy.Request(self.fan_url.format(uid=uid, page=1), callback=self.parse_fans,
            #               meta={'page': 1, 'uid': uid})
            # # 微博
            yield scrapy.Request(self.weibo_url.format(uid=uid, page=1), callback=self.parse_weibos,
                          meta={'page': 1, 'uid': uid})

    def parse_follows(self, response):
        """
        解析用户关注
        :param response: Response对象
        """
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and \
                result.get('data').get('cards')[-1].get(
                        'card_group'):
            # 解析用户
            follows = result.get('data').get('cards')[-1].get('card_group')
            for follow in follows:
                if follow.get('user'):
                    uid = follow.get('user').get('id')
                    yield scrapy.Request(self.user_url.format(uid=uid), callback=self.parse_user)

            uid = response.meta.get('uid')
            # 关注列表
            user_relation_item = UserRelationItem()
            follows = [{'id': follow.get('user').get('id'), 'name': follow.get('user').get('screen_name')} for follow in
                       follows]
            user_relation_item['id'] = uid
            user_relation_item['follows'] = follows
            user_relation_item['fans'] = []
            yield user_relation_item
            # 下一页关注
            page = response.meta.get('page') + 1
            yield scrapy.Request(self.follow_url.format(uid=uid, page=page),
                          callback=self.parse_follows, meta={'page': page, 'uid': uid})

    def parse_fans(self, response):
        """
        解析用户粉丝
        :param response: Response对象
        """
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and \
                result.get('data').get('cards')[-1].get(
                        'card_group'):
            # 解析用户
            fans = result.get('data').get('cards')[-1].get('card_group')
            for fan in fans:
                if fan.get('user'):
                    uid = fan.get('user').get('id')
                    yield scrapy.Request(self.user_url.format(uid=uid), callback=self.parse_user)

            uid = response.meta.get('uid')
            # 粉丝列表
            user_relation_item = UserRelationItem()
            fans = [{'id': fan.get('user').get('id'), 'name': fan.get('user').get('screen_name')} for fan in
                    fans]
            user_relation_item['id'] = uid
            user_relation_item['fans'] = fans
            user_relation_item['follows'] = []
            yield user_relation_item
            # 下一页粉丝
            page = response.meta.get('page') + 1
            yield scrapy.Request(self.fan_url.format(uid=uid, page=page),
                          callback=self.parse_fans, meta={'page': page, 'uid': uid})