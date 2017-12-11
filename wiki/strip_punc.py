def strip_punc(book_name, title):
    en_bookstrip = book_name.strip().replace('（', '').replace('）', '').replace('《', '').replace('》', '').replace(' ','').replace(
        '，', '').replace('/', '')
    en_title_strip = title.replace('《', '').replace('》', '').replace(' ', '').replace('，', '').replace('/', '')
