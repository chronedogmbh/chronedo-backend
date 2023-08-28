import time
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup, NavigableString, Tag
from selenium import webdriver

from watches.models import Watch


class Command(BaseCommand):
    help = "Scrape Watches from Chrono24"

    VALID_BRANDS = {
        "rolex": 221,
        "iwc": 124,
        "omega": 187,
        "breitling": 32,
        "audemarspiguet": 18,
        "hublot": 118,
        "panerai": 192,
        "patekphilippe": 194,
        "tudor": 245,
        
    }

    VALID_COUNTRY_IDS = ["AT", "BR", "BG", "CA", "CZ", "FR", "DE", "GR", "IT", "JP", "NO", "PL", "SG", "ES", "SE" "CH","NL", "AE",  "UK",  "US"]  # Add more country IDs if needed

    brand_ids = {
        "rolex": 1,
        "omega": 2,
        "iwc": 4,
        "breitling": 5,
        "audemarspiguet": 6,
        "hublot": 7,
        "panerai": 8,
        "patekphilippe": 9,
        "tudor": 10
    }

    def add_arguments(self, parser):
        parser.add_argument("brand", type=str, help="Brand name")
        parser.add_argument("country_id", type=str, help="Country ID")
        parser.add_argument("per_page", type=int, help="Watches per Page")
        parser.add_argument("max_pages", type=int, help="Max Pages to Scrape")

    def handle(self, *args, **kwargs):
        VALID_PER_PAGE = [30, 60, 120]
        brand = str(kwargs["brand"]).lower()  # Convert brand to lowercase string
        country_id = str(kwargs["country_id"]).upper()  # Convert country ID to uppercase string
        per_page = kwargs["per_page"]
        max_pages = kwargs["max_pages"]

        if max_pages < 1:
            self.stdout.write(self.style.ERROR("Invalid Max Pages!"))
            return
        if per_page not in VALID_PER_PAGE:
            self.stdout.write(self.style.ERROR("Invalid Per Page!"))
            self.stdout.write(
                self.style.NOTICE(f"Valid Per Page Values: {VALID_PER_PAGE}")
            )
            return

        if brand not in self.VALID_BRANDS:
            self.stdout.write(self.style.ERROR("Invalid Brand!"))
            self.stdout.write(
                self.style.NOTICE(f"Valid Brands: {', '.join(self.VALID_BRANDS)}")
            )
            return

        if country_id not in self.VALID_COUNTRY_IDS:
            self.stdout.write(self.style.ERROR("Invalid Country ID!"))
            self.stdout.write(
                self.style.NOTICE(f"Valid Country IDs: {', '.join(self.VALID_COUNTRY_IDS)}")
            )
            return

        self.stdout.write(
            self.style.NOTICE(
                f"Scraping {brand} - Country ID: {country_id} - Per Page {per_page} - Total Pages {max_pages}..."
            )
        )

        manufacturer_id = self.VALID_BRANDS.get(brand)
        brand_id = self.brand_ids.get(brand)

        if manufacturer_id is None or brand_id is None:
            self.stdout.write(self.style.ERROR("Invalid Brand!"))
            self.stdout.write(
                self.style.NOTICE(f"Valid Brands: {', '.join(self.VALID_BRANDS)}")
            )
            return

        url = f"https://www.chrono24.com/search/index.htm?countryIds={country_id}&currencyId=USD&dosearch=true&manufacturerIds={manufacturer_id}&maxAgeInDays=0&pageSize={per_page}&redirectToSearchIndex=true&resultview=block&sortorder=0"
        print(url)

        data = self.fetch_watches_by_brand(url, brand, per_page, max_pages)

        for item in data:
            normalized_price = item["price"].replace("$", "").replace(",", "")
            try:
                watch, _ = Watch.objects.get_or_create(
                    brand_id=item["brand_id"],
                    title=item["title"],
                    subtitle=item["subtitle"],
                    price=normalized_price,
                    link=item["link"],
                    image=item["image"],
                    location=item.get("location"),
                )

                print("Extracted Watch Data:", watch)

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to add {item['title']}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"Watches of {brand} scraped successfully!")
        )

   
    def get_pagination_links(self, url: str, max_pages: int) -> List[Tuple[int, str]]:
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
                if i <= max_pages:
                    if i == 1:
                        link = url
                    else:
                        link = url.replace("index-", "index")
                        link = link.replace("&sortorder=0", f"&showpage={i}&sortorder=0")  # Add showpage parameter
                    label = i
                    pages_links.append((label, link))

        driver.quit()

        return pages_links

    def scrape_watches(self, url: str, brand_id: int) -> List[Dict[str, Any]]:
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        driver = webdriver.Chrome(options=options)
        parsed_url = urlparse(url)
        domain_with_protocol = f"{parsed_url.scheme}://{parsed_url.netloc}"
        driver.get(url)
        print(url)
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
                "brand_id": brand_id,
                "link": link,
                "title": title_element.text.strip() if title_element else None,
                "subtitle": subtitle_element.text.strip()
                if subtitle_element
                else None,
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
                            elif key == "Gender":  # New condition for extracting Gender
                                watch_data["gender"] = value  # Adding the gender information

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
                or extracted_data.get("gender") is None  # Check for gender field
            ):
                print("Missing data for:", extracted_data["title"])
                print("here")
                continue
            else:
                watches.append(extracted_data)

        driver.quit()

        return watches

    def fetch_watches_by_brand(
        self, initial_url: str, brand: str, per_page: int, max_pages: int
    ) -> List[Dict[str, Any]]:
        pages = self.get_pagination_links(initial_url, max_pages)[:max_pages]
        watches = []

        brand_id = self.brand_ids.get(brand)

        if brand_id is None:
            self.stdout.write(self.style.ERROR("Invalid Brand!"))
            self.stdout.write(
                self.style.NOTICE(f"Valid Brands: {', '.join(self.VALID_BRANDS)}")
            )
            return watches

        for page in pages:
            label, url = page
            scraped_watches = self.scrape_watches(url, brand_id)
            watches.extend(scraped_watches)

        for item in watches:
            normalized_price = item["price"].replace("$", "").replace(",", "")
            try:
                watch, _ = Watch.objects.get_or_create(
                    brand_id=item["brand_id"],
                    title=item["title"],
                    subtitle=item["subtitle"],
                    price=normalized_price,
                    link=item["link"],
                    image=item["image"],
                    location=item.get("location"),
                    gender=item.get("gender"),  # Add the gender field
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to add {item['title']}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"Watches of {brand} scraped successfully!")
        )

        return watches

