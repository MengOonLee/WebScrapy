import scrapy
import datetime

class GrocerySpider(scrapy.Spider):
    name = 'grocery'
    start_urls = ["https://mydinexpress.my/hypermart/product-category/grocery/"]
    
    def parse(self, response):
        for product in response.xpath('//div[contains(@class, "product-grid-item")]'):
            yield {
                'name': product.css('h3.product-title::text').get(),
                'price': ''.join(product.css('span.price ::text').getall()),
                'datetime': datetime.datetime.now()
            }
            
        for next_page in response.xpath('//div[@class="products-footer"]/a/@href'):
            yield response.follow(next_page, self.parse)
