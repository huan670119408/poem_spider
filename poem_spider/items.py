# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PoemItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    dynasty = scrapy.Field()
    translation = scrapy.Field()
    form = scrapy.Field()
    content = scrapy.Field()


class PoetItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    dynasty = scrapy.Field()
    introduction = scrapy.Field()