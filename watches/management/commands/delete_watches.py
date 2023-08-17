import time
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

from django.core.management.base import BaseCommand

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from selenium import webdriver

from watches.models import Brand, Watch


class Command(BaseCommand):
    help = "Scrape Watches from Chrono24"

    def handle(self, *args, **kwargs):
        watches = Watch.objects.order_by("?").all()[:500]
        for watch in watches:
            # print(watch.url)
            options = webdriver.ChromeOptions()
            options.add_argument("headless")
            driver = webdriver.Chrome(options=options)
            driver.get(watch.link)
            if driver.current_url != watch.link:
                watch.delete()
                print(watch.link)
