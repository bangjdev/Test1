import scrapy
import urllib.parse as urlparse


class GoodReadsSpider(scrapy.Spider):
    name = "goodreads"
    start_urls = ["https://www.goodreads.com/author/list/4634532.Nguy_n_Nh_t_nh"]
    first_time_run = True


    def parse(self, response):
        # If this is the first request, we need to yield other requests for unknown numbers of pages
        if self.first_time_run:
            self.first_time_run = False
            final_page_url = response.selector.xpath("//a[contains(@href,'page=')]/@href").getall()[-2]
            total_pages_count = int(urlparse.parse_qs(urlparse.urlparse(final_page_url).query)['page'][0])
            for page_num in range(1, total_pages_count + 1):
                yield scrapy.Request((response.request.url + "?page={page}").format(page=page_num), self.parse)

        # Crawling phase
        print("Crawling page " + response.request.url)
        print(response.selector.xpath("//a[@class='bookTitle']/@href").getall())

    def item_parse(self, response): # parser for a particularly single item
        pass