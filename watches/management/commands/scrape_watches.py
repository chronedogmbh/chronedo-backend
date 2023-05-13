import time
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

from django.core.management.base import BaseCommand

from bs4 import BeautifulSoup, NavigableString, Tag
from selenium import webdriver

from watches.models import Brand, Watch


class Command(BaseCommand):
    help = "Scrape Watches from Chrono24"

    def get_pagination_links(self, url: str) -> List[Tuple[int, str]]:
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        pagination_nav = soup.select(".pagination li:not(.flex-grow-1)")

        pages_links = []

        if not pagination_nav:
            pages_links = [(1, url)]
        else:
            total_pages = pagination_nav[-1].text.strip()
            for i in range(1, int(total_pages) + 1):
                if i <= self.max_pages:
                    link = url.replace("index.htm", f"index-{i}.htm")
                    label = i
                    pages_links.append((label, link))

        driver.quit()

        return pages_links

    def scrape_watches(self, url: str) -> List[Dict[str, Any]]:
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(options=options)
        parsed_url = urlparse(url)
        domain_with_protocol = f"{parsed_url.scheme}://{parsed_url.netloc}"
        driver.get(url)

        total_height = 0
        distance = 1000
        while True:
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script(f"window.scrollBy(0, {distance});")
            total_height += distance
            time.sleep(1)
            if total_height >= scroll_height:
                break

        soup = BeautifulSoup(driver.page_source, "html.parser")

        def extract_data(item: Tag) -> Dict[str, Any]:
            link_element = item.select_one("a")
            title_element = item.select_one(".text-bold.text-ellipsis")
            subtitle_element = item.select_one(".text-ellipsis.m-b-2")
            price_element = item.select_one(
                ".d-flex.justify-content-between.align-items-end.m-b-1 .text-bold"
            )
            image_element = item.select_one(".article-item-image-container img")
            image_url = image_element["src"] if image_element else None

            link = domain_with_protocol + link_element["href"] if link_element else None

            watch_data = {
                "link": link,
                "title": title_element.text.strip() if title_element else None,
                "subtitle": subtitle_element.text.strip() if subtitle_element else None,
                "price": price_element.text.strip() if price_element else None,
                "image": image_url,
            }

            if link:
                driver.get(link)
                time.sleep(1)
                watch_soup = BeautifulSoup(driver.page_source, "html.parser")
                data_element = watch_soup.select_one(
                    ".js-tab.tab.active section .row .col-xs-24.col-md-12 table tbody"
                )

                if data_element:
                    for item in data_element:
                        if isinstance(item, NavigableString):
                            continue

                        if isinstance(item, Tag):
                            if len(item.select("td")) < 2:
                                continue

                            sub_data = item.select("td")
                            key = sub_data[0].select_one("strong").text.strip()
                            value = sub_data[1].text.strip()

                            if key == "Location":
                                watch_data["location"] = value

            return watch_data

        watch_items = soup.select(".article-item-container")
        watches = []

        for item in watch_items:
            extracted_data = extract_data(item)
            if (
                extracted_data["title"] is None
                or extracted_data["price"] is None
                or extracted_data["link"] is None
                or extracted_data["image"] is None
                or extracted_data["subtitle"] is None
                or extracted_data["location"] is None
            ):
                continue
            else:
                watches.append(extracted_data)

        driver.quit()

        return watches

    def fetch_watches_by_brand(self, initial_url: str) -> List[Dict[str, Any]]:
        pages = self.get_pagination_links(initial_url)
        watches = []
        for page in pages:
            label, url = page
            scraped_watches = self.scrape_watches(url)
            watches.extend(scraped_watches)

        self.stdout.write(
            self.style.SUCCESS(
                f"Scraped {len(watches)} watches from {len(pages)} pages"
            )
        )
        return watches

    def add_arguments(self, parser):
        parser.add_argument("max_pages", type=int, help="Max Pages to Scrape")
        parser.add_argument("per_page", type=int, help="Watches per Page")

    def handle(self, *args, **kwargs):
        BRANDS = [
            "rolex",
            "iwc",
            "omega",
            "breitling",
            "audemarspiguet",
            "hublot",
            "panerai",
            "patekphilippe",
            "tudor",
            "gallet",
        ]
        VALID_PER_PAGE = [30, 60, 120]
        max_pages = kwargs["max_pages"]
        per_page = kwargs["per_page"]

        if max_pages < 1:
            self.stdout.write(self.style.ERROR("Invalid Max Pages!"))
            return
        if per_page not in VALID_PER_PAGE:
            self.stdout.write(self.style.ERROR("Invalid Per Page!"))
            self.stdout.write(
                self.style.NOTICE(f"Valid Per Page Values: {VALID_PER_PAGE}")
            )
            return

        self.max_pages = max_pages

        for brand in BRANDS:
            self.stdout.write(
                self.style.NOTICE(
                    f"Scraping {brand} - Per Page{per_page} - Total Pages {max_pages}..."
                )
            )
            brand_obj, _ = Brand.objects.get_or_create(name=brand)
            url = f"https://www.chrono24.com/{brand}/index.htm?pageSize={per_page}"
            data = self.fetch_watches_by_brand(url)

            for item in data:
                normalized_price = item["price"].replace("$", "").replace(",", "")
                try:
                    watch, _ = Watch.objects.get_or_create(
                        title=item["title"],
                        subtitle=item["subtitle"],
                        price=normalized_price,
                        link=item["link"],
                        image=item["image"],
                        location=item.get("location"),
                        brand=brand_obj,
                    )
                except Exception as E:
                    self.stdout.write(
                        self.style.ERROR(f"Failed to add {item['title']}")
                    )
                    self.stdout.write(self.style.ERROR(str(E)))

        self.stdout.write(
            self.style.SUCCESS(f"Watches of {brand} scrapped successfully!")
        )
