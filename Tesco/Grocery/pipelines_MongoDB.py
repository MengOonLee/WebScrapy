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
import pymongo

class GroceryPipeline:
    
    collection_name = 'Grocery'
    
    def __init__(self, mongo_uri, mongo_db):
        self.name_seen = set()
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )
        
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        
    def close_spider(self, spider):
        self.client.close()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['name'] in self.name_seen:
            raise DropItem("Duplicate item found: %r" % item)
        else:
            self.name_seen.add(adapter['name'])
            self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
            return item

class GroceryImagesPipeline(ImagesPipeline):
    
    def get_media_requests(self, item, info):
        adapter = ItemAdapter(item)
        image_url = adapter['image_urls']
        yield scrapy.Request(image_url,
            meta={'image_name': adapter["name"]})
    
    def file_path(self, request, response=None, info=None):
        return 'Grocery/%s.jpg' % request.meta['image_name']
    
    def item_completed(self, results, item, info):
        image_path = [x['path'] for ok, x in results if ok]
        if not image_path:
            raise DropItem("Item contains no images")
        adapter = ItemAdapter(item)
        adapter['image_path'] = image_path[0]
        image_checksum = [x['checksum'] for ok, x in results if ok]
        adapter['image_checksum'] = image_checksum[0]
        return item
