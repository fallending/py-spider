# -*- coding: utf-8 -*-

from scrapy import Item, Field

class ProfileItem(Item):
    """
    账号的微博数、关注数、粉丝数及详情
    """

    collection = 'profiles'

    id = Field()
    nick_name = Field()
    profile_pic = Field()
    tweet_stats = Field()
    following_stats = Field()
    follower_stats = Field()
    sex = Field()
    location = Field()
    birthday = Field()
    bio = Field()

class FollowingItem(Item):
    """
    关注的微博账号
    """

    collection = 'followings'

    id = Field()
    relationship = Field()

class FollowedItem(Item):
    """
    粉丝的微博账号
    """

    collection = 'followeds'

    id = Field()
    relationship = Field()


class UserItem(Item):
    """
    用户表
    """
    collection = 'users'

    id = Field()
    name = Field()
    avatar = Field()
    cover = Field()
    gender = Field()
    description = Field()
    fans_count = Field()
    follows_count = Field()
    weibos_count = Field()
    verified = Field()
    verified_reason = Field()
    verified_type = Field()
    follows = Field()
    fans = Field()
    crawled_at = Field()


class UserRelationItem(Item):
    """
    用户关系表
    """
    collection = 'users'

    id = Field()
    follows = Field()
    fans = Field()


class WeiboItem(Item):
    """
    用户微博条目表
    """
    collection = 'weibos'

    id = Field()
    attitudes_count = Field()
    comments_count = Field()
    reposts_count = Field()
    picture = Field()
    pictures = Field()
    source = Field()
    text = Field()
    raw_text = Field()
    thumbnail = Field()
    user = Field()
    created_at = Field()
    crawled_at = Field()