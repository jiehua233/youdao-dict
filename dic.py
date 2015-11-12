#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf8")

import requests
from bs4 import BeautifulSoup


def main():
    word = 'pythoo'
    result = look_up(word)
    show2screen(result)


def show2screen(result):
    if result['errinfo'] != '':
        print u'您要找的是不是: ' + result['errinfo']

    print '%(title)s  %(pronounce)s' % result['wordbook']
    for wt in result['wordbook']['content']:
        print '%s' % wt


def look_up(word):
    soup = get_soup(word)

    result = {}
    # 错误信息
    result['errinfo'] = get_errinfo(soup)
    # 基本资料
    result['wordbook'] = get_phrs(soup)
    # 网络释义, 网络短语 'web_trans', 'web_phrase'
    result.update(get_webtrans(soup))
    # 同义词
    result['synonyms'] = get_synonyms(soup)
    # 百科
    result['ebaike'] = get_ebaike(soup)

    return result


def get_soup(word):
    url = "http://dict.youdao.com/search?q="
    r = requests.get(url+word)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def get_errinfo(soup):
    result = ''
    # 判断是否错误
    err_wrapper = soup.find(class_='typo-rel')
    if err_wrapper is not None:
        word = err_wrapper.find(class_='title').get_text().strip()
        content = err_wrapper.contents[-1].strip()
        result = '%s %s' % (word, content)

    return result


def get_phrs(soup):
    result = {'title': '', 'pronounce': '', 'content':[]}
    # 基本资料
    phrs_list = soup.find(id='phrsListTab')
    if phrs_list is not None:
        title = phrs_list.find('h2', class_='wordbook-js')
        result['title'] = title.find(class_='keyword').get_text().strip()
        result['pronounce'] = title.find(class_='phonetic').get_text().strip()
        content = phrs_list.find(class_='trans-container').find('ul')
        ct_li = content.find_all('li')
        ct_p = content.find_all('p', class_='wordGroup')
        ct_list = ct_li if len(ct_li) != 0 else ct_p
        for wt in ct_list:
            result['content'].append(wt.get_text().strip())

    return result


def get_webtrans(soup):
    result = {'web_trans': [], 'web_phrase': []}
    web_trans = soup.find(id='tWebTrans')
    if web_trans is not None:
        # 网络释义
        for wt in web_trans.find_all(class_='wt-container'):
            w = {
                'title': wt.find(class_="title").find('span').string.strip(),
                'content': wt.find(class_="collapse-content").get_text().strip(),
            }
            result['web_trans'].append(w)

        # 网络短语
        for wg in web_trans.find(id='webPhrase').find_all(class_="wordGroup"):
            w = {
                'title': wg.find('span').get_text().strip(),
                'content': '; '.join([s.strip() for s in wg.contents[-1].strip().split(';')]),
            }
            result['web_phrase'].append(w)

    return result


def get_synonyms(soup):
    result = []
    # 同义词
    synonyms = soup.find(id='eTransform')
    if synonyms is not None:
        synonyms = synonyms.find(id='synonyms')
        if synonyms is not None:
            for s in synonyms.find('ul').find_all('li'):
                cts = s.next_sibling.next_sibling.find_all(class_='contentTitle')
                w = {
                    'title': s.get_text().strip(),
                    'content': ', '.join([k.get_text().strip() for k in cts]),
                }
                result.append(w)

    return result


def get_ebaike(soup):
    result = ''
    # 百科
    ebaike = soup.find(id='eBaike')
    if ebaike is not None:
        result = ebaike.find(id='bk').find(class_='content').find('p').get_text().strip()

    return result


if __name__ == "__main__":
    main()

