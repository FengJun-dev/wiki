import re
import scrapy
from ChineseTone import *
from scrapy.loader import ItemLoader
from wiki.filter_quality import book_reach_quality, article_reach_quality
from wiki.items import WikiItem
from wiki.log import log_low_quality_article, log_book_info

base = '/users/Apple/desktop/WikiBook2/'
log_filename = base + 'log/不符合质量要求的书籍.json'
log_book_file = base + '书籍信息汇总.json'


class WikiSpider(scrapy.Spider):
    name = 'wiki'
    allow_domains = ['zh.wikisource.org']
    # category_list = ['古文', '史書', '宗教典籍', '小说', '戲曲', '教科書', '散文', '譯文', '醫家', '韵文']
    start_urls = [
        'https://zh.wikisource.org/wiki/Wikisource:%E5%8F%B2%E6%9B%B8',
    ]

    def __init__(self):
        self.count_book = 0
        self.count_catalog = 0
        self.article_id = 0

    # current_link = 'https://zh.wikisource.org/wiki/Wikisource:史書'
    def parse(self, response):
        main_link = response.url

        category = response.xpath('//*[@id="firstHeading"]/text()').extract_first()
        book_xpath = '//*[@id="mw-content-text"]/div/ul/li/a'
        book_xpath2 = '//*[@id="mw-content-text"]/div/ul/li/ul/li/a'

        book = response.xpath(book_xpath + '|' + book_xpath2)
        book_list = [book]

        for book_link in book_list:
            link = book_link.xpath('@href').extract()
            # book_name = book_link.xpath('text()').extract()
            book_title = book_link.xpath('@title').extract()

            if link is not None:
                if self.count_book < len(link):
                    link = response.urljoin(link[self.count_book])
                    book_name = book_title[self.count_book]

                    if '页面不存在' in book_name:
                        self.count_book += 1
                        yield scrapy.Request(
                            main_link,
                            callback=self.parse,
                            dont_filter=True,
                        )

                    yield scrapy.Request(
                        link,
                        meta={
                            'main_link': main_link,
                            'category': category,
                            'book_name': book_name,
                        },
                        callback=self.parse_bookcat,
                    )
                else:
                    return

    # current_link = 'https://zh.wikisource.org/wiki/史記'
    def parse_bookcat(self, response):
        main_link = response.meta['main_link']
        category = response.meta['category']
        book_name = response.meta['book_name']

        book_link = response.url

        catalog_xpath = '//*[@id="mw-content-text"]/div/ul/li'
        quality_xpath = '//*[@id="mw-normal-catlinks"]/ul/li[1]/a/text()'

        xpath = '//*[@id="toc"]/ul/li[1]/a/span[2]/text()'

        catalog = response.xpath(catalog_xpath)
        catalog_list = [catalog]

        content_xpath = '//*[@id="mw-content-text"]/div/p'
        content = response.xpath(content_xpath).xpath('string(.)').extract()
        if content:
            new_content = []
            for i in content:
                if len(i) != 0:
                    new_content.append(i)

        if not book_reach_quality(response, quality_xpath):
            self.count_book += 1
            link = response.urljoin(main_link)
            yield scrapy.Request(
                link,
                callback=self.parse,
                dont_filter=True,
            )

        if not catalog_list:
            yield scrapy.Request(
                main_link,
                meta={
                    'main_link': main_link,
                    'category': category,
                    'book_name': book_name,
                },
                callback=self.parse_article,
            )

        for catalog_link in catalog_list:
            link = catalog_link.xpath('a/@href').extract()
            title = catalog_link.xpath('a/text()').extract()
            title_content = catalog_link.xpath('text()').extract()

            if link is not None:
                if self.article_id < len(link):
                    link = response.urljoin(link[self.article_id])
                    title = title[self.article_id]
                    if self.article_id < len(title_content):
                        title_content = title_content[self.article_id].strip()
                        title = title + ':' + title_content
                    else:
                        title = title

                    yield scrapy.Request(
                        link,
                        meta={
                            'main_link': main_link,
                            'book_link': book_link,
                            'category': category,
                            'book_name': book_name,
                            'title': title,
                        },
                        callback=self.parse_article2,
                    )
                else:
                    self.count_book += 1
                    self.article_id = 0
                    yield scrapy.Request(
                        main_link,
                        callback=self.parse,
                        dont_filter=True,
                    )

    # current_link = 'https://zh.wikisource.org/wiki/史記/卷001'
    def parse_article(self, response):
        main_link = response.meta['main_link']

        main_category = '史部'
        en_main_category = '-'.join(
            PinyinHelper.convertToPinyinFromSentence(
                main_category,
                pinyinFormat=PinyinFormat.WITHOUT_TONE
            )
        )

        category = response.meta['category']
        en_category = '-'.join(
            PinyinHelper.convertToPinyinFromSentence(
                category.replace(':', ''),
                pinyinFormat=PinyinFormat.WITHOUT_TONE
            )
        )

        book_name = response.meta['book_name']
        en_bookstrip = book_name.strip().replace('（', '').replace('）', '')
        en_book = '-'.join(
            PinyinHelper.convertToPinyinFromSentence(
                en_bookstrip,
                pinyinFormat=PinyinFormat.WITHOUT_TONE
            )
        )

        quality_xpath = '//*[@id="mw-normal-catlinks"]/ul/li/a/text()'
        if not article_reach_quality(response, quality_xpath):
            self.count_book += 1
            log_low_quality_article(log_filename, book_name, en_book)
            link = response.urljoin(main_link)
            yield scrapy.Request(
                link,
                callback=self.parse,
                dont_filter=True,
            )

        title = response.meta['title']
        if title:
            title = title
        else:
            title = response.xpath('//*[@id="mw-content-text"]/div/table[1]/tr/td[2]/text()').extract_first().strip()
        en_title = '-'.join(
            PinyinHelper.convertToPinyinFromSentence(
                title.replace(':', ''),
                pinyinFormat=PinyinFormat.WITHOUT_TONE
            )
        ).replace('》', '')

        content_xpath = '''
        //*[@id="mw-content-text"]/div/p|
        //span[@class="mw-headline"]'''

        content = response.xpath(content_xpath).xpath('string(.)').extract()
        new_content = []
        for i in content:
            if len(i) != 0:
                if '[' and ']' not in i:
                    new_content.append(i)
                else:
                    r = re.compile('\[.*?\]')
                    new = r.sub('', i)
                    new_content.append(new)

        reference_xpath = '//*[@id="mw-content-text"]/div/ol[@class="references"]'
        reference = response.xpath(reference_xpath).xpath('string(.)').extract()

        new_content.extend(reference)

        # '//*[@id=".E6.9C.AC.E7.B4.80"]
        filename = '-'.join([en_main_category, en_category, en_title])

        file_name = (base + main_category).replace('-', '')
        second_filename = (file_name + '/' + category).replace('-', '')
        article_id = 1
        log_book_info(log_book_file, article_id, book_name, en_book)

        l = ItemLoader(item=WikiItem(), response=response)
        l.add_value('filename', filename)
        l.add_value('title', title)
        l.add_value('main_category', main_category)
        l.add_value('en_main_category', en_main_category)
        l.add_value('en_category', en_category)
        l.add_value('category', category)
        l.add_value('book', book_name)
        l.add_value('en_book', en_book)
        l.add_value('content', new_content)
        l.add_value('en_title', en_title)
        # l.add_value('en_sub_category', en_sub_category)
        # l.add_value('sub_category', sub_category)
        l.add_value('path', second_filename)
        l.add_value('article_id', article_id)
        yield l.load_item()

        next_link = main_link
        self.count_book += 1
        yield scrapy.Request(
            next_link,
            callback=self.parse,
            dont_filter=True,
        )

    def parse_article2(self, response):
        book_link = response.meta['book_link']
        main_link = response.meta['main_link']

        main_category = '史部'
        en_main_category = '-'.join(
            PinyinHelper.convertToPinyinFromSentence(
                main_category,
                pinyinFormat=PinyinFormat.WITHOUT_TONE
            )
        )

        category = response.meta['category']
        en_category = '-'.join(
            PinyinHelper.convertToPinyinFromSentence(
                category.replace(':', ''),
                pinyinFormat=PinyinFormat.WITHOUT_TONE
            )
        )

        book_name = response.meta['book_name']
        en_bookstrip = book_name.strip().replace('（', '').replace('）', '')
        en_book = '-'.join(
            PinyinHelper.convertToPinyinFromSentence(
                en_bookstrip,
                pinyinFormat=PinyinFormat.WITHOUT_TONE
            )
        )

        '''quality_xpath = '//*[@id="mw-normal-catlinks"]/ul/li/a/text()'
        if not article_reach_quality(response, quality_xpath):
            self.count_book += 1
            log_low_quality_article(log_filename, book_name, en_book)
            link = response.urljoin(main_link)
            yield scrapy.Request(
                link,
                callback=self.parse,
                dont_filter=True,
            )'''

        title = response.meta['title']
        if title:
            title = title
        else:
            title = response.xpath('//*[@id="mw-content-text"]/div/table[1]/tr/td[2]/text()').extract_first().strip()
        en_title = '-'.join(
            PinyinHelper.convertToPinyinFromSentence(
                title.replace(':', ''),
                pinyinFormat=PinyinFormat.WITHOUT_TONE
            )
        ).replace('》', '')

        content_xpath = '''
        //*[@id="mw-content-text"]/div/p|
        //span[@class="mw-headline"]'''
        content = response.xpath(content_xpath).xpath('string(.)').extract()
        new_content = []
        for i in content:
            if len(i) != 0:
                if '[' and ']' not in i:
                    new_content.append(i)
                else:
                    r = re.compile('\[.*?\]')
                    new = r.sub('', i)
                    new_content.append(new)

        reference_xpath = '//*[@id="mw-content-text"]/div/ol[@class="references"]'
        reference = response.xpath(reference_xpath).xpath('string(.)').extract()

        new_content.extend(reference)

        # '//*[@id=".E6.9C.AC.E7.B4.80"]

        filename = '-'.join([en_main_category, en_category, en_title])

        file_name = (base + main_category).replace('-', '')
        second_filename = (file_name + '/' + category[0:4]).replace('-', '')
        self.article_id += 1
        article_id = self.article_id
        log_book_info(log_book_file, article_id, book_name, en_book)

        l = ItemLoader(item=WikiItem(), response=response)
        l.add_value('filename', filename)
        l.add_value('title', title)
        l.add_value('main_category', main_category)
        l.add_value('en_main_category', en_main_category)
        l.add_value('en_category', en_category)
        l.add_value('category', category)
        l.add_value('book', book_name)
        l.add_value('en_book', en_book)
        l.add_value('content', new_content)
        l.add_value('en_title', en_title)
        # l.add_value('en_sub_category', en_sub_category)
        # l.add_value('sub_category', sub_category)
        l.add_value('path', second_filename)
        l.add_value('article_id', article_id)
        yield l.load_item()

        next_link = response.urljoin(book_link)
        yield scrapy.Request(
            next_link,
            meta={
                'main_link': main_link,
                'category': category,
                'book_name': book_name,
                'title': title,
            },
            callback=self.parse_bookcat,
            dont_filter=True,
        )






"""# current_link = 'https://zh.wikisource.org/wiki/Wikisource:%E5%8F%B2%E6%9B%B8'
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
"""