# -*- coding: utf-8 -*-

import scrapy


class DominicItem(scrapy.Item):

    number = scrapy.Field()
    initial = scrapy.Field()
    name = scrapy.Field()
    images = scrapy.Field()
    file_name = scrapy.Field()
