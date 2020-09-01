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
        # Get list of books in current page
        books_urls_list = response.selector.xpath("//a[@class='bookTitle']/@href").getall()
        for book_url in books_urls_list:
            # Call crawling task for each book item
            yield scrapy.Request(response.urljoin(book_url), self.item_parse)

    def item_parse(self, response): # parser for a particularly single item
        book_meta = response.xpath("//div[@id='bookMeta']")
        book_reviews = response.xpath("//div[@id='bookReviews']")
        yield {
            'id': response.xpath("//input[@id='book_id']/@value").get(),
            'url': response.request.url,
            'title': response.xpath("//h1[@id='bookTitle']/text()").get().strip(),
            'author': response.xpath("//div[@id='bookAuthors']//a//span/text()").get(),
            'rating': book_meta.xpath("//span[@itemprop='ratingValue']/text()").get().strip(),
            'description': response.xpath("//div[@id='description']/span/text()")[-1].get()
        }