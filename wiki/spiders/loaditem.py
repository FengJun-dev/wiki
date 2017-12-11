from wiki.items import WikiItem
from scrapy.loader import ItemLoader


def load_item(l, filename, title, main_category,en_main_category, en_category, category,
              book_name, en_book, content, en_title, second_filename, article_id, reference=None):
    l.add_value('filename', filename)
    l.add_value('title', title)
    l.add_value('main_category', main_category)
    l.add_value('en_main_category', en_main_category)
    l.add_value('en_category', en_category)
    l.add_value('category', category)
    l.add_value('book', book_name)
    l.add_value('en_book', en_book)
    l.add_value('content', content)
    l.add_value('en_title', en_title)
    # l.add_value('en_sub_category', en_sub_category)
    # l.add_value('sub_category', sub_category)
    l.add_value('path', second_filename)
    l.add_value('article_id', article_id)
    l.add_value('reference', reference)
    yield l.load_item()
