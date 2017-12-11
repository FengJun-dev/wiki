def book_reach_quality(response, quality_xpath):
    quality = response.xpath(quality_xpath).extract_first()
    if quality:
        if quality.split('%')[0].isnumeric():
            if quality == '100%' or quality == '75%':
                return 'high quality'
            else:
                return 'low quality'
        else:
            return 'can not judge'
    else:
        return 'can not judge'


def article_reach_quality(response, quality_xpath, article_id=None):
    quality = response.xpath(quality_xpath).extract_first()
    if quality:
        if quality.split('%')[0].isnumeric():
            if quality == '100%' or quality == '75%':
                return 'high quality'
            else:
                return 'low quality'
        else:
            return 'low quality'
    # elif article_id == 1 and quality is None:
        # return 'high quality'
    else:
        return 'low quality'
