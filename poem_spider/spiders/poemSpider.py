import scrapy
from poem_spider.items import PoemItem, PoetItem
import re
import uuid


class PoemSpider(scrapy.Spider):
    name = "poem"
    # allowed_domains = ["www.gushiwen.org"]
    poet_count = 1
    poem_count = 1

    def start_requests(self):
        base_url = 'https://so.gushiwen.org/authors/Default.aspx?p=1&c='
        # dynastys = ['先秦', '两汉', '魏晋', '南北朝', '隋代', '唐代', '五代', '宋代', '金朝', '元代', '明代', '清代', '近现代']
        dynastys = ['先秦', '两汉', '魏晋', '唐代']
        for dynasty in dynastys:
            url = base_url + dynasty
            yield scrapy.Request(url=url, callback=self.parse_poet)

    # def start_requests(self):
    #     base_url = 'https://so.gushiwen.org/authors/Default.aspx?p=1&c=先秦'
    #     yield scrapy.Request(url=base_url, callback=self.parse_poet)

    # start_urls = ['https://so.gushiwen.org/authors/Default.aspx?p=1&c=先秦']
    poem_urls = []

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
            poem_url = sel.xpath('p[2]/a/@href').extract_first()
            poem_url = response.urljoin(poem_url)
            self.poem_urls.append(poem_url)
        next = response.xpath('//form/div/a[@class="amore"]/@href').extract_first()
        if next is not None and len(next) != 0:
            next = response.urljoin(next)
            yield scrapy.Request(url=next, callback=self.parse_poet)
        else:
            for poem_url in self.poem_urls:
                yield scrapy.Request(url=poem_url, callback=self.parse_poem)

    def parse_poem(self, response):
        count = self.settings.get('COUNT')
        if self.poem_count > count:
            return
        for sel in response.xpath('//p[@class="source"]/..'):
            title = sel.xpath('p[1]/a/b/text()').extract()
            author = sel.xpath('p[2]/a/text()').extract()
            content = sel.xpath('div[@class="contson"]').extract_first()
            pat1 = re.compile('<[^>]+>', re.S)
            content = pat1.sub('', content)  # 去html标签
            item = PoemItem()
            item['id'] = str(uuid.uuid1()).replace('-', '')
            item['title'] = title[0]
            item['dynasty'] = author[0]
            item['author'] = author[1]
            content = re.sub(r'\s+', '', content)  # 去空白符
            item['content'] = content
            yield item
            self.poem_count += 1
        next = response.xpath('//form/div/a[@class="amore"]/@href').extract_first()
        if next is not None and len(next) != 0:
            next = response.urljoin(next)
            yield scrapy.Request(url=next, callback=self.parse_poem)
