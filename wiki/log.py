import json

# log_low_quality_filename = '/users/Apple/desktop/WikiBook2/log/不符合质量要求的书籍.json'
# log_book_file = '/Users/apple/Desktop/WikiBook2/书籍信息汇总.json'


def log_low_quality_article(log_low_quality_filename, book_name, en_book):
    with open(log_low_quality_filename, 'r') as json_file:
        if len(json_file.read()) == 0:
            with open(log_low_quality_filename, 'w') as f:
                ch_name = book_name
                en_name = en_book.replace('-', '')
                if ch_name is not None:
                    log_info = [{"ch_name": ch_name, "type": "tw", "en_name": en_name}]
                    line = json.dumps(log_info, indent=4, ensure_ascii=False)
                    f.write(line)

        with open(log_low_quality_filename, 'r') as g:
            data = json.load(g)
            ch_name = book_name
            en_name = en_book.replace('-', '')
            log_info = {"ch_name": ch_name, "type": "tw", "en_name": en_name}
            # print('log_info: %s' % log_info)
            for i in data:  # 做了两次
                if en_book == i['en_name']:
                    # print('en_book: %s' % en_book)
                    print("k['en_name']: %s" % i['en_name'])
                    break
                else:
                    data.append(log_info)
                # print('data: %s' % data)
            new_data = []
            for k in data:
                if k not in new_data:
                    new_data.append(k)
            # print('new_data: %s' % new_data)
            with open(log_low_quality_filename, 'w') as f:
                new_data = json.dumps(new_data, indent=4, ensure_ascii=False)
                f.write(new_data)


def log_book_info(log_book_file, article_id, book_name, en_book):
    # if not os.path.exists(log_book_file):
        # os.mknod(log_book_file)
    with open(log_book_file, 'r') as f:
        if article_id == 1:
            if len(f.read()) == 0:
                ch_name = book_name
                en_name = en_book.replace('-', '')
                with open(log_book_file, 'w') as g:
                    if ch_name is not None:
                        log_info = [{"ch_name": ch_name, "type": "tw", "en_name": en_name}]
                        line = json.dumps(log_info, indent=4, ensure_ascii=False)
                        g.write(line)
            with open(log_book_file, 'r') as h:
                data = json.load(h)
                ch_name = book_name
                en_name = en_book.replace('-', '')
                log_info = {"ch_name": ch_name, "type": "tw", "en_name": en_name}
                data.append(log_info)
                new_data = []
                for i in data:
                    if i not in new_data:
                        new_data.append(i)
                with open(log_book_file, 'w') as k:
                    new_data = json.dumps(new_data, indent=4, ensure_ascii=False)
                    k.write(new_data)
        else:
            return
