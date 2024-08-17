import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import scrapy
from scrapy.crawler import CrawlerProcess

class LotusSpider(scrapy.Spider):
    name = 'Lotus'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        options = webdriver.chrome.options.Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--enable-javascript")
        options.add_argument("--enable-cookies")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-web-security")
        options.add_argument("--incognito")
        self.driver = webdriver.Chrome(options=options)

    def start_requests(self):
        urls = [
            "https://www.lotuss.com.my/en/product/aus-mutton-loin-slice-5318-74539337"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_categories)

    def parse_categories(self, response):
        self.driver.get(response.url)

        elem_present = ""
        while not elem_present:
            try:
                elem_present = self.driver.find_element(By.XPATH,
                    "//div[@class='product-grid-item']"
                )
            except:
                continue

        selector = scrapy.Selector(text=self.driver.page_source)
        category = selector.css("h1#category-title::text").get()
        print(category)
        category_links = selector.css("div.carousel a")
        if len(category_links)!=0:
            yield from response.follow_all(category_links,
                callback=self.parse_categories)
        else:
            last_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )

            while True:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight)"
                )
                time.sleep(3)
                new_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )
                if new_height==last_height:
                    break
                last_height = new_height

            selector = scrapy.Selector(text=self.driver.page_source)
            item_links = selector.css("div#product-list a")

            yield from response.follow_all(item_links,
                callback=self.parse_items)

    def parse_items(self, response):
        self.driver.get(response.url)

        elem_present = ""
        while not elem_present:
            try:
                elem_present = self.driver.find_element(By.XPATH, """
                    //img[@id='current-product-image']
                """)
            except:
                continue

        selector = scrapy.Selector(text=self.driver.page_source)
        item = selector.css("div.MuiBox-root")
        name = item.css("h1::text").get()
        price = item.css("::text")[3:6].getall()
        price = "".join(price)
        print(name, price)

process = CrawlerProcess()
process.crawl(LotusSpider)
process.start()
