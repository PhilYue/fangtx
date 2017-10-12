# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.conf import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer, Text,ForeignKey
from sqlalchemy import event
from sqlalchemy import DDL
engine = create_engine('mysql+pymysql://root:x@localhost:3306/test?charset=utf8')
DBSession = sessionmaker(bind=engine)
Base = declarative_base()


class House(Base):
    __tablename__ = 'tb_houses'

    id = Column(Integer, primary_key=True)
    house_name = Column(String(80),index=True)
    city_name = Column(String(80),index=True)
    url = Column(String(300),index=True)
    price = relationship('Price',backref='houseinfo')
    rent_info = relationship('Rent',backref='houseinfo')
    latitude = Column(String(50))
    longitude = Column(String(50))
    address = Column(String(300))
    building_date = Column(String(60))
    building_type = Column(String(60))
    property_corp = Column(Text)
    developers = Column(Text)
    district = Column(String(60))

event.listen(
        House.__table__,
        "after_create",
        DDL("ALTER TABLE %(table)s AUTO_INCREMENT = 1000000;")
    )

class Price(Base):
    __tablename__ = 'tb_prices'
    id = Column(Integer, primary_key=True)
    price = Column(Integer)
    origin = Column(String(80),index=True)
    months = Column(String(80))
    crawl_time = Column(DateTime)
    uid= Column(Integer,ForeignKey('tb_houses.id'))

class Rent(Base):
    __tablename__ = 'tb_rents'
    id = Column(Integer, primary_key=True)
    rent_price = Column(Integer,index=True)
    rent_origin = Column(String(80),index=True)
    publish_date = Column(DateTime,index=True)
    rent_crawl_time = Column(DateTime)
    rent_type=Column(String(80))
    house_type=Column(String(80))
    rent_floor = Column(String(80))
    rent_url=Column(String(600))
    rent_title= Column(Text)
    rent_area=Column(String(80))
    uid= Column(Integer,ForeignKey('tb_houses.id'))

Base.metadata.create_all(engine)