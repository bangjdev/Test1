import requests, html
import scrapy
import json


class Test:
    # Send a get request and return as a Selector object
    def get_response(self, url):
        req = requests.get(url)
        html_code = html.unescape(req.text[29:-5].encode().decode("unicode_escape").encode("latin1", "ignore").decode("utf-8"))
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


test = Test()
f = open("test.json", "w", encoding="utf-8")
f.write(json.dumps(test.get_reviews_json("36989101"), ensure_ascii=False).encode("utf-8").decode())
f.close()