#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf8")

import requests
from bs4 import BeautifulSoup

class Dictionary():
    """ 字典类 """

    def lookup(self, word):
        self.init_soup(word)
        result = {
            'errinfo': self.get_errinfo(),
            'wordbook': self.get_phrs(),
            'web_trans': self.get_webtrans(),
            'web_phrase': self.get_webphrase(),
            'word_group': self.get_wordgroup(),
            'synonyms': self.get_synonyms(),
            'relword': self.get_relword(),
            'discriminate': self.get_discriminate(),
            'ebaike': self.get_ebaike(),
        }
        return result

    def init_soup(self, word):
        """ 初始化，抓取数据 """
        url = "http://dict.youdao.com/search?q="
        r = requests.get(url+word)
        self.soup = BeautifulSoup(r.text, 'html5lib')

    def get_errinfo(self):
        """ 是否拼写错误 """
        result = ''
        err_wrapper = self.soup.find(class_='typo-rel')
        if err_wrapper is not None:
            word = err_wrapper.find(class_='title').get_text().strip()
            content = err_wrapper.contents[-1].strip()
            result = '%s %s' % (word, content)

        return result

    def get_phrs(self):
        """ 基本释义 """
        result = {'title': '', 'pronounce': '', 'content':[]}
        phrs_list = self.soup.find(id='phrsListTab')
        if phrs_list is not None:
            title = phrs_list.find('h2', class_='wordbook-js')
            if title is not None:
                word = title.find(class_='keyword')
                result['title'] = word.get_text().strip() if word else ''
                pronounce = title.find(class_='phonetic')
                result['pronounce'] = pronounce.get_text().strip() if pronounce else ''

            try:
                content = phrs_list.find(class_='trans-container').find('ul')
                if content.find('li') is not None:
                    for wt in content.find_all('li'):
                        result['content'].append(wt.get_text().replace('\n', '').strip())

                elif content.find('p', class_='wordGroup') is not None:
                    for wt in content.find_all('p', class_='wordGroup'):
                        s = []
                        for k in wt.find_all('span'):
                            t = k.get_text().replace('\n', '').strip()
                            if t != '':
                                s.append(t)
                        result['content'].append(' '.join(s).replace('; ;', ';'))

            except:
                pass

        return result

    def get_webtrans(self):
        """ 网络释义 """
        result = []
        web_trans = self.soup.find(id='tWebTrans')
        if web_trans is not None:
            for wt in web_trans.find_all(class_='wt-container'):
                w = {
                    'title': wt.find(class_="title").find('span').string.strip(),
                    'content': wt.find(class_="collapse-content").get_text().replace('\n', '').strip(),
                }
                result.append(w)

        return result

    def get_webphrase(self):
        """ 网络短语 """
        result = []
        web_phrase = self.soup.find(id='webPhrase')
        if web_phrase is not None:
            for wg in web_phrase.find_all(class_="wordGroup"):
                w = {
                    'title': wg.find('span').get_text().strip(),
                    'content': '; '.join([s.strip() for s in wg.contents[-1].strip().split(';')]),
                }
                result.append(w)

        return result

    def get_synonyms(self):
        """ 同义词 """
        result = []
        synonyms = self.soup.find(id='synonyms')
        if synonyms is not None:
            for s in synonyms.find_all('li'):
                cts = s.next_sibling.next_sibling.find_all(class_='contentTitle')
                w = {
                    'title': s.get_text().strip(),
                    'content': ', '.join([k.get_text().replace('\n', '').replace(',', '').strip() for k in cts]),
                }
                result.append(w)

        return result

    def get_wordgroup(self):
        """ 词组短语 """
        return self.get_loop('wordGroup')

    def get_relword(self):
        """ 同根词 """
        return self.get_loop('relWordTab')

    def get_discriminate(self):
        """ 词语辨析 """
        result = []
        discri = self.soup.find(id='discriminate')
        if discri is not None:
            for wg in discri.find_all(class_='wordGroup'):
                w = {
                    'title': wg.find('span').get_text().strip(),
                    'content': wg.find('p').contents[-1].strip(),
                }
                result.append(w)

        return result

    def get_ebaike(self):
        """ 百科 """
        result = ''
        ebaike = self.soup.find(id='eBaike')
        if ebaike is not None:
            result = ebaike.find(id='bk').find(class_='content').find('p').get_text().strip()

        return result

    def get_loop(self, idname):
        result = []
        info = self.soup.find(id=idname)
        if info is not None:
            for wg in info.find_all(class_='wordGroup'):
                w = {
                    'title': wg.find('span').get_text().strip(),
                    'content': wg.contents[-1].strip(),
                }
                result.append(w)

        return result


class Printer():
    """ 显示类 """

    def show(self, result):
        # 错误信息
        if result['errinfo'] != '':
            print u'您要找的是不是: \033[1;35;40m%s\033[0m\n\n' % result['errinfo']

        # 基本释义
        print '\033[1;32;40m%(title)s\033[0m  \033[0;33;40m%(pronounce)s\033[0m' % result['wordbook']
        for wt in result['wordbook']['content']:
            print '%s' % wt

        self._print_list(result, 'web_trans', u'网络释义')
        self._print_list(result, 'web_phrase', u'网络短语')
        self._print_list(result, 'synonyms', u'同近义词')
        self._print_list(result, 'word_group', u'词组短语')
        self._print_list(result, 'relword', u'同根词')
        self._print_list(result, 'discriminate', u'词语辨析')

        # 百科
        if result['ebaike'] != '':
            self._print_title(u'有道百科')
            print '%s\n' % result['ebaike']

    def help(self):
        print '''
YouDao Dictionary v0.0.1
Usage:
    python dict.py word
    '''
    def _print_list(self, result, key, title):
        if len(result[key]) != 0:
            self._print_title(title)
            for wt in result[key]:
                print '\033[1;37;40m%(title)s:\033[0m %(content)s' % wt

    def _print_title(self, title):
        print '\n\033[1;31;40m%s\033[0m' % title


def main():
    printer = Printer()
    if len(sys.argv) < 2:
        printer.help()
        return

    word = ' '.join(sys.argv[1:])
    dictionary = Dictionary()
    result = dictionary.lookup(word)
    printer.show(result)


if __name__ == "__main__":
    main()

