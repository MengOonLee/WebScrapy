import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import wait, expected_conditions
from selenium.common.exceptions import NoSuchElementException
import scrapy
from scrapy import crawler, loader
from itemloaders import processors
import logging
logging.getLogger().setLevel(logging.ERROR)

class LotusItem(scrapy.Item):
    categories = scrapy.Field()
    name = scrapy.Field(output_processor = processors.TakeFirst())
    price = scrapy.Field(output_processor = processors.TakeFirst())
    info = scrapy.Field()

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
            "https://www.lotuss.com.my/en/product/mamypoko-extra-dry-unisex-pants-xl32-74175572"
        ]
        
        for url in urls:
            request = scrapy.Request(url=url, callback=self.parse_info)
            yield request

    def parse_item(self, response):
        self.driver.get(response.url)

        num_trial = 0
        while num_trial < 3:
            try:
                if wait.WebDriverWait(self.driver, timeout=10)\
                    .until(expected_conditions.presence_of_element_located(
                        (By.XPATH, "//div[@id='product-list']"))):
                    break
            except NoSuchElementException:
                continue
                num_trial += 1
        
        selector = scrapy.Selector(text=self.driver.page_source)
        categories_url = selector.css("div.carousel a")
        
        if len(categories_url)!=0:
            yield from response.follow_all(categories_url,
                callback=self.parse_items)

        else:
            last_height = self.driver.execute_script(
                "return document.body.scrollHeight")
            while True:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(10)

                new_height = self.driver.execute_script(
                    "return document.body.scrollHeight")
                if new_height==last_height:
                    break
                last_height = new_height
            
            selector = scrapy.Selector(text=self.driver.page_source)
            
            categories = selector.xpath(
                "//li[contains(@class, 'MuiBreadcrumbs-li')]//text()"
            ).getall()
            
            for item in selector.css("div.product-grid-item"):
                loader = LotusLoader()

                loader.add_value("categories", categories)
                
                name = item.css("a#product-title::text").get()
                loader.add_value("name", name)

                price = item.css("p")[0].css("::text").getall()
                loader.add_value("price", "".join(price))

                info_page = item.css("a::attr(href)").get()
                if info_page is not None:
                    yield response.follow(info_page,
                        callback=self.parse_info, meta={"loader": loader})

                yield loader.load_item()

                # img_url = item.css("img::attr(src)").get()

            # info_links = selector.css("div#product-list a")
            # yield from response.follow_all(info_links,
            #     callback=self.parse_info)

    def parse_info(self, response):
        self.driver.get(response.url)

        num_trial = 0
        while num_trial < 3:
            try:
                if wait.WebDriverWait(self.driver, timeout=10)\
                    .until(expected_conditions.presence_of_element_located(
                        (By.XPATH, "//div[@id='scrollable-force-tabpanel-0']"))):
                    break
            except NoSuchElementException:
                continue
                num_trial += 1
        
        selector = scrapy.Selector(text=self.driver.page_source)
        info = selector.css("div#scrollable-force-tabpanel-0 ::text").get()
        
        print(info)
        
        # self.loader.add_value("info", info)


process = crawler.CrawlerProcess(
    # settings={"FEEDS":{"items.jl":{"format":"jsonlines"}}}
)
process.crawl(LotusSpider)
process.start()
