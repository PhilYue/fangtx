# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FangtianxiaRentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    city_name = scrapy.Field()
    price = scrapy.Field()
    location = scrapy.Field()
    building_type = scrapy.Field()
    building_date = scrapy.Field()
    url = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    property_corp = scrapy.Field()
    developers = scrapy.Field()
    district = scrapy.Field()
    months = scrapy.Field()
    crawl_date = scrapy.Field()
    origin = scrapy.Field()


class RentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    rent_price = scrapy.Field()
    area = scrapy.Field()
    rent_type = scrapy.Field()
    floor = scrapy.Field()
    house_type = scrapy.Field()
    publish_time = scrapy.Field()
    origin = scrapy.Field()
    h_id = scrapy.Field()
    crawl_date = scrapy.Field()