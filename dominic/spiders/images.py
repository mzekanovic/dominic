# -*- coding: utf-8 -*-
import urllib
import csv
import json

import scrapy
from scrapy.utils.project import get_project_settings

from dominic.items import DominicItem

settings = get_project_settings()


class ImagesSpider(scrapy.Spider):

    name = "images"
    allowed_domains = ["ajax.googleapis.com"]

    def __init__(self, csv_file=None, *args, **kwargs):
        """ Constructor can get nondefault CSV_file as arguments """
        super(ImagesSpider, self).__init__(*args, **kwargs)
        if csv_file is None:
            csv_file = settings.get("DEFAULT_PEOPLE_LIST")
        self._csv_file = csv_file

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
        url = "https://ajax.googleapis.com/ajax/services/search/images?v=1.0&\
        imgsz=medium&q={row[url_encoded_name]}"
        for row in self.names_list():
            yield scrapy.Request(
                url.format(row=row),
                self.parse,
                meta={"row": row})

    def parse(self, response):
        jsonr = json.loads(response.body)
        row = response.meta["row"]
        item = DominicItem()
        if (jsonr.get("responseData") is not None and
                jsonr["responseData"].get("results") is not None and
                len(jsonr["responseData"]["results"]) > 0):
            item["number"] = row.get("number")
            item["initial"] = row.get("initial")
            item["name"] = row.get("name")
            item["images"] = [image["url"]
                              for image in jsonr["responseData"]["results"]]
            item["file_name"] = "{number}-{initial}-{name}".format(**row)

            yield item
