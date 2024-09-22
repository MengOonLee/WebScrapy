import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import wait, expected_conditions
import scrapy
from scrapy import crawler, loader
from itemloaders import processors
import logging
logging.getLogger().setLevel(logging.ERROR)

class LotusItem(scrapy.Item):
    categories = scrapy.Field()
    name = scrapy.Field(output_processor=processors.TakeFirst())
    price = scrapy.Field(output_processor=processors.TakeFirst())
    info = scrapy.Field(output_processor=processors.TakeFirst())

class LotusLoader(loader.ItemLoader):
    item = LotusItem()

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
            # "https://www.lotuss.com.my/en/category/grocery/biscuits-cakes"
            "https://www.lotuss.com.my/en/category/grocery/commodities/rice"
        ]
        
        for url in urls:
            request = scrapy.Request(url=url, callback=self.parse_category)
            yield request

    def parse_category(self, response):
        self.driver.get(response.url)

        try:
            wait.WebDriverWait(self.driver, timeout=10)\
                .until(expected_conditions.presence_of_element_located(
                    (By.XPATH, "//div[@class='carousel']")))
            selector = scrapy.Selector(text=self.driver.page_source)
            category_urls = selector.css("div.carousel a")

            yield from response.follow_all(category_urls,
                callback=self.parse_category)
        except:
            pass

        last_height = self.driver.execute_script(
            "return document.body.scrollHeight")
        
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(20)
        
        new_height = self.driver.execute_script(
            "return document.body.scrollHeight")
        print(last_height, new_height)
            
        # while True:
        #         time.sleep(10)
        #         self.driver.execute_script(
        #             "window.scrollTo(0, document.body.scrollHeight)")

        #         new_height = self.driver.execute_script(
        #             "return document.body.scrollHeight")
        #         if new_height==last_height:
        #             break
        #         last_height = new_height
        #     print(new_height)

process = crawler.CrawlerProcess()
process.crawl(LotusSpider)
process.start()
