import datetime
import json

import scrapy

from .base_spider import BaseSpider


class CharactersSpider(BaseSpider):
    # LIST_URL_PATTERN should contain 3 placeholders: limit, offset and api_key and should not contain filter parameter
    LIST_URL_PATTERN = "https://comicvine.gamespot.com/api/characters?" \
                       "format=json&" \
                       "field_list=api_detail_url,id&" \
                       "sort=id:asc&" \
                       "offset={offset}&" \
                       "limit={limit}&" \
                       "api_key={api_key}"
    name = "comicvine_characters"
    DETAIL_FIELD_LIST = "id,api_detail_url,site_detail_url,name,aliases,deck,description,image,first_appeared_in_issue,real_name,gender,birth,origin,character_friends,character_enemies,teams,team_enemies,team_friends,publisher,creators,powers"
