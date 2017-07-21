# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.contrib.loader.processor import MapCompose, TakeFirst


class WikiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    content = scrapy.Field(
        input_processor=MapCompose()
    )
    page = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    main_category = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    en_main_category = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    category = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    en_category = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    book = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    en_book = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    filename = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    en_title = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    en_sub_category = scrapy.Field(
        input_processor=MapCompose(),
        output_processor=TakeFirst(),
    )
    sub_category = scrapy.Field(
        output_processor=TakeFirst(),
    )
    path = scrapy.Field()
