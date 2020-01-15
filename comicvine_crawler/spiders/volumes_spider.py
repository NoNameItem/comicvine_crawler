import datetime
import json

import scrapy

from .base_spider import BaseSpider


class VolumesSpider(BaseSpider):
    # LIST_URL_PATTERN should contain 3 placeholders: limit, offset and api_key and should not contain filter parameter
    LIST_URL_PATTERN = "https://comicvine.gamespot.com/api/volumes?" \
                       "format=json&" \
                       "field_list=api_detail_url&" \
                       "sort=id:asc&" \
                       "offset={offset}&" \
                       "limit={limit}&" \
                       "api_key={api_key}"
    name = "comicvine_volumes"
