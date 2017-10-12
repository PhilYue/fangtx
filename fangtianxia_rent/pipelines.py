# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from models import House,Price,Rent,DBSession
from items import FangtianxiaRentItem,RentItem
class FangtianxiaRentPipeline(object):
    def __init__(self):
        self.session=DBSession()

    def process_item(self, item, spider):
        # 写入小区房价
        if isinstance(item,FangtianxiaRentItem):
            db_house = self.session.query(House).filter(House.house_name == item['name']).filter(
                House.city_name == item['city_name']).first()



            if db_house:
                if db_house.property_corp == u'暂无数据':
                    db_house.property_corp = item['property_corp']

                if db_house.developers == u'暂无数据':
                    db_house.developers = item['developers']

                if db_house.building_date == u'暂无数据':
                    db_house.building_date = item['building_date']

                if db_house.building_date == u'暂无数据':
                    db_house.building_date = item['building_date']

                # 需要添加判断, 以防同一个价格数据插入多次

                p = Price(
                    price=item['price'],
                    origin=item['origin'],
                    months=item['months'],
                    crawl_time=item['crawl_date'],
                    uid=db_house.id
                )
                db_house.price.append(p)

            else:
                house = House(
                    house_name=item['name'],
                    city_name=item['city_name'],
                    url=item['url'],
                    latitude=item['latitude'],
                    longitude=item['longitude'],
                    address=item['location'],
                    building_date=item['building_date'],
                    building_type=item['building_type'],
                    property_corp=item['property_corp'],
                    developers=item['developers'],
                    district=item['district']
                )
                price = Price(
                    price=item['price'],
                    origin=item['origin'],
                    months=item['months'],
                    crawl_time=item['crawl_date']
                )

                house.price.append(price)
                self.session.add(house)

            try:
                self.session.commit()
            except Exception, e:
                print e
                self.session.rollback()
            return item
        # 写入小区租金
        elif (isinstance(item,RentItem)):
            h_id=item['h_id']

            house = self.session.query(House).filter(House.id==h_id).first()
            print house.id
            rent = Rent(
            rent_price = item['rent_price'],
            rent_origin =item['origin'],
            publish_date = item['publish_time'],
            rent_crawl_time = item['crawl_date'],
            rent_type = item['rent_type'],
            house_type = item['house_type'],
            rent_floor = item['floor'],
            rent_url = item['url'],
            rent_title =item['title'],
            rent_area=item['area']

            )

            house.rent_info.append(rent)
            self.session.add(house)

        try:
            self.session.commit()
        except Exception, e:
            print e
            self.session.rollback()
        return item