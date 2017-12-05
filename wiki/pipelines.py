# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json


class WikiPipeline(object):

    def process_item(self, item, spider):
        filename = item['en_book'].replace('-', '')
        filename = filename + '(' + item['book'] + ')'
        filename += '.jl'
        filename = item['path'] + '/' + filename
        print(filename)
        content = dict(item)
        del content['path']
        line = json.dumps(content, indent=4, ensure_ascii=False) + "\n"
        with open(filename, 'a') as self.fp:
            self.fp.write(line)
        if item['content'] == item['title'] or item['content'] is None:
            with open('/users/apple/desktop/问题书籍.json', 'a') as f:
                line = filename
                f.write(line)
        return item

    if __name__ == '__main__':
        process_item()