def book_reach_quality(response, quality_xpath=None):
    quality = response.xpath(quality_xpath).extract_first()
    if quality:
        if quality.isnumeric():
            if quality == '100%' or quality == '75%':
                return 'high quality'
            else:
                return 'low quality'
        else:
            return 'can not judge'
    else:
        return 'can not judge'


def article_reach_quality(response, quality_xpath):
    quality = response.xpath(quality_xpath).extract_first()
    if quality:
        if quality == '100%' or quality == '75%':
            return 'high_quality'
        else:
            return 'low_quality'
    else:
        return 'low_quality'

