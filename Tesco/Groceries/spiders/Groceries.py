
import scrapy
from Groceries.items import GroceriesLoader, GroceriesItem

from urllib.parse import urlparse

class GroceriesSpider(scrapy.Spider):
    name = 'Groceries'
    
    start_urls = [
        'https://eshop.tesco.com.my/groceries/en-GB/shop/fresh-food/all',
        'https://eshop.tesco.com.my/groceries/en-GB/shop/grocery/all',
        'https://eshop.tesco.com.my/groceries/en-GB/shop/baby/all'
        'https://eshop.tesco.com.my/groceries/en-GB/shop/chilled-and-frozen/all',
        'https://eshop.tesco.com.my/groceries/en-GB/shop/drinks/all',
        'https://eshop.tesco.com.my/groceries/en-GB/shop/health-and-beauty/all',
        'https://eshop.tesco.com.my/groceries/en-GB/shop/household/all',
        'https://eshop.tesco.com.my/groceries/en-GB/shop/pets/all',
        'https://eshop.tesco.com.my/groceries/en-GB/shop/non-food-and-gifting/all']

    def parse(self, response):
        product_links = response.css('h3 a')
        yield from response.follow_all(product_links, self.parse_product)
        
        pagination_links = response.css('li.pagination-btn-holder a')
        yield from response.follow_all(pagination_links, self.parse)
        
    def parse_product(self, response):
        l = GroceriesLoader(item=GroceriesItem(), response=response)
        
        l.add_value('store', 'Tesco')

        categorys = response.xpath('//span[contains(@class,"beans-link__text")]/text()')\
            .getall()[3:]
        l.add_value('group', categorys[0])
        l.add_value('category', categorys[1])
        l.add_value('subcategory', categorys[2])
        
        l.add_css('name', 'h1.product-details-tile__title::text')
        l.add_xpath('price_unit', "//div[contains(@class, 'price-per-sellable-unit')]//span/text()")
        l.add_xpath('price_weight', "//div[contains(@class, 'price-per-quantity-weight')]//span/text()")
        l.add_xpath('legal_disclaim', '//div[h4="Legal Disclaimers"]/p/text()')
        l.add_xpath('feature', '//div[h4="Features"]/p/text()')
        l.add_xpath('ingredient', '//div[h3="Ingredients"]/div/p/text()')
        l.add_xpath('product_market', '//div[h4="Product Marketing"]/p/text()')
        l.add_xpath('brand_market', '//div[h4="Brand Marketing"]/p/text()')
        l.add_xpath('other_info', '//div[h4="Other Information"]/p/text()')
        l.add_xpath('third_party_logo', '//div[h4="Third Party Logos"]/p/text()')
        l.add_xpath('third_party_logo_other_text', '//div[h4="Third Party Logo Other Text"]/p/text()')
        l.add_xpath('origin', '//div[h4="Origin"]/p/text()')
        l.add_xpath('usage', '//div[h4="Preparation and Usage"]/p/text()')
        l.add_xpath('storage', '//div[h4="Storage"]/p/text()')
        l.add_xpath('manufacturer_address', '//div[h4="Manufacturers Address"]/p/text()')
        l.add_xpath('distributor_address', '//div[h4="Distributor Address"]/p/text()')
        l.add_xpath('return_to', '//div[h4="Return To"]/p/text()')
        l.add_xpath('numeric_size', '//div[h4="Numeric Size"]/p/text()')
        l.add_xpath('unit_specific', '//div[h4="Unit (specific)"]/p/text()')
        l.add_xpath('number_unit', '//div[h4="Number of Units"]/p/text()')
        l.add_xpath('unit_type', '//div[h4="Unit Type"]/p/text()')
        l.add_css('image_urls', 'img::attr(src)')
        
        url = urlparse(response.url).path.split('/')[-1]
        l.add_value('product_id', url)
        
        l.add_value('available_quantity', '1')
        return l.load_item()
