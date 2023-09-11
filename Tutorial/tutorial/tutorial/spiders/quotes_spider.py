import scrapy
import pathlib

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        "https://quotes.toscrape.com/page/1/",
        "https://quotes.toscrape.com/page/2/"
    ]

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"./data/quotes-{page}.html"
        pathlib.Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")
