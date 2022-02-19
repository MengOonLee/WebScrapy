import scrapy

class LazadaSpider(scrapy.Spider):
    name = "Lazada"
    start_urls = ['https://www.zyte.com/blog/']

    def parse(self, response):
        for title in response.css('a.oxy-post-title'):
            yield {'title': title.css('::text').get()}
            
        for next_page in response.css('a.next'):
            yield response.follow(next_page, self.parse)
