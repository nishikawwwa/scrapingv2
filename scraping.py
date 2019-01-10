# coding: UTF-8
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

save_path = '/home/a_nishikawa/scrapingv2/data/'

USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'

def scraping(url):
    # requestsの場合
    headers={'User-Agent':USER_AGENT}
    HTML = requests.get(url, headers=headers)
    #mecab用処理
    url_soup = lxml.html.fromstring(HTML.content)
    lim = url_soup.body
    text = lim.xpath('//text()[name(..)!="script"][name(..)!="style"]')
    text = np.array(text)
    text = [e for e in text if not e.startswith('\n')]

    return text



def mecab(keyword):
    sentence = scraping('http://blog.livedoor.jp/kinisoku/archives/5013621.html')
    #print(sentence)

    noun = []
    word = []

    t = MeCab.Tagger()
    for each_sentence in sentence:

        t.parse('')
        m = t.parseToNode(each_sentence)
        m2 = t.parseToNode(each_sentence)
        print(m)
        while m:
            if m.feature.split(',')[0] == '名詞':
                noun.append(m.surface)
            m = m.next


        while m2:
            word.append(m2.surface)
            m2 = m2.next


    #キーワードマッチ数
    keyword_match = len(sentence[sentence== keyword])

    return noun,word,keyword_match

noun, word, keyword_match = mecab('私')

print('keywords',len(noun))
print('key',len(word))
print('keyword_match',keyword_match)
