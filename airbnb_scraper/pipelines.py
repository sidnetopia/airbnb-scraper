# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
import json
import csv
import scrapy


class CSVPipeline:

    def open_spider(self, spider):
        self.file = open('{}.csv'.format(spider.name), 'w', encoding="utf-8")
        self.writer = csv.writer(self.file)
        
        self.written_header = False


    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        def flatten_dict(dictionary, parent_key='', sep='_'):
            items = []
            for key, value in dictionary.items():
                new_key = f"{parent_key}{sep}{key}" if parent_key else key
                if isinstance(value, dict):
                    items.extend(flatten_dict(value, new_key, sep=sep).items())
                elif isinstance(value, scrapy.Item):
                    items.extend(flatten_dict(dict(value), new_key, sep=sep).items())
                else:
                    items.append((new_key, value))
            return dict(items)

        flattened_item = flatten_dict(item)

        if not self.written_header:
            self.writer.writerow(flattened_item.keys())
            self.written_header = True

        self.writer.writerow(flattened_item.values())

        return item


class JsonWriterPipeline:

    def open_spider(self, spider):
        self.file = open(spider.name + '.json', 'w', encoding="utf-8")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):

        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item


class MongoPipeline:

    collection_name = 'listings'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        
        print("\n\n\n", crawler.settings.get('MONGO_URI'), "\n\n\n\n")
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item
