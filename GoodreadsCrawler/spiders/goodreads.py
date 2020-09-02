import scrapy
import urllib.parse as urlparse
import json
import requests
import html
from ..settings import TARGET_URLS


class GoodReadsSpider(scrapy.Spider):
    name = "goodreads"
    start_urls = TARGET_URLS
    first_time_run = True


    def parse(self, response):
        print("Parsing ", response.request.url)
        # If this is the first request, we need to yield other requests for unknown numbers of pages
        if self.first_time_run:
            self.first_time_run = False
            final_page_url = response.selector.xpath("//a[contains(@href,'page=')]/@href").getall()[-2]
            try:
                total_pages_count = int(urlparse.parse_qs(urlparse.urlparse(final_page_url).query)['page'][0])
            except:
                total_pages_count = 1

            # Call crawling task for each page
            for page_num in range(1, total_pages_count + 1):
                yield scrapy.Request((response.request.url + "?page={page}").format(page=page_num), self.parse)

        # Crawling phase
        # Get list of books in current page
        books_urls_list = response.selector.xpath("//a[@class='bookTitle']/@href").getall()
        for book_url in books_urls_list:
            # Call crawling task for each book item
            yield scrapy.Request(response.urljoin(book_url), self.item_parse)


    def item_parse(self, response): # parser for a particularly single item
        print("-> Item crawling ", response.request.url)
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



    # Send a get request and return as a Selector object
    def get_response(self, url):
        req = requests.get(url)
        html_code = html.unescape(req.text[29:-5].encode().decode("unicode_escape").encode("latin1", "ignore").decode("utf-8"))
        response = scrapy.Selector(text=html_code)
        return response


    def get_text_by_xpath(self, selector, xpath_str, index=0, all=False):
        try:
            if all:
                res = "\n".join(selector.xpath(xpath_str).getall())
            else:
                res = selector.xpath(xpath_str)[index].get()
        except:
            res = ""

        return res.strip()


    def subcomment_selector_to_json(self, comment):
        return [{
            'user_id': comment.xpath("div/a/@href").get().split("/")[5].split("-")[0],
            'name': comment.xpath("div/a/@title").get(),
            'content': self.get_text_by_xpath(comment, "div[contains(@class, 'reviewText')]/text()", all=True),
            'date': comment.xpath("div[contains(@class, 'brownBox')]/div/a/text()")[-1].get(),
        }]


    def get_sub_comments(self, review_id):
        print("\t\t Getting subcomments for review " + review_id)

        res = []

        # With the limit of data, now we don't know how to count the number of page in sub comments
        # We suppose that it has the same structure with other pages

        # Count how many pages of comments
        comments_response = self.get_response("https://www.goodreads.com/review/show/{review_id}".format(review_id=review_id))
        try:
            total_pages_count = int(comments_response.xpath("//a[@href='#']/text()")[-2].get())
        except:
            total_pages_count = 1

        # We get also comments in first page to save time
        comments = comments_response.xpath("//div[@id='comment_list']/div[contains(@class, 'comment')]")
        if comments is None:
            return res
        for comment in comments:
            res += self.subcomment_selector_to_json(comment)


        for comment_page in range(2, total_pages_count + 1):
            # Get comment as scrapy resposne
            comments_response = self.get_response("https://www.goodreads.com/review/show/{review_id}?page={comment_page}"
                .format(review_id=review_id, comment_page=comment_page))

            comments = comments_response.xpath("//div[@id='comment_list']/div[contains(@class, 'comment')]")
            if comments is None:
                break

            for comment in comments:
                res += self.subcomment_selector_to_json(comment)
            
        return res


    def review_selector_to_json(self, review):
        review_id = review.xpath("div/div/link/@href").get().split("/")[-1]
        comments = self.get_sub_comments(review_id)
        return [{
            'review_id': review_id,
            'user_id': review.xpath("div/div/a/@href").get().split("/")[3].split("-")[0],
            'name': review.xpath("div/div/a/@title").get(),
            'rating': str(len(review.xpath("div/div/div/div[contains(@class, 'reviewHeader')]/span/span[contains(@class, 'staticStar p10')]").getall())),
            'content': self.get_text_by_xpath(review, "div/div/div/div[contains(@class, 'reviewText')]/span/span/text()", all=True),
            'comments': comments,
            'date': review.xpath("div/div/div/div/a[contains(@class, 'reviewDate')]/text()").get(),
        }]


    # Get all comments
    def get_reviews_json(self, book_id):
        print("\t-> Reading reviews for book_id ", book_id)
        res = []

        # Count how many pages of comments
        reviews_response = self.get_response("https://www.goodreads.com/book/reviews/{book_id}?hide_last_page=true&utf8=\%E2\%9C\%93&language_code=".format(book_id=book_id))
        try:
            total_pages_count = int(reviews_response.xpath("//a[@href='#']/text()")[-2].get())
        except:
            total_pages_count = 1
        # Get also reviews in first page to save time
        reviews = reviews_response.xpath("//div[@id='bookReviews']/div[@class='friendReviews elementListBrown']")
        for review in reviews:
            res += self.review_selector_to_json(review)


        # Iterate over each page to get comments
        for review_page in range(2, total_pages_count + 1):
            reviews_response = self.get_response("https://www.goodreads.com/book/reviews/{book_id}?hide_last_page=true&utf8=\%E2\%9C\%93&language_code=&page={page}"
                .format(book_id=book_id, page=review_page))
            reviews = reviews_response.xpath("//div[@id='bookReviews']/div[@class='friendReviews elementListBrown']")

            for review in reviews:
                res += self.review_selector_to_json(review)

        return res
