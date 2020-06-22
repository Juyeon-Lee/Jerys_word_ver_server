# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Article(scrapy.Item):
    """super class"""
    url = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()

'''class newsArticle(scrapy.Item):'''




class News(Article, scrapy.Item):
    """
    child class
    url, title, text, time
    """
    time = scrapy.Field()
