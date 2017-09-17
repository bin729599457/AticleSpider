# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class BookImagePipeline(ImagesPipeline):
#使用该Pipeline前 应确保 下载的属性参数是list,否则会抛出异常
    def item_completed(self, results, item, info):
        if "img" in item:
            for result,value in results:
                image_file_path=value["path"]
                item["img"]=image_file_path
        return item

#scrapy 连接到MYSQL实例
class MysqlPipeline(object):
    #采用同步机制连接MYSQL
    def __init__(self):
        self.conn=MySQLdb.connect('127.0.0.1','root','root','book_spider',charset="utf8",use_unicode=True)
        self.cursor=self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql="""
            insert into douban_book(title,url,content,img)
            VALUES (%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql,(item["title"],item["url"],item["content"],item["img"]))
        self.conn.commit()

#异步存储数据到MYSQL中
class MysqlTwistedPipeline(object):
    def __init__(self,dbpool):
        self.dbpool=dbpool

    @classmethod
    def from_settings(cls,settings):
        dbparms=dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        #dbpool=adbapi.ConnectionPool("MySQLdb",host=settings["MYSQL_HOST"],db=settings["MYSQL_DBNAME"],user=settings["MYSQL_USER"],passwd=settings["MYSQL_PASSWORD"],)
        dbpool=adbapi.ConnectionPool("MySQLdb",**dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将MYSQL插入变成异步执行
        query=self.dbpool.runInteraction(self.do_insert,item)
        query.addErrorback(self.handle_error)#处理异常

    def handle_error(self,failure):
        #处理异步插入的异常
        print(failure)

    def do_insert(self,cursor,item):
        #执行具体的插入逻辑
        insert_sql,params=item.get_insert_sql()
        cursor.execute(insert_sql,params)

