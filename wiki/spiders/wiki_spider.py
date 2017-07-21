import scrapy
from urllib.parse import unquote
from wiki.items import WikiItem
from scrapy.contrib.loader import ItemLoader
from ChineseTone import *
import json
import os

base = '/users/Apple/desktop/'


class WikiSpider(scrapy.Spider):
    name = 'wiki'
    allow_domains = ['zh.wikisource.org']
    # category_list = ['古文', '史書', '宗教典籍', '小说', '戲曲', '教科書', '散文', '譯文', '醫家', '韵文']
    start_urls = [
        'https://zh.wikisource.org/wiki/Category:古文',
    ]

    def __init__(self):
        self.count = 0
        self.count_book_cat = 0

    # current_link = 'https://zh.wikisource.org/wiki/Category:古文'
    def parse(self, response):
        # cat_xpath = '//div[@id="mw-subcategories"]/div//ul/li/div/div[1]/a'
        cat_xpath = '''
        //div[@id="mw-subcategories"]/div/ul/li/div[@class="CategoryTreeSection"]/div[@class="CategoryTreeItem"]/a
        '''
        cat = response.xpath(cat_xpath)
        main_cat_text = response.xpath('//h1[@id="firstHeading"]/text()').extract_first()
        main_cat = main_cat_text.split(':')[1]

        cat_list = [cat]

        for cat_link in cat_list:
            link = cat_link.xpath('@href').extract()

            if link is not None:
                link = response.urljoin(link[0])
                # link_cat = unquote(link.split(':')[2])
                yield scrapy.Request(
                    link,
                    callback=self.parse_sub_cat,
                    meta={
                        'main_cat': main_cat,
                    },
                )

    # current_link = 'https://zh.wikisource.org/wiki/Category:史部'
    def parse_sub_cat(self, response):
        main_cat = response.meta['main_cat']
        xpath = '//*[@id="mw-subcategories"]/div/div/div/ul/li/div/div[1]/a'
        sub_cat = response.xpath(xpath)
        cat_text = response.xpath('//*[@id="firstHeading"]/text()').extract_first().split(':')[1]

        sub_list = [sub_cat]

        for sub_link in sub_list:
            link = sub_link.xpath('@href').extract()

            if link is not None:
                link = response.urljoin(link[0])
                link_cat = unquote(link.split(':')[2])
                yield scrapy.Request(
                    link,
                    meta={
                        'cat_text': cat_text,
                        'main_cat': main_cat,
                    },
                    callback=self.parse_book,
                )

    # current_link = 'https://zh.wikisource.org/wiki/Category:別史'
    def parse_book(self, response):
        main_cat = response.meta['main_cat']
        cat_text = response.meta['cat_text']

        xpath = '//*[@id="mw-pages"]/div/ul/li/a'
        cat_link = response.url
        sub_text = response.xpath('//*[@id="firstHeading"]/text()').extract_first().split(':')[1]
        book = response.xpath(xpath)

        book_list = [book]

        for book_link in book_list:
            link = book_link.xpath('@href').extract()

            if link is not None:
                link = response.urljoin(link[0])
                # link = unquote(link)
                yield scrapy.Request(
                    link,
                    callback=self.parse_book,
                    meta={
                        'main_cat': main_cat,
                        'cat_text': cat_text,
                        'cat_link': cat_link,
                        'sub_text': sub_text,
                    },
                    dont_filter=True,
                )

    # current_link = 'https://zh.wikisource.org/wiki/八家後漢書'
    def parse_book_cat(self, response):
        main_cat = response.meta['main_cat']
        cat_text = response.meta['cat_text']
        cat_link = response.meta['cat_link']
        sub_text = response.meta['sub_text']

        book_text = response.xpath('//h1[@id="firstHeading"]/text()').extract_first()
        quality_xpath = '//*[@id="mw-normal-catlinks"]/ul/li[1]/a/text()'
        book_cat_xpath = '//*[@id="mw-content-text"]/div/ul/li/a'
        quality = response.xpath(quality_xpath).extract_first()
        # first_article_link = response.urljoin(book_cat_list[0])
        # article_title_list = response.xpath(book_cat_xpath).xpath('@title').extract()

        book_cat_list = [response.xpath(book_cat_xpath)]

        for book_cat in book_cat_list:
            link = book_cat.xpath('@href').extract()
            article_title_list = book_cat.xpath('@title').extract()

            for title in article_title_list:
                if '页面不存在' in title:
                    # self.count_book_cat += 1
                    yield scrapy.Request(
                        cat_link,
                        callback=self.parse_book,
                        dont_filter=True,
                    )
                elif link is not None and quality == '75%' or quality == '100%':
                    link = response.urljoin(link[self.count_book_cat])
                    yield scrapy.Request(
                        link,
                        callback=self.parse_article,
                        meta={
                            'main_cat': main_cat,
                            'cat_text': cat_text,
                            'sub_text': sub_text,
                            'book_text': book_text,
                        }
                    )
                else:
                    yield scrapy.Request(
                        link,
                        callback=self.parse_article_quality,
                    )

    # current_link = 'https://zh.wikisource.org/wiki/八家後漢書/目錄'
    def parse_article_quality(self, response):
        quality_xpath = '//*[@id="mw-normal-catlinks"]/ul/li/a/text()'
        quality = response.xpath(quality_xpath).extract_first()
        if quality == '75%' or quality == '100':
            yield scrapy.Request(
                response.url,
                callback=self.parse_article,
            )
        else:
            yield scrapy.Request()

    # current_link = 'https://zh.wikisource.org/wiki/八家後漢書/目錄'
    def parse_article(self, response):
        # cat_xpath = '//div[@class="panel panel-default"]/div[@class="panel-body"]/ol/li[2]/a/text()'
        # sub_xpath = '//div[@class="panel panel-default"]/div[@class="panel-body"]/ol/li[3]/a/text()'
        # book_xpath = '//div[@class="panel panel-default"]/div[@class="panel-body"]/ol/li[@class="active"]/text()'
        main_cat = response.meta['main_cat']
        cat_text = response.meta['cat_text']
        sub_text = response.meta['sub_text']
        book_name = response.meta['book_text']

        en_bookstrip = book_name.replace('（', '').replace('）', '')
        en_book = '-'.join(
            PinyinHelper.convertToPinyinFromSentence(
                en_bookstrip,
                pinyinFormat=PinyinFormat.WITHOUT_TONE
            )
        )
        main_category = main_cat
        en_main_category = '-'.join(
            PinyinHelper.convertToPinyinFromSentence(
                main_category,
                pinyinFormat=PinyinFormat.WITHOUT_TONE
            )
        )
        category = cat_text
        en_category = '-'.join(
            PinyinHelper.convertToPinyinFromSentence(
                category,
                pinyinFormat=PinyinFormat.WITHOUT_TONE
            )
        )
        sub_category = sub_text
        en_sub_category = '-'.join(
            PinyinHelper.convertToPinyinFromSentence(
                sub_category,
                pinyinFormat=PinyinFormat.WITHOUT_TONE
            )
        )
        title = response.xpath('//h1[@id="firstHeading"]/text()').extract_first().split('/')[1]
        # en_title_strip = response.xpath('//h1[@id="firstHeading"]/text()').extract_first()
        en_title = '-'.join(
            PinyinHelper.convertToPinyinFromSentence(
                title,
                pinyinFormat=PinyinFormat.WITHOUT_TONE
            )
        ).replace('》', '')
        filename = '-'.join([en_category, en_sub_category, en_title])

        file_name = (base + category).replace('-', '')
        second_filename = (file_name + '/' + sub_category).replace('-', '')
        self.count_page += 1
        page = self.count_page

        if not os.path.exists(file_name):
            os.makedirs(file_name)
            if not os.path.exists(second_filename):
                item = WikiItem()
                os.makedirs(second_filename)
                item['path'] = second_filename

        with open('/Users/apple/Desktop/book2/书籍信息汇总10.json', 'a') as f:
            if page == 1:
                ch_name = book_name
                en_name = en_book.replace('-', '')
                if ch_name is not None:
                    dict = {"ch_name": ch_name, "type": "tw", "en_name": en_name}
                    line = json.dumps(dict, ensure_ascii=False) + ',' + "\n"
                    f.write(line)

        l = ItemLoader(item=WikiItem(), response=response)
        l.add_value('filename', filename)
        l.add_value('title', title)
        l.add_value('main_category', main_category)
        l.add_value('en_main_category', en_main_category)
        l.add_value('en_category', en_category)
        l.add_value('category', category)
        l.add_value('book', book_name)
        l.add_value('en_book', en_book)
        l.add_xpath('content', '//*[@id="mw-content-text"]/div/p/text()')
        l.add_value('en_title', en_title)
        l.add_value('en_sub_category', en_sub_category)
        l.add_value('sub_category', sub_category)
        l.add_value('path', second_filename)
        l.add_value('page', page)
        yield l.load_item()

        sub_url = response.xpath(
            '//div[@class="panel panel-default"]/div[@class="panel-body"]/ol/li[3]/a/@href'
        ).extract_first()
        next_xpath = '//div[@class="row"]/nav/ul[@class="pager"]/li/a'
        next_link = response.xpath(next_xpath).xpath('@href').extract()
        next_text = response.xpath(next_xpath).xpath('text()').extract()
        sum = len(next_link)
        if sum == 0:
            link = response.urljoin(sub_url)
            self.count_page = 0
            yield scrapy.Request(
                link,
                callback=self.parse_book,
                dont_filter=True,
            )
        elif sum == 1:
            if next_text[0] == '下一页':
                link = response.urljoin(next_link[0])
                yield scrapy.Request(
                    link,
                    callback=self.parse_article,
                    dont_filter=True,
                )
            else:
                link = response.urljoin(sub_url)
                self.count_page = 0
                yield scrapy.Request(
                    link,
                    callback=self.parse_book,
                    dont_filter=True,
                )
        elif sum == 2:
            if '下一页' not in next_text:
                link = response.urljoin(sub_url)
                self.count_page = 0
                yield scrapy.Request(
                    link,
                    callback=self.parse_book,
                    dont_filter=True,
                )
        elif sum == 3:
            link = next_link[2]
            link = response.urljoin(link)
            yield scrapy.Request(
                link,
                callback=self.parse_article,
                dont_filter=True,
            )