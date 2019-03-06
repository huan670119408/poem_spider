import scrapy
from poem_spider.items import PoemItem, PoetItem
import re
import uuid


class PoemSpider(scrapy.Spider):
    name = "poem"
    poet_count = 1
    poem_count = 1

    """
    用于记录某个诗人所有诗词的总页数
    例如https://so.gushiwen.org/authors/authorvsw_515ea88d1858A30.aspx 没有到最后一页确展示空无法请求下一页 此时请求下下一页
    """
    poet_total_dict = {}

    def start_requests(self):
        """
        这个网站诗词列表里实际有大量重复的诗词
        """
        base_url = 'https://so.gushiwen.org/search.aspx?type=author&value='
        poets = ['李白', '杜甫', '白居易']
        for poet in poets:
            url = base_url + poet
            yield scrapy.Request(url=url, callback=self.parse_poem_url)

    def parse_poem_url(self, response):
        count = self.settings.get('COUNT')
        if self.poem_count > count:
            return
        poem_detail = response.xpath(
            '//div[@class="main3"]/div[@class="left"]/div[@class="sonspic"]/div[@class="cont"]/p[2]/a/@href').extract_first()
        poem_detail = response.urljoin(poem_detail)
        yield scrapy.Request(url=poem_detail, callback=self.parse_poem)

    def parse_poem(self, response):
        current_page = response.xpath('//form/div/label[@id="temppage"]/text()').extract_first()
        author = response.xpath(
            '//div[@class="main3"]/div[@class="left"]/div[@class="title"]/h1/text()').extract_first()
        author = author.replace('的诗文全集', '')
        if author not in self.poet_total_dict:
            total_page = response.xpath('//form/div/label[@id="sumPage"]/text()').extract_first()
            if total_page is not None and total_page != '0':
                self.poet_total_dict[author] = total_page
        # elif int(current_page) >= int(self.poet_total_dict[author]):
        #     del self.poet_total_dict[author]
        for sel in response.xpath('//p[@class="source"]/..'):
            title = sel.xpath('p[1]/a/b/text()').extract()
            dynasty = sel.xpath('p[2]/a/text()').extract_first()
            content = sel.xpath('div[@class="contson"]').extract_first()
            pat1 = re.compile('<[^>]+>', re.S)
            content = pat1.sub('', content)  # 去html标签
            item = PoemItem()
            item['id'] = str(uuid.uuid1()).replace('-', '')
            item['title'] = title[0]
            item['dynasty'] = dynasty
            item['author'] = author
            content = re.sub(r'\s+', '', content)  # 去空白符
            item['content'] = content
            yield item
            self.poem_count += 1
        next = response.xpath('//form/div/a[@class="amore"]/@href').extract_first()
        if next is not None and len(next) != 0:
            next = response.urljoin(next)
            yield scrapy.Request(url=next, callback=self.parse_poem)
        else:
            """
            https://so.gushiwen.org/authors/authorvsw_515ea88d1858A30.aspx 个别页数展示异常没有下一页 此时请求下下一页
            """
            current_total_page = self.poet_total_dict[author]
            if int(current_page) < int(current_total_page):
                current_url = response.url
                next = current_url.replace('A' + current_page, 'A' + str(int(current_page) + 1))
                yield scrapy.Request(url=next, callback=self.parse_poem)
