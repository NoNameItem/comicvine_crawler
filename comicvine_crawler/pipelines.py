from .mongo_connection import Connect


class MongoPipeline(object):
    def __init__(self, mongo_url):
        self._mongo_url = mongo_url
        self._mongo_client = None
        self._mongo_collection = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL')
        )

    def open_spider(self, spider):
        self._mongo_client = Connect.get_connection(self._mongo_url)
        self._mongo_collection = self._mongo_client.get_default_database()[spider.name]

    def close_spider(self, spider):
        self._mongo_client.close()

    def process_item(self, item, spider):
        if not item.get("skip"):
            self._mongo_collection.replace_one({"id": item["id"]}, dict(item), upsert=True)
            return {"id": item["id"], "api_detail_url": item["api_detail_url"], "crawl_date": item["crawl_date"],
                    "name": item.get("name")}
        else:
            return item
