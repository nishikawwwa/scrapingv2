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
from collections import Counter
import pandas as pd

#USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'

def scraping(domain):
    # requestsの場合
    #headers={'User-Agent':USER_AGENT}
    #HTML = requests.get(url, headers=headers)

    try:
        url = 'http://' + domain
        HTML = requests.get(url)
        print('http')
    except:
        url = 'https://' + domain
        HTML = requests.get(url)
        print('https')

    #mecab用処理
    url_soup = lxml.html.fromstring(HTML.content)
    lim = url_soup.body
    text = lim.xpath('//text()[name(..)!="script"][name(..)!="style"]')
    text = np.array(text)
    text = [e for e in text if not e.startswith('\n')]
    text = [e for e in text if not e.startswith('\t')]
    text = [e for e in text if not e.startswith('\r')]

    return text

def mecab(sentence):

    word = []

    t = MeCab.Tagger()
    for each_sentence in sentence:

        t.parse('')
        m = t.parseToNode(each_sentence)
        #print(m)


        while m:
            word.append(m.surface)
            m = m.next
    return word

df = pd.read_excel('20190110.xlsx', skiprows=0, header=0, index_col=2)
print(df)

data = np.array(df)
print(data)
count = 0
#ドメイン抽出
domain_list = []
for i in data:
    domain_list.append(i[1])

word_list = []
for j in domain_list:
    print(j)
    try:
        text = scraping(j)
        word = mecab(text)
        word_list.append(word)
        count += 1
    except:
        pass

print(word_list)

'''
text, links,images = scraping('otonanswer.jp')
print(text)
word = mecab(text)
print(word)
'''
