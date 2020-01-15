import datetime
import json

import scrapy

from ..mongo_connection import Connect
# from ..settings_dev import API_KEY


class SpiderImplementationError(Exception):
    pass


class BaseSpider(scrapy.Spider):
    # LIST_URL_PATTERN should contain 3 placeholders: limit, offset and api_key and should not contain filter parameter
    LIST_URL_PATTERN = None
    DETAIL_FIELD_LIST = None
    LIMIT = 100

    def __init__(self, incremental='N', api_key=None, filters=None, **kwargs):
        self.logger.info("incremental: " + incremental)
        if filters is None:
            filters = {}
        if not self.LIST_URL_PATTERN:
            raise SpiderImplementationError(
                'Class `{0.__class__}` should override `LIST_URL_PATTERN`'.format(self)
            )
        super().__init__(**kwargs)
        self.api_key = api_key
        self.filters = filters
        self.incremental = incremental

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.api_key = spider.api_key or spider.settings.get('API_KEY')
        mongo_connection = Connect.get_connection(spider.settings.get("MONGO_URL"))
        spider.logger.info("Spider name: " + spider.name)
        spider.logger.info("API_KEY: " + spider.api_key)
        spider.logger.info("MONGO_URL: " + spider.settings.get("MONGO_URL"))
        mongo_db = mongo_connection.get_default_database()

        if spider.incremental == 'Y':

            spider_info = mongo_db.spider_info.find_one({"name": spider.name})
            spider.logger.info("Spider info: " + str(spider_info))
            if spider_info:
                start_date = str(spider_info.get("last_run_dttm", datetime.datetime.min))
                end_date = str(datetime.datetime.max)
                spider.filters["date_last_updated"] = "{0}|{1}".format(start_date, end_date)

        mongo_db.spider_info.update({"name": spider.name}, {"last_run_dttm": datetime.datetime.now(),
                                                            "name": spider.name}, upsert=True)
        mongo_connection.close()

        return spider

    def start_requests(self):
        url = self.construct_list_url(0)

        yield scrapy.Request(url=url, callback=self.parse_list)

    def construct_list_url(self, offset):
        url = self.LIST_URL_PATTERN.format(**{"api_key": self.api_key, "limit": self.LIMIT, "offset": offset})
        filter_str = ",".join(["{0}:{1}".format(k, v) for k, v in self.filters.items()])
        url += "&filter=" + filter_str
        self.logger.info("List url: " + url)
        return url

    def construct_detail_url(self, url):
        url += "?api_key=" + self.api_key
        url += "&format=json"
        if self.DETAIL_FIELD_LIST:
            url += "&field_list=" + self.DETAIL_FIELD_LIST
        self.logger.info("Detail url: " + url)
        return url

    def parse(self, response):
        pass

    def parse_list(self, response):
        # Parsing json
        json_res = json.loads(response.body)

        # Follow to detail pages
        for entry in json_res.get("results", []):
            detail_url = self.construct_detail_url(entry["api_detail_url"])
            yield scrapy.Request(url=detail_url, callback=self.parse_detail)

        # Follow to next list page
        offset = json_res["offset"]
        number_of_total_results = json_res["number_of_total_results"]
        number_of_page_results = json_res["number_of_page_results"]

        if offset + number_of_page_results < number_of_total_results:
            next_page = self.construct_list_url(offset + number_of_page_results)
            yield scrapy.Request(url=next_page, callback=self.parse_list)

    def parse_detail(self, response):
        item = json.loads(response.body).get("results", {})
        item["crawl_date"] = datetime.datetime.now()
        yield item
