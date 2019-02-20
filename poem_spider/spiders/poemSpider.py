import scrapy
from poem_spider.items import PoemItem
import re


class PoemSpider(scrapy.Spider):
    name = "poem"
    allowed_domains = ["www.gushiwen.org"]
    start_urls = [
        "https://www.gushiwen.org/shiwen/"
    ]
    count = 0

    def parse(self, response):
        if self.count > 10:
            return
        for sel in response.xpath('//p[@class="source"]/..'):
            title = sel.xpath('p[1]/a/b/text()').extract()
            author = sel.xpath('p[2]/a/text()').extract()
            content = sel.xpath('div[@class="contson"]').extract_first()  # 去html标签
            pat1 = re.compile('<[^>]+>', re.S)
            content = pat1.sub('', content)
            # pat2 = re.compile("\'[^\']+\'",re.S)
            # content = pat2.sub("",content)
            item = PoemItem()
            item['title'] = title[0]
            item['dynasty'] = author[0]
            item['author'] = author[1]
            item['content'] = content
            print(item)
        next = response.xpath('//form/div/a[@class="amore"]/@href').extract_first()
        url = response.urljoin(next)
        print(url)
        self.count += 1
        print(self.count)
        yield scrapy.Request(url=url, callback=self.parse)
