import scrapy


class WikiDictSpider(scrapy.Spider):
    name = "wiki_dict"
    start_urls = [
        "https://vi.wiktionary.org/w/index.php?title=Th%E1%BB%83_lo%E1%BA%A1i:%C4%90%E1%BB%99ng_t%E1%BB%AB_ti%E1%BA%BFng_Vi%E1%BB%87t",
        "https://vi.wiktionary.org/w/index.php?title=Th%E1%BB%83_lo%E1%BA%A1i:T%C3%ADnh_t%E1%BB%AB_ti%E1%BA%BFng_Vi%E1%BB%87t",
        "https://en.wiktionary.org/w/index.php?title=Category:English_verbs",
        "https://en.wiktionary.org/w/index.php?title=Category:English_adjectives",
        "https://en.wiktionary.org/w/index.php?title=Category:English_conjunctions",
        "https://en.wiktionary.org/w/index.php?title=Category:English_adverbs",
        "https://en.wiktionary.org/w/index.php?title=Category:English_nouns"
    ]


    def parse(self, response):
        print("Parsing ", response.request.url)

        next_page = response.xpath("//div[@id='mw-pages']/a[contains(text(), 'Trang sau')]/@href").get()
        if next_page is None:
            next_page = response.xpath("//div[@id='mw-pages']/a[contains(text(), 'next page')]/@href").get()

        if not (next_page is None):
            yield scrapy.Request(("/".join(response.request.url.split("/")[0:3])) + next_page, self.parse)

        verbs = response.xpath("//div[@class='mw-category']/div/ul/li/a/text()").getall()
        yield {"words": verbs}