# -*- coding: utf-8 -*-
import mysql.connector
from cntv.managedata import formatProName
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class CntvPipeline(object):

    def __init__(self):
        self.conn = mysql.connector.connect(user='root', password='lacom159753', database='smarthome', use_unicode=True)
        self.cursor = self.conn.cursor()
    #将记录插入数据库方法
    def process_item(self, item, spider):
        try:
            self.conn = mysql.connector.connect(user='root', password='lacom159753', database='smarthome', use_unicode=True)
            self.cursor = self.conn.cursor()
            insertSql = 'insert into program(name, chandi, leibie, zhuyan, bianju, daoyan, jianjie) values (%s, %s, %s, %s, %s, %s, %s);'
            #给字典中的数据进行处理，---空格、编码、节目名字后面的括号
            for key in item.keys():
                if key == 'name':
                    item[key][0] = formatProName(item[key][0].strip())
                else:
                    pass
                item[key][0] = item[key][0].strip().encode('utf8')
            #将记录，插入数据库
            self.cursor.execute(insertSql, [item['name'][0], item['chandi'][0], item['leibie'][0], item['zhuyan'][0], item['bianju'][0], item['daoyan'][0], item['jianjie'][0]])
            self.conn.commit()
        except mysql.connector.Error as e:
            print('query error!{}'.format(e))
        finally:
            self.close_db()
        return item
    #查询数据库是否由此记录
    def search(self, proName):
        num = 0
        try:
            self.conn = mysql.connector.connect(user='root', password='lacom159753', database='smarthome', use_unicode=True)
            self.cursor = self.conn.cursor()
            querySql = "select name, zhuyan from program where name = %s"
            self.cursor.execute(querySql, [proName, ])
            self.cursor.fetchall()
            num = self.cursor.rowcount
        except mysql.connector.Error as e:
            print('query error!{}'.format(e))
        finally:
            self.close_db()
        return num
    #关闭数据库相关资源
    def close_db(self):
        self.cursor.close()
        self.conn.close()
