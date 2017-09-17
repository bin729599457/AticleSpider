# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from ..items import DoubanBookItem,ArticleItemLoader
from ..utils.common import get_md5
from scrapy.loader import ItemLoader


class DoubanSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = ["book.douban.com"]
    start_urls = ['https://book.douban.com/tag/哲学']

    def parse(self, response):
    # 解析列表页的所有url
        channel_urls=response.xpath('//div[@class="info"]/h2/a/@href').extract()
        for book_url in channel_urls:
            yield Request(url=book_url,meta={"bookUrl":book_url},callback=self.parse_detail)

    # 提取下一页的url并交给scrapy进行下载
        nextLink=response.xpath('//span[@class="next"]/link/@href').extract_first("")
        if nextLink:
            init_url="https://book.douban.com"
            yield Request(url=init_url+nextLink,callback=self.parse)


    def parse_detail(self,response):
        # book_item=DoubanBookItem()

       #提取具体的书本信息
        # publish_str = ".*出版社$"
        # price_str = ".*(\d{1,3}[./]\d{1,3}(元$|$))"
        # publish_time_str =".*(\d{4}[-/年]\d{1,2}([月/-]\d{1,2}|[月/-]$|$))"
        # book_info=response.xpath('//div[@id="info"]/text()').extract()
        #
        # book_url=response.meta.get("bookUrl","")
        # book_img=response.xpath('//a[@class="nbg"]/img/@src').extract_first("")
        # book_type="哲学"
        # book_title=response.xpath('//span[@property="v:itemreviewed"]/text()').extract_first("")
        # book_author=response.xpath('//div[@id="info"]/span/a/text()').extract_first("").strip().replace("\n","")
        # book_context=response.xpath('//div[@class="intro"]').extract_first("").replace("<p>","").replace("</p>","").replace("</div>","").replace('<div class="intro">\n',"").strip()
        # book_point=response.xpath('//strong[@class="ll rating_num "]/text()').extract_first("").strip()
        # book_price=""
        # book_publish_time = "0000-00"
        # book_house = "未知出版社"

        #通过正则表达式匹配对应的书本信息
        # for str in book_info:
        #     str.strip()
        #     if re.match(publish_str, str):
        #         book_house=str
        #     if re.match(price_str, str):
        #         book_price=str.replace("元","").strip()
        #     if re.match(publish_time_str, str):
        #         book_publish_time=str.replace("年","-").replace("月","")

        # try:
        #     book_publish_time=datetime.datetime.strptime(book_publish_time,"%Y%M").date()
        # except Exception as e:
        #     book_publish_time=datetime.datetime.now().date()


        #通过item loader加载item

        book_type = "哲学"
        book_url = response.meta.get("bookUrl", "")

        item_loder=ArticleItemLoader(item=DoubanBookItem(),response=response)
        item_loder.add_value("url",book_url)
        item_loder.add_xpath("title",'//span[@property="v:itemreviewed"]/text()')
        item_loder.add_xpath("img",'//a[@class="nbg"]/img/@src')
        item_loder.add_value("url_object_id",get_md5(response. url))
        item_loder.add_xpath("author",'//div[@id="info"]/a/text()')
        item_loder.add_xpath("publish_time",'//div[@id="info"]/text()')
        item_loder.add_xpath("content",'//div[@class="intro"]')
        item_loder.add_xpath("point",'//strong[@class="ll rating_num "]/text()')
        item_loder.add_value("book_type",book_type)
        item_loder.add_xpath("house",'//div[@id="info"]/text()')
        item_loder.add_xpath("price",'//div[@id="info"]/text()')
        book_item=item_loder.load_item()

        yield book_item


"strip()方法可以去除字符串之间的空格符; replace()替换掉不需要的字符串"