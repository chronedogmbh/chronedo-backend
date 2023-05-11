import time
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup, NavigableString, Tag
from selenium import webdriver


def get_pagination_links(url: str) -> List[Tuple[int, str]]:
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    pagination_nav = soup.select(".pagination li:not(.flex-grow-1)")

    pages_links = []

    if not pagination_nav:
        pages_links = [url]
    else:
        total_pages = pagination_nav[-1].text.strip()
        for i in range(1, int(total_pages) + 1):
            link = url.replace("index.htm", f"index-{i}.htm")
            label = i
            pages_links.append((label, link))

    driver.quit()

    return pages_links


def scrape_watches(url: str) -> List[Dict[str, Any]]:
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
    watches = [extract_data(item) for item in watch_items]

    driver.quit()

    return watches


def fetch_watches_by_brand(initial_url: str) -> List[Dict[str, Any]]:
    pages = get_pagination_links(initial_url)
    watches = []
    for page in pages:
        label, url = page
        print(f"Scraping page {label} of {len(pages)}")
        scraped_watches = scrape_watches(url)
        watches.extend(scraped_watches)

    return watches


url = "https://www.chrono24.com/gallet/index.htm?pageSize=30"
data = fetch_watches_by_brand(url)
print(data)
print(len(data))
