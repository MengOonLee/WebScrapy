# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

import json
import hashlib

class GroceriesPipeline:
    def __init__(self):
        self.name_seen = set()
        
    def open_spider(self, spider):
        self.file = open("Groceries.jl", "w")
        
    def close_spider(self, spider):
        self.file.close()
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['name'] in self.name_seen:
            raise DropItem("Duplicate item found: %r" % item)
        else:
            self.name_seen.add(adapter['name'])
            line = json.dumps(adapter.asdict()) + "\n"
            self.file.write(line)
            return item
        
class GroceriesImagesPipeline(ImagesPipeline):
    
    def get_media_requests(self, item, info):
        adapter = ItemAdapter(item)
        image_url = adapter['image_urls']
        yield scrapy.Request(image_url,
            meta={'group': adapter['group'],
                'category': adapter['category'],
                'subcategory': adapter['subcategory'],
                'name': adapter["name"]})
    
    def file_path(self, request, response=None, info=None):
        path = request.meta['group'] + '/' + request.meta['category'] + '/' + \
            request.meta['subcategory'] + '/' + request.meta['name'] + '.jpg'
        return path
    
    def item_completed(self, results, item, info):
        image_path = [x['path'] for ok, x in results if ok]
        if not image_path:
            raise DropItem("Item contains no images")
        adapter = ItemAdapter(item)
        adapter['image_path'] = image_path[0]
        image_checksum = [x['checksum'] for ok, x in results if ok]
        adapter['image_checksum'] = image_checksum[0]
        return item