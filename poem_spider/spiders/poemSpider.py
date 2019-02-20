from scrapy.spiders import Spider

class PoemSpider(Spider):
    name = "poem"
    allowed_domains = ["www.gushiwen.org"]
    start_urls = [
        "https://www.gushiwen.org/shiwen/"
    ]

    def parse(self, response):
        for sel in response.xpath('//div[@class="cont"]'):  # contson
            print(sel.extract())
            title = sel.xpath('p[0]').extract()
            author = sel.xpath('p[1]').extract()
            content = sel.xpath('div[@class="contson"]').extract()
            print(title)
            print(author)
            print(content)