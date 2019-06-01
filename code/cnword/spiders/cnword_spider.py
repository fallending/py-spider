# -*- coding: utf-8 -*-

import scrapy
import sqlite3
from cnword.data.cnword import CNWORDS

import os
import urllib

class CnwordSpiderSpider(scrapy.Spider):
    name = "cnword_spider"
    url = 'https://hanyu.baidu.com/s?wd={word}&cf=rcmd&t=img&ptype=zici'
    words = CNWORDS
    # words = ['你', '我']

    # mydb = sqlite3.connect("cnword\/data\/cnword.db")

    def start_requests(self):
        # cursor = self.mydb.cursor()
        # cursor.execute("SELECT zi FROM bw_cnword;")
        # data = cursor.fetchall()
        # print(data)

        for word in self.words:
            yield scrapy.Request(self.url.format(word=word), callback=self.parse_html)

    def parse_html(self, response):
        url = response.selector.xpath('//img[@id="word_bishun"]/@data-gif').extract_first()
        if not url:
            return

        name = response.selector.xpath('//body/@data-name').extract_first()
        path = os.path.join('./imgs', (name+'.gif'))

        print(url)
        print(name)
        print(path)

        urllib.request.urlretrieve(url, path)

