import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import wait, expected_conditions
from selenium.common.exceptions import NoSuchElementException
import scrapy
from scrapy import crawler, loader
from itemloaders import processors
import logging
logging.getLogger().setLevel(logging.ERROR)

class LotusItem(scrapy.Item):
    categories = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    info = scrapy.Field()

class LotusLoader(loader.ItemLoader):
    default_output_processor = processors.TakeFirst()
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
            # "https://www.lotuss.com.my/en/category/grocery/commodities/rice"
            "https://www.lotuss.com.my/en/product/jati-pusa-finest-basmathi-1121-2kg-74175599"
        ]

        for url in urls:
            request = scrapy.Request(url=url, callback=self.parse_items)
            yield request

    # def parse_products(self, response):
    #     self.driver.get(response.url)

    #     try:
    #         wait.WebDriverWait(self.driver, timeout=10)\
    #             .until(expected_conditions.presence_of_element_located(
    #                 (By.XPATH, "//div[@class='carousel']")))
    #         selector = scrapy.Selector(text=self.driver.page_source)
    #         category_urls = selector.css("div.carousel a")
    #         yield from response.follow_all(category_urls,
    #             callback=self.parse_products)

    #     except Exception:
    #         pass

    #     try:
    #         wait.WebDriverWait(self.driver, timeout=10)\
    #             .until(expected_conditions.presence_of_element_located(
    #                 (By.XPATH, "//div[@id='product-list']")))

    #     except Exception:
    #         raise

    #     html = self.driver.find_element(By.TAG_NAME, "html")
    #     last_height = self.driver.execute_script(
    #         "return document.body.scrollHeight")
    #     while True:
    #         for _ in range(3):
    #             html.send_keys(Keys.END)
    #             time.sleep(10)
    #             html.send_keys(Keys.HOME)
    #         new_height = self.driver.execute_script(
    #             "return document.body.scrollHeight")
    #         if new_height==last_height:
    #             break
    #         last_height = new_height

    #     selector = scrapy.Selector(text=self.driver.page_source)
    #     item_urls = selector.css("div#product-list a")
    #     yield from response.follow_all(item_urls,
    #         callback=self.parse_items)

    def parse_items(self, response):
        self.driver.get(response.url)
        loader = LotusLoader()

        num_trial = 0
        while num_trial < 3:
            try:
                if wait.WebDriverWait(self.driver, timeout=10)\
                    .until(expected_conditions.presence_of_element_located(
                        (By.XPATH, "//img[@id='current-product-image']"))):
                    break
            except NoSuchElementException:
                continue
                num_trial += 1

        selector = scrapy.Selector(text=self.driver.page_source)
        categories = selector.css("ol.MuiBreadcrumbs-ol ::text").getall()
        categories = ["/".join(categories[1:])]
        loader.add_value("categories", categories)

        name = selector.css("h1::text").get()
        loader.add_value("name", name)

        price = selector.css(
            "div.MuiBox-root.jss418.jss329.jss326 ::text"
        ).getall()
        price = ["".join(price)]
        loader.add_value("price", price)

        info = selector.css(
            "div#scrollable-force-tabpanel-0 ::text"
        ).get()
        loader.add_value("info", info)

        yield loader.load_item()

process = crawler.CrawlerProcess(
    # settings={"FEEDS":{"items.jl":{"format":"jsonlines"}}}
)
process.crawl(LotusSpider)
process.start()
