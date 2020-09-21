# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Join, Identity
from w3lib.html import remove_tags

class GroceryLoader(ItemLoader):
    default_input_processor = MapCompose(remove_tags, str.strip)
    default_output_processor = TakeFirst()
    
def last_str(s):
    return s.split()[-1]

class RiceItem(Item):
    # define the fields for your item here like:
    name = Field()
    currency = Field()
    price = Field()
    legal_disclaim = Field()
    feature = Field()
    product_market = Field()
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
        input_processor=MapCompose(remove_tags, str.strip, last_str))
    unit_specific = Field(
        input_processor=MapCompose(remove_tags, str.strip, last_str))
    image_urls = Field(input_processor=Identity())
    image_path = Field()
    image_checksum = Field()