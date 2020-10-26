# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Join, Identity
from w3lib.html import remove_tags

class GroceriesLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags, str.strip)
    default_output_processor = TakeFirst()
    
def last_str_item(s):
    return s.split()[-1]

class GroceriesItem(Item):
    # define the fields for your item here like:
    product_id = Field()
    group = Field()
    category = Field()
    subcategory = Field()
    name = Field()
    price_unit = Field(output_processor=Join(''))
    price_weight = Field(output_processor=Join(''))
    legal_disclaim = Field()
    feature = Field()
    ingredient = Field()
    product_market = Field()
    brand_market = Field()
    other_info = Field()
    third_party_logo = Field()
    third_party_logo_other_text = Field()
    origin = Field()
    usage = Field(output_processor=Join('\n'))
    storage = Field()
    manufacturer_address = Field(output_processor=Join('\n'))
    distributor_address = Field(output_processor=Join('\n'))
    return_to = Field(output_processor=Join('\n'))
    numeric_size = Field(
        input_processor=MapCompose(remove_tags, str.strip, last_str_item))
    unit_specific = Field(
        input_processor=MapCompose(remove_tags, str.strip, last_str_item))
    number_unit = Field(
        input_processor=MapCompose(remove_tags, str.strip, last_str_item))
    unit_type = Field()
    image_urls = Field(input_processor=Identity())
    image_path = Field()
    image_checksum = Field()
    store = Field()
    available_quantity = Field()