import scrapy
import urllib.parse as urlparse
import json


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
        # Get list of books in current page
        books_urls_list = response.selector.xpath("//a[@class='bookTitle']/@href").getall()
        for book_url in books_urls_list:
            # Call crawling task for each book item
            yield scrapy.Request(response.urljoin(book_url), self.item_parse)

    def get_reviews_json(self, book_reviews):
        res = []
        for review in book_reviews:
            res += [{
                'user_id': review.xpath("div/div/a/@href").get().split("/")[3].split("-")[0],
                'name': review.xpath("div/div/a/@title").get(),
                'content': review.xpath("div/div/div/div[contains(@class, 'reviewText')]/span/span/text()")[-1].get(),
                'date': review.xpath("div/div/div/div/a[contains(@class, 'reviewDate')]/text()").get(),
            }]

        return res


    def item_parse(self, response): # parser for a particularly single item
        # book_meta contains info about rating
        book_meta = response.xpath("//div[@id='bookMeta']")

        # encode reviews data in json format
        book_reviews = self.get_reviews_json(response.xpath("//div[@id='bookReviews']/div[@class='friendReviews elementListBrown']"))

        # Sometimes book doesn't have description
        try:
            description = response.xpath("//div[@id='description']/span/text()")[-1].get()
        except:
            description = ""

        yield {
            'id': response.xpath("//input[@id='book_id']/@value").get(),
            'url': response.request.url,
            'title': response.xpath("//h1[@id='bookTitle']/text()").get().strip(),
            'author': response.xpath("//div[@id='bookAuthors']//a//span/text()").get(),
            'rating': book_meta.xpath("//span[@itemprop='ratingValue']/text()").get().strip(),
            'description': description,
            'reviews': book_reviews
        }