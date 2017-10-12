# coding: utf-8
import re
import datetime
from fangtianxia_rent.items import FangtianxiaRentItem
import scrapy
from lxml import etree
from fangtianxia_rent.spiders.fetch_info import getcity_validate


class FangtianxiaSpider(scrapy.Spider):
    name = 'fangtx'
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
        self.origin = 'FTX'
        self.identify = ''

    def start_requests(self):

        for k, v in self.city_dict.items():
            self.re_start = 0
            self.headers['referer'] = 'https://m.fang.com/fangjia/%s_list_pinggu/' % k
            # 最多100页, 后面的重复
            for i in range(1, 105):
                if self.re_start == 0:
                    url = 'https://m.fang.com/fangjia/?c=pinggu&a=ajaxGetList&city=%s&price=&district=&comarea=&orderby=0&keyword=&x1=&y1=&distance=&from=&r=0.0828841320981899&p=%d' % (
                    k, i)
                    yield scrapy.Request(url=url, headers=self.headers)
                else:
                    break
        '''
        k = 'dg'
        for i in range(1, 5):
            url = 'https://m.fang.com/fangjia/?c=pinggu&a=ajaxGetList&city=%s&price=&district=&comarea=&orderby=0&keyword=&x1=&y1=&distance=&from=&r=0.0828841320981899&p=%d' % (
            k, i)
            yield scrapy.Request(url=url, headers=self.headers)
        '''

    def parse(self, response):
        city_code = re.findall('city=(.*?)&', response.url)[0]
        city_name = self.city_dict[city_code]

        tree = etree.HTML(response.body, parser=etree.HTMLParser(encoding='utf-8'))
        root = tree.xpath('//li/a')

        for elem in root:
            items = FangtianxiaRentItem()
            url = 'https:' + elem.xpath('.//@href')[0]
            # 如果遇到重复的, 就停止循环
            if url == self.identify:
                self.re_start = 1
            name = elem.xpath('.//div[@class="txt"]/h3/text()')[0]
            try:
                price = elem.xpath('.//span[@class="new "]/i/text()')[0]
                price = re.findall('(\d+)', price)[0]
                price = int(price)
                if price < 1000:
                    price = 0
            except:
                price = 0

            items['name'] = name
            items['price'] = price

            items['city_name'] = city_name
            items['url'] = url
            self.identify = url
            yield scrapy.Request(url=url, meta={'items': items}, headers=self.headers, callback=self.parse_comm)

    def parse_comm(self, response):
        items = response.meta['items']
        #content = response.body
        #print content
        tree = etree.HTML(response.body, parser=etree.HTMLParser(encoding='GBK'))
        content = response.body.decode('gbk')
        #print content
        nodes = tree.xpath('//ul[@class="flextablexqN pdY10"]')
        try:
            # building_date = nodes[0].xpath('.//p/text()')[0]
            t1 = u"建筑年代："
            building_date = nodes[0].xpath('.//span[text()="%s"]/following::*[1]/text()' % t1)[0]
        except:
            building_date = ''
        try:
            # building_type = nodes[0].xpath('.//p/text()')[1]
            t2 = u"建筑类型："
            building_type = nodes[0].xpath('.//span[text()="%s"]/following::*[1]/text()' % t2)[0]

        except:
            building_type = ''

        try:
            # property_corp = nodes[0].xpath('.//p/text()')[9]
            # property_corp=nodes[0].xpath('.//span[text()="建筑年代："]/following::*[1]/text()')
            t3 = u"物业公司："
            property_corp = nodes[0].xpath('.//span[text()="%s"]/following::*[1]/text()' % t3)[0]
        except:
            property_corp = ''
        try:
            t4 = u"商："
            # developers = nodes[0].xpath('.//p/text()')[11]
            developers = nodes[0].xpath('.//span[text()="%s"]/following::*[1]/text()' % t4)[0]
        except:
            developers = ''

        try:
            t5 = u"域："
            # district = nodes[0].xpath('.//p/text()')[8]
            district = nodes[0].xpath('.//span[text()="%s"]/following::*[1]/text()' % t5)[0]
        except:
            district = ''
        p = re.compile('markers=(.*?)&')
        try:
            address = tree.xpath('//i[@class="subtt"]/text()')[0]
        except:
            address = ''
        try:
            latitude = p.findall(content)[0].split(',')[1]
            longitude = p.findall(content)[0].split(',')[0]
        except:
            latitude = 0
            longitude = 0

        try:
            months = re.findall(u'(\d+)月参考均价', content)[0]
        except Exception,e :
            print e
            months = '1'

        # 新房信息
        '''
        if len(address) == 0 and len(district) == 0 and len(building_type) == 0:
            try:
                district = tree.xpath('//div[@class="none district"]/text()')[0]
            except:
                district = ''
            try:
                address = tree.xpath('//a[@class="s-arr-rt"]/text()')[0]

                address = address.strip().replace(' ', '')
            except:
                address = ''
        '''
        # 新房信息 不一样的页面结构
        if re.findall('m.fang.com/xf/', response.url):
            try:
                print 'find now house'
                xf_base_url = tree.xpath('//li[@class="moreInfo"]/a/@href')[0]
                xf_url = 'https://m.fang.com' + xf_base_url
                items['latitude'] = latitude
                items['longitude'] = longitude
                #items['months'] = '2017-' + months
                yield scrapy.Request(url=xf_url, headers=self.headers, callback=self.parse_newhouse,
                                     meta={'items': items})
                return
            except:
                return

        items['building_date'] = building_date
        items['building_type'] = building_type
        items['district'] = district
        items['property_corp'] = property_corp
        items['developers'] = developers
        items['latitude'] = latitude
        items['longitude'] = longitude
        items['origin'] = self.origin
        items['months'] = '2017-' + months
        items['crawl_date'] = self.crawl_time
        items['location'] = address
        yield items

    def parse_newhouse(self, response):
        items = response.meta['items']
        content = response.body.decode('gbk')
        #print content
        tree = etree.HTML(response.body, parser=etree.HTMLParser(encoding='GBK'))
        try:
            district = tree.xpath('//div[@class="none district"]/text()')[0]
        except:
            district = ''

        try:
            t1 = u'建筑类型：'
            building_type = tree.xpath('.//span[text()="%s"]/following::*[1]/text()' % t1)[0]
        except:
            building_type = ''

        try:
            t2 = u'商：'
            developers = tree.xpath('.//span[text()="%s"]/following::*[1]/text()' % t2)[0]
        except:
            developers = ''

        try:
            t3 = u'楼盘地址：'
            address = tree.xpath('.//span[text()="%s"]/following::*[1]/a/text()' % t3)[0].strip()
        except:
            address = ''
        try:
            t4 = u'物业公司：'
            property_corp = tree.xpath('.//span[text()="%s"]/following::*[1]/text()' % t4)[0]
        except:
            property_corp = ''
        try:
            t5 = u'开盘时间：'
            open_time = tree.xpath('.//span[text()="%s"]/following::*[1]/text()' % t5)[0]
            building_date = re.findall(u'(\d+)年', open_time)[0]
        except:
            building_date = ''

        try:
            months= re.findall(u'(\d+)月房价', content)[0]
        except:
            months='1'

        items['url'] = response.url
        items['building_date'] = building_date
        items['building_type'] = building_type
        items['district'] = district
        items['property_corp'] = property_corp
        items['developers'] = developers
        items['origin'] = self.origin
        items['crawl_date'] = self.crawl_time
        items['location'] = address
        items['months'] = '2017-' + months
        items['location'] = address
        yield items
