# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrapy.conf import settings
from scrapy import log
from weibo.items import *

class WeiboPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoDBPipeline(object):
    def __init__(self):
        connection = MongoClient(
            host=settings['MONGODB_SERVER'],
            port=settings['MONGODB_PORT']
        )

        if not connection:
            log.msg('db connection failed!')

        db = connection[settings['MONGODB_DB']] # 连接mydb数据库，没有则自动创建
        self.info = db[settings['INFO']] #使用 xxx 集合，没有则自动创建
        self.following = db[settings['FOLLOWING']]
        self.followed = db[settings['FOLLOWED']]

        self.userTable = db[settings['USER']]
        self.relationTable = db[settings['RELATION']]
        self.weiboTable = db[settings['WEIBO']]

    def process_item(self, item, spider):

        if isinstance(item, ProfileItem):
            self.info.insert(dict(item))
        elif isinstance(item, FollowingItem):
            self.following.insert(dict(item))
        elif isinstance(item, FollowedItem):
            self.followed.insert(dict(item))
        elif isinstance(item, UserItem):
            self.userTable.insert(dict(item))
        elif isinstance(item, UserRelationItem):
            self.relationTable.insert(dict(item))
        elif isinstance(item, WeiboItem):
            self.weiboTable.insert(dict(item))
        else:
            log.msg("item 未识别!", level=log.DEBUG, spider=spider)

            return

        log.msg("item  added to MongoDB database!", level=log.DEBUG, spider=spider)

        return item