# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import mimetypes

import requests
from scrapy.utils.project import get_project_settings


settings = get_project_settings()
IMAGES_STORE = settings.get("IMAGES_STORE")

headers = {
    "Accept": "image/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "en-US,en;q=0.8",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
}


def validate_image(url):
    """ Verifiying that url is JPEG  image"""
    mime, _ = mimetypes.guess_type(url)
    if mime is not None:
        if "image/jpeg" == mime:
            return True
    return False


def validate_images(image_list):
    """ Find JPEG image in list of urls """
    for url in image_list:
        if validate_image(url):
            return (True, url)


class DownloadImagesPipeline(object):

    def process_item(self, item, spider):
        """ Verifiy and download images """
        ok, url = validate_images(item["images"])
        if ok:
            # simulationg google user
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                file_name = "{f}.jpg".format(f=item["file_name"])
                image_file = os.path.join(IMAGES_STORE, file_name)
                with open(image_file, "wb") as f:
                    f.write(response.content)
                return item
