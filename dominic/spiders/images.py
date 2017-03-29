# -*- coding: utf-8 -*-
import urllib
import csv
import json

import scrapy
from scrapy.utils.project import get_project_settings

from scrapy.exceptions import CloseSpider

from dominic.items import DominicItem

settings = get_project_settings()


class ImagesSpider(scrapy.Spider):

    name = "images"
    allowed_domains = ["ajax.googleapis.com"]

    def __init__(self, csv_file=None, key=None, cx=None, *args, **kwargs):
        """ Constructor can get nondefault CSV_file as arguments """
        super(ImagesSpider, self).__init__(*args, **kwargs)
        if csv_file is None:
            csv_file = settings.get("DEFAULT_PEOPLE_LIST")
        self._csv_file = csv_file
        
        if key is None:
            raise CloseSpider('No google custom search api key')

        if cx is None:
            raise CloseSpider('No google custom search cx value')

        self.key = key
        self.cx = cx

    def names_list(self, csv_file=None):
        """ Proces file that has list of names in CSV format"""
        csv_file = self._csv_file if csv_file is None else csv_file
        if csv_file is None:
            raise StopIteration
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["url_encoded_name"] = urllib.pathname2url(
                                                    row.get("name", ""))
                yield row

    def start_requests(self):

        url = "https://www.googleapis.com/customsearch/v1?q={row[url_encoded_name]}&cx={cx}&imgColorType=color&imgSize=medium&imgType=face&searchType=image&key={key}"
        
        for row in self.names_list():
            yield scrapy.Request(
                url.format(row=row, key=self.key, cx=self.cx),
                self.parse,
                meta={"row": row})

    def parse(self, response):
        jsonr = json.loads(response.body)
        row = response.meta["row"]
        images_list = jsonr.get('items');

        item = DominicItem()
        if len(images_list) > 0:
            item["number"] = row.get("number")
            item["initial"] = row.get("initial")
            item["name"] = row.get("name")
            item["images"] = [image["link"]
                              for image in images_list]
            item["file_name"] = "{number}-{initial}-{name}".format(**row)

            yield item



