# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from w3lib.html import remove_tags


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def return_value(value):
    return value


def get_author(value):
    str=value.replace("\n","").strip()
    return str

def get_house(value):
    publish_str = ".*出版社$"
    for str in value:
        str.strip()
        if re.match(publish_str, str):
            return str

    return "未知出版社"

def get_publish_time(value):
    publish_time_str = ".*(\d{4}[-/年]\d{1,2}([月/-]\d{1,2}|[月/-]$|$))"
    for str in value:
        str.strip()
        if re.match(publish_time_str, str):
            return str

    return "0000-00"

def get_price(value):
    price_str = ".*(\d{1,3}[./]\d{1,3}(元$|$))"
    for str in value:
        str.strip()
        if re.match(price_str, str):
            return str

    return "未知价格"

def get_context(value):
    str=value.replace("<p>","").replace("</p>","").replace("</div>","").replace('<div class="intro">\n',"").strip()
    return str

class ArticleItemLoader(ItemLoader):
    #自定义ItemLoader
    default_output_processor = TakeFirst()

class DoubanBookItem(scrapy.Item):
    #input_processor 对Item的属性进行预处理
    title=scrapy.Field()
    img=scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    url=scrapy.Field()
    url_object_id=scrapy.Field()
    author=scrapy.Field(
        input_processor=MapCompose(get_author)
    )
    publish_time=scrapy.Field(
        input_processor=MapCompose(get_publish_time)
    )
    house=scrapy.Field(
        input_processor=MapCompose(get_house)
    )
    content=scrapy.Field(
        input_processor=MapCompose(get_context)
    )
    point=scrapy.Field()
    book_type=scrapy.Field()
    price=scrapy.Field(
        input_processor=MapCompose(get_price)
    )


    def get_insert_sql(self):
        insert_sql = """
            insert into douban_book(title,author,img,url,urlObjectId,publishTime,house,content,point,bookType,price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    #参数应确保与数据库中的类型相同
        params = (self["title"], self["author"], self["img"][0],self["url"], self["url_object_id"],
                  self["publish_time"], self["house"], self["content"],
                  self["point"], self["book_type"],self["price"])
        return insert_sql, params

def replace_splash(value):
    return value.replace("/", "")

def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)

def handle_strip(value):
    return value.strip()

class LagouJobItemLoader(ItemLoader):
    #自定义ItemLoader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    #拉勾网职业信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id=scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(replace_splash),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(replace_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(replace_splash),
    )
    job_type = scrapy.Field()
    tags=scrapy.Field(
        input_processor=Join(",")
    )
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=MapCompose(remove_tags,handle_strip),
    )
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags,handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    crawl_time = scrapy.Field()


    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(url_object_id, url,title, salary, job_city, work_years, degree_need,
            job_type, publish_time, job_advantage,tags, job_desc, job_addr, company_name, company_url,crawl_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params=(self["url_object_id"], self["url"], self["title"],self["salary"], self["job_city"], self["work_years"], self["degree_need"],
                  self["job_type"], self["publish_time"], self["job_advantage"],self["tags"], self["job_desc"], self["job_addr"], self["company_name"],
                  self["company_url"],self["crawl_time"])

        return insert_sql, params