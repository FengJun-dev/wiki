def book_reach_quality(response, quality_xpath=None):
    quality = response.xpath(quality_xpath).extract_first()
    if quality:
        if quality.isnumeric():
            if quality == '100%' or quality == '75%':
                return True
            else:
                return False
        else:
            return True


def article_reach_quality(response, quality_xpath):
    if book_reach_quality(response, quality_xpath):
        return True
    quality = response.xpath(quality_xpath).extract_first()
    if quality == '100%' or quality == '75%':
        return True
    else:
        return False
