# coding: utf-8
import re
import datetime
from fangtianxia_rent.items import FangtianxiaRentItem
import scrapy
from lxml import etree
from fangtianxia_rent.items import RentItem
from fangtianxia_rent.spiders.fetch_info import getcity_validate
from fangtianxia_rent.models import House, Price, DBSession


class FangRentSpider(scrapy.Spider):
    name = 'fangtx_rent'
    allowed_domains = ['m.fang.com']

    def __init__(self):
        self.re_start = 0
        self.headers = {'accept-language': 'zh-CN,zh;q=0.8', 'accept-encoding': 'gzip, deflate, br',
                        'x-requested-with': 'XMLHttpRequest', 'accept': '*/*',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
                        'cookie': 'global_cookie=mhf9mmses6ovr76y48gq9jrfj1pj6ekwgdp; Integrateactivity=notincludemc; SoufunSessionID_Esf=3_1503037979_11739; vh_newhouse=1_1503451998_12479%5B%3A%7C%40%7C%3A%5Dbcc17dddf35e886dd3be5d0a8a822358; newhouse_user_guid=671E18B0-D023-C049-0AFB-BD2E31F666A9; showAdsh=1; __jsluid=542d5f8b93b04313bed905bc9085206c; global_wapandm_cookie=7u17sxmhmlxcdue3lchbetnfq2vj7havntp; JSESSIONID=aaaAFYVF5Flzxg-zbf15v; zhcity=%E6%B7%B1%E5%9C%B3; encity=sz; addr=%E5%B9%BF%E4%B8%9C%E7%9C%81%E6%B7%B1%E5%9C%B3; sf_source=; s=; city=sz; unique_cookie=U_kgwjsw4l3h52al5vci7wi3erj17j7haurmv*38; cityHistory=%E6%97%A0%E9%94%A1%2Cwuxi; __utmt_t0=1; __utmt_t1=1; cancellocation=1; swiperIndex=1; __utma=147393320.1104454669.1502861445.1505280538.1505287635.31; __utmb=147393320.51.10.1505287635; __utmc=147393320; __utmz=147393320.1505287635.31.12.utmcsr=sh.fang.com|utmccn=(referral)|utmcmd=referral|utmcct=/; unique_wapandm_cookie=U_7u17sxmhmlxcdue3lchbetnfq2vj7havntp*28; mencity=dg',
                        'pragma': 'no-cache', 'cache-control': 'no-cache'
                        }
        self.crawl_time = datetime.datetime.now().strftime('%Y-%m-%d')
        self.city_dict = getcity_validate()
        self.stop_flag = False
        # self.identify = ''
        self.origin = 'FTX'


    def start_requests(self):
        self.session = DBSession()
        # print self.city_name
        # print type(self.city_name)

        for k,v in self.city_dict.items():
            urls_info = self.session.query(House.id, House.url).join(Price).filter(Price.origin == 'FTX').filter(
            House.url.like('%m.fang.com%')).filter(
            House.city_name == v).all()
            # 从数据库提取小区的url和id
            print 'start.....................'
            req_url = 'https://m.fang.com/zf/?projcodes={}&src=xiaoqu&jhtype=zf&renttype=cz&c=zf&a=ajaxGetList&city={}&page={}'
            if not urls_info:
                print "city not found"
                return
            for url in urls_info:
                try:
                    hostid = re.findall('/(\d+)\.htm', url[1])[0]
                except Exception, e:
                    print e
                    return
                self.stop_flag = False
                for i in range(1, 20):
                    if self.stop_flag:
                        break
                    start_url = req_url.format(hostid, k, i)
                    yield scrapy.Request(url=start_url, headers=self.headers, callback=self.parse_rent_url,
                                     meta={'id': url[0]})

    def parse_rent_url(self, response):
        house_id = response.meta['id']
        tree = etree.HTML(response.body)
        if not tree:
            self.stop_flag = True
            return
        urls = tree.xpath('//li/a/@href')
        urls = map(lambda x: 'https:' + x, urls)
        for url in urls:
            yield scrapy.Request(url=url, meta={'house_id': house_id}, headers=self.headers, callback=self.parse_rent_detail)

    def parse_rent_detail(self, response):
        house_id = response.meta['house_id']
        tree = etree.HTML(response.body, parser=etree.HTMLParser(encoding='gbk'))
        # 判断是否有房子出租, 没有直接退出
        if not tree:
            self.stop_flag = True

        # 有房子出租信息, 获取出租url

        items = RentItem()

        url = response.url

        try:
            title = tree.xpath('//section[@class="xqCaption mb8"]/h1/text()')[0]
        except:
            title=''

        try:
            house_type =  tree.xpath('//div[@class="bb pdY10"]/ul/li/p/text()')[1]
        except:
            house_type=''

        try:
            rent_type = tree.xpath('//div[@class="bb pdY10"]/ul/li/p/text()')[0]
        except:
            rent_type=''

        try:
            rent_price = tree.xpath('//div[@class="price-box mt20"]/p/span/text()')[0]
            # 未知或者非数字的一律转为0
            rent_price = int(rent_price)
        except:
            rent_price = 0

        try:
            area= tree.xpath('//div[@class="bb pdY10"]/ul/li/p/text()')[2]
        except:
            area = ''

        try:
            floor=tree.xpath('//div[@class="bb pdY10"]/ul/li/p/text()')[3]
        except:
            floor=''

        items['title'] = title
        items['url'] = url
        items['rent_price'] = rent_price
        items['rent_type'] = rent_type
        items['house_type'] = house_type
        items['h_id'] = house_id
        items['area'] = area
        items['floor'] = floor
        items['publish_time'] = self.crawl_time
        items['crawl_date'] = self.crawl_time
        items['origin'] = self.origin

        yield items
