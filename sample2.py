# -*- coding: utf-8 -*-
from selenium import webdriver
from pprint import pprint
import requests
from bs4 import BeautifulSoup
import numpy as np
import os
from time import sleep
import lxml.html
from pyvirtualdisplay import Display
import sys
import pandas as pd
import MeCab
from collections import Counter
import pandas as pd
import re

__VERSION__ = '0.0.1'
__AUTHOR__ = 'Akari Nishikawa (a_nishikawa@fancs.com)'

HOME = '/home/a_nishikawa'
LOGDIR = os.path.join(HOME, 'log')

save_path = '/home/a_nishikawa/scrapingv2/data/'


def url():
    """
    引数
    """
    args = sys.argv
    url = args[1]
    return url

site_name = url()
split_sitename = len(site_name.split('/'))
site_major = site_name.rsplit('/',split_sitename - 3)


def extract_pos(t,each_sentence,list,pos):
    """
    品詞抽出
    """
    m = t.parseToNode(each_sentence)
    while m:
        if m.feature.split(',')[0] == pos:
            list.append(m.surface)
        m = m.next
    return list

def scraping(url):
    """
    スクレイピング
    """
    HTML = requests.get(url)
    #mecab用処理
    url_soup = lxml.html.fromstring(HTML.content)
    lim = url_soup.body
    text = lim.xpath('//text()[name(..)!="script"][name(..)!="style"]')
    text = np.array(text)
    text = [e for e in text if not e.startswith('\n')]

    soup = BeautifulSoup(HTML.text, 'lxml')
    #リンク
    links = [a.get("href") for a in soup.find_all("a")]
    text_data = BeautifulSoup(HTML.content, 'html.parser')
    with open('body.html', mode='w', encoding = 'utf-8') as f:
        f.write(text_data.prettify())
    #画像
    images = []
    for link in soup.find_all("img"):
        if link.get("src").endswith(".jpg"):
            images.append(link.get("src"))
        elif link.get("src").endswith(".png"):
        	images.append(link.get("src"))

    return text,links,images


def mecab(keyword,sentence):
    '''
    mecabで品詞抽出
    '''
    noun = []
    word = []
    adjective = []
    adjective_verb = []
    verb = []

    t = MeCab.Tagger()
    for each_sentence in sentence:
        t.parse('')

        noun = extract_pos(t,each_sentence,noun,'名詞')
        adjective = extract_pos(t,each_sentence,adjective,'形容詞')
        adjective_verb = extract_pos(t,each_sentence,adjective_verb,'形容動詞語幹')
        verb = extract_pos(t,each_sentence,verb,'動詞')

        #単語数
        m2 = t.parseToNode(each_sentence)
        while m2:
            word.append(m2.surface)
            m2 = m2.next

    #キーワードマッチ数
    keyword_match = len(sentence[sentence== keyword])
    return len(noun),len(word),keyword_match,len(adjective), len(adjective_verb), len(verb)
'''

def link_destination(link,split_sitename,site_major):
    link_list = []
    in_link = 0
    page_link_num = 0
    for count, ll in enumerate(link):
        if ll != None:
            split_num = len(ll.split('/'))
            link_major = ll.rsplit('/',split_num - 3)
            link_major_1 = link_major[0]
            #print('site_major', site_major[0])
            if link_major_1 != None:
                #print('1',link_major_1,'1')
                try:
                    #print('link1', str(link_major_1[0]))
                    if link_major_1[0] == '#':
                        page_link_num += 1
                    elif link_major[0] != site_major[0]:
                        if link_major_1[0] == 'h':
                            link_list.append(link_major[0])
                    else:
                        #内部リンク数カウント
                        in_link += 1
                except:
                    pass

        #外部リンク数
        out_link = len(link_list)
        return link_list, page_link_num, out_link

'''
def extract_major(link,top_count):
    """
    リンク先分類
    """
    link_list = []
    in_link = 0
    page_link_num = 0
    for count, ll in enumerate(link):
        if ll != None:
            split_num = len(ll.split('/'))
            link_major = ll.rsplit('/',split_num - 3)
            link_major_1 = link_major[0]
            #print('site_major', site_major[0])
            if link_major_1 != None:
                #print('1',link_major_1,'1')
                try:
                    #print('link1', str(link_major_1[0]))
                    if link_major_1[0] == '#':
                        page_link_num += 1
                    elif link_major[0] != site_major[0]:
                        if link_major_1[0] == 'h':
                            #外部リンクだけ
                            link_list.append(link_major[0])
                    else:
                        #内部リンク数カウント
                        in_link += 1
                except:
                    pass

        #外部リンク数
        out_link = len(link_list)

    #uniqueなリンク数が10以下の場合
    if len(set(link_list)) < 10:
        top_count = len(set(link_list))

    mm = Counter(link_list)
    #外部リンクないのtop
    link_top = []
    for i in range(top_count):
        link_top.append(mm.most_common()[i][0])

    return link_top, in_link, out_link,page_link_num


def main():
    text,links,images = scraping(site_name)
    noun, word, keyword_match,adjective, adjective_verb, verb = mecab('名無し',text)
    print(noun)

    link_top,link_in_link,link_out_link,page_link_num = extract_major(links,10)
    print(link_in_link)


if __name__ == '__main__':
    main()
