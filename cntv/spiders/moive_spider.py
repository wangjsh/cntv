# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from cntv.items import CntvItem
from cntv.pipelines import CntvPipeline
from cntv.notifyJava import notifyJava
from cntv.managedata import formatProName, manageJianjie
import time


class MoiveSpider(CrawlSpider):
    name = "cntv"
    allowed_domains = ['dianshiju.cctv.com']
    year = time.strftime('%Y',time.localtime(time.time()))
    start_urls = ['http://dianshiju.cctv.com/list/nf/' + year + '/index.shtml', 'http://dianshiju.cctv.com/list/all/index.shtml']
    #负责操作数据库的一个对象
    pipe = CntvPipeline()
    
    #在电视节目页面中，提取该电视节目的属性信息：演员、导演、编剧......
    def parse_program(self, response):
        sel = Selector(response)
        item = CntvItem()
        item['name'] = sel.xpath('//*[@id="page_body"]/div[3]/div/div[1]/div[1]/div/div[1]/table/tbody/tr/td[3]/table/tbody/tr[1]/td[2]/a/text()').extract()
        item['chandi'] = sel.xpath('//*[@id="page_body"]/div[3]/div/div[1]/div[1]/div/div[1]/table/tbody/tr/td[3]/table/tbody/tr[2]/td[2]/a/text()').extract()
        item['leibie'] = sel.xpath('//*[@id="page_body"]/div[3]/div/div[1]/div[1]/div/div[1]/table/tbody/tr/td[3]/table/tbody/tr[3]/td[2]/a/text()').extract()
        item['zhuyan'] = sel.xpath('//*[@id="page_body"]/div[3]/div/div[1]/div[1]/div/div[1]/table/tbody/tr/td[3]/table/tbody/tr[4]/td[2]/a[1]/text()').extract()
        item['bianju'] = sel.xpath('//*[@id="page_body"]/div[3]/div/div[1]/div[1]/div/div[1]/table/tbody/tr/td[3]/table/tbody/tr[5]/td[2]/a/text()').extract()
        item['daoyan'] = sel.xpath('//*[@id="page_body"]/div[3]/div/div[1]/div[1]/div/div[1]/table/tbody/tr/td[3]/table/tbody/tr[6]/td[2]/a/text()').extract()
        jianjie_str_list = sel.xpath('//td[@class="js"]/script/text()').extract()
        if len(jianjie_str_list) > 0:
            jianjie = jianjie_str_list[0].strip()
            item['jianjie'] = [manageJianjie(jianjie)]
        else:
            item['jianjie'] = ['_null']
        if len(item['name']) == 0 or len(item['zhuyan']) == 0:
            #如果电视节目名和演员名有缺失，则不要此记录
            pass
        else:
            #有时候，网页中电视节目相关信息不完整，我们只要节目名和演员名，其他缺失信息的用_null填充
            for key in item.keys():
                if len(item[key]) == 0:
                    item[key].append('_null')
                else:
                    pass
            return item
    #在start_url中提取电视节目页面的url
    def parse(self,response):
        sel = Selector(response)
        tvinfos = sel.xpath('//div[@class="text"]/h3')
        count = 0#记录新插入的节目总数
        for e in tvinfos:
            name = e.xpath('./a/@title').extract()
            url = e.xpath('./a/@href').extract()
            if len(name) == 0 or len(url) == 0:
                continue
            else:
                proName = formatProName(name[0].strip())
                proUrl = url[0].strip()
                num = self.pipe.search(proName)
                #数据库中没有记录则插入此新纪录
                if num < 1:
                    yield Request(proUrl, callback = self.parse_program)
                    print proName.encode('utf8'), 'new added program'
                    count = count + 1
                else:
                    pass
        print 'the new added program numbers is: ', count
        print 'the number of programs extracted in this page is: ', len(tvinfos)
    
    #closed 方法  判断爬虫结束方式，若完成爬取正常结束，则通知相关建立索引进程数据已经更新，重新建立索引
    def closed(self, reason):
        if reason == "finished":
            print 'scrapy completed crawling, closed. Notify java process to create index_file.'
            notifyJava()
        else:
            print 'scrapy was closed in other ways.'
