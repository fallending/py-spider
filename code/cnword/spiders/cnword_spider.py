# -*- coding: utf-8 -*-

import scrapy
import sqlite3
from cnword.data.cnword import CNWORDS

import os
import os.path
import urllib
import re

class CnwordSpiderSpider(scrapy.Spider):
    name = "cnword_spider"
    url = 'https://hanyu.baidu.com/s?wd={word}&cf=rcmd&t=img&ptype=zici'
    words = CNWORDS
    # words = ['刚']

    # mydb = sqlite3.connect("cnword\/data\/cnword.db")

    def start_requests(self):
        # cursor = self.mydb.cursor()
        # cursor.execute("SELECT zi FROM bw_cnword;")
        # data = cursor.fetchall()
        # print(data)

        for word in self.words:
            yield scrapy.Request(self.url.format(word=word), callback=self.parse_html)

    def file_extension(self, path):
        return os.path.splitext(path)[1]

    def parse_html(self, response):
        name = response.selector.xpath('//body/@data-name').extract_first()

        data_gif = response.selector.xpath('//img[@id="word_bishun"]/@data-gif').extract_first()
        if data_gif:
            extension = self.file_extension(data_gif)
            path = os.path.join('./', (name + extension))

            print('data-gif -> ' + path)

            urllib.request.urlretrieve(data_gif, path)
        else:
            bg_url = response.selector.xpath('//div[@id="header-img"]//div[@class="alter-text"]/@style').extract_first()
            if bg_url:
                # p1 = re.compile(r'[(](.*?)[)]', re.S)  # 最小匹配
                p2 = re.compile(r'[(](.*)[)]', re.S)  # 贪婪匹配
                ret = re.findall(p2, bg_url)
                path = os.path.join('./', (name + '.png'))

                print('bg_url -> ' + ret[0])

                urllib.request.urlretrieve(ret[0], path)

        src = response.selector.xpath('//img[@id="word_bishun"]/@src').extract_first()
        if src and 'http' in src:
            extension = self.file_extension(src)
            path = os.path.join('./', (name + extension))

            print('src -> ' + path)

            urllib.request.urlretrieve(src, path)



