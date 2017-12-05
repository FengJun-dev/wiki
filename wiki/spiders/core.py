def parse_article(self, base, response):
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
            category,
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
        )

    title = response.meta['title']
    if title:
        title = title
    else:
        title = response.xpath('//*[@id="mw-content-text"]/div/table[1]/tr/td[2]/text()').extract_first().strip()
    en_title = '-'.join(
        PinyinHelper.convertToPinyinFromSentence(
            title,
            pinyinFormat=PinyinFormat.WITHOUT_TONE
        )
    ).replace('》', '')

    content_xpath = '''
    //*[@id="mw-content-text"]/div/p/span/span/text()|
    //*[@id="mw-content-text"]/div/p/text()|
    //*[@id="mw-content-text"]/div/p[4]/span[5]/text()
    '''
    content = response.xpath(content_xpath).extract()

    content_head = response.xpath('//span[@class="mw-headline"]/text()').extract()
    # '//*[@id=".E6.9C.AC.E7.B4.80"]
    filename = '-'.join([en_main_category, en_category, en_title])

    file_name = (base + main_category).replace('-', '')
    second_filename = (file_name + '/' + category).replace('-', '')
    article_id = self.article_id + 1
    log_book_info(article_id, book_name, en_book)

    l = ItemLoader(item=WikiItem(), response=response)
    l.add_value('filename', filename)
    l.add_value('title', title)
    l.add_value('main_category', main_category)
    l.add_value('en_main_category', en_main_category)
    l.add_value('en_category', en_category)
    l.add_value('category', category)
    l.add_value('book', book_name)
    l.add_value('en_book', en_book)
    l.add_xpath('content', content)
    l.add_value('en_title', en_title)
    # l.add_value('en_sub_category', en_sub_category)
    # l.add_value('sub_category', sub_category)
    l.add_value('path', second_filename)
    l.add_value('article_id', article_id)
    yield l.load_item()