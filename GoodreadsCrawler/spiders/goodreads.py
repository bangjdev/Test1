import scrapy
import urllib.parse as urlparse
import json
import requests
import html


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


    # Send a get request and return as a Selector object
    def get_response(self, url):
        req = requests.get(url)
        html_code = html.unescape(req.text[29:-5].encode().decode("unicode_escape").encode("utf-8").decode("utf-8"))
        response = scrapy.Selector(text=html_code)
        return response


    def get_text_by_xpath(self, selector, xpath_str, index=0):
        try:
            res = selector.xpath(xpath_str)[index].get()
        except:
            res = ""

        return res.strip()


    # Get all comments
    def get_reviews_json(self, book_id):
        # Count how many pages of comments
        response = self.get_response("https://www.goodreads.com/book/reviews/{book_id}?hide_last_page=true&utf8=\%E2\%9C\%93&language_code=".format(book_id=book_id))
        try:
            total_pages_count = int(response.xpath("//a[@href='#']/text()")[-2].get())
        except:
            total_pages_count = 1

        # Iterate over each page to get comments
        res = []
        for comment_page in range(1, total_pages_count + 1):
            comments_response = self.get_response("https://www.goodreads.com/book/reviews/{book_id}?hide_last_page=true&utf8=\%E2\%9C\%93&language_code=&page={page}"
                .format(book_id=book_id, page=comment_page))
            reviews = comments_response.xpath("//div[@id='bookReviews']/div[@class='friendReviews elementListBrown']")

            for review in reviews:
                res += [{
                    'user_id': review.xpath("div/div/a/@href").get().split("/")[3].split("-")[0],
                    'name': review.xpath("div/div/a/@title").get(),
                    'content': self.get_text_by_xpath(review, "div/div/div/div[contains(@class, 'reviewText')]/span/span/text()", -1),
                    'date': review.xpath("div/div/div/div/a[contains(@class, 'reviewDate')]/text()").get(),
                }]

        return res


    def item_parse(self, response): # parser for a particularly single item
        # book_meta contains info about rating
        book_meta = response.xpath("//div[@id='bookMeta']")

        # encode reviews data in json format
        book_reviews = self.get_reviews_json(response.xpath("//input[@id='book_id']/@value").get())

        yield {
            'id': response.xpath("//input[@id='book_id']/@value").get(),
            'url': response.request.url,
            'title': response.xpath("//h1[@id='bookTitle']/text()").get().strip(),
            'author': response.xpath("//div[@id='bookAuthors']//a//span/text()").get(),
            'rating': book_meta.xpath("//span[@itemprop='ratingValue']/text()").get().strip(),
            'description': self.get_text_by_xpath(response, "//div[@id='description']/span/text()", -1),
            'reviews': book_reviews
        }