import scrapy
from poem_spider.items import PoemItem, PoetItem
import re
import uuid


class PoetSpider(scrapy.Spider):
    name = "poet"
    # allowed_domains = ["www.gushiwen.org"]
    poet_count = 1

    def start_requests(self):
        start_url = 'https://so.gushiwen.org/authors/Default.aspx?p=1&c=先秦'
        yield scrapy.Request(url=start_url, callback=self.parse_poet)

    def parse_poet(self, response):
        count = self.settings.get('COUNT')
        if self.poet_count > count:
            return
        for sel in response.xpath('//div[@class="sonspic"]/div[@class="cont"]'):
            name = sel.xpath('p/a/b/text()').extract_first()
            introduction = sel.xpath('p[2]/text()').extract_first()
            dynasty = response.xpath('//div[@class="sright"]/span/text()').extract_first()
            item = PoetItem()
            item['id'] = str(uuid.uuid1()).replace('-', '')
            item['name'] = name
            item['introduction'] = introduction
            item['dynasty'] = dynasty
            yield item
            self.poet_count += 1
        next = response.xpath('//div/a[@class="amore"]/@href').extract_first()
        if next is not None and len(next) != 0:
            next = response.urljoin(next)
            yield scrapy.Request(url=next, callback=self.parse_poet)
        else:
            next = response.xpath('//div[@class="sright"]/span/following-sibling::a[1]/@href').extract_first()
            if next is not None and len(next) != 0:
                next = response.urljoin(next)
                yield scrapy.Request(url=next, callback=self.parse_poet)
