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
save_path = '/home/a_nishikawa/scrapingv2/data/top100/'
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
#print(df)

data = np.array(df)
#print(data)
count = 0
#ドメイン抽出
domain_list = []
for i in data:
    domain_list.append(i[1])

domain_list = domain_list[0:3]

word_list = []
un_word_list = np.array([])
for j in domain_list:
    list = []
    print(j)
    try:
        text = scraping(j)
        word = mecab(text)
        #print('word',word)
        unique_word = np.array(word)
        unique_word = np.unique(unique_word)
        un_word_list = np.append(un_word_list, unique_word)
        word_list.append(word)
        count += 1
    except:
        pass

#print(len(word_list))
print(len(un_word_list))
#uniqueなlist
unique_word_list = np.unique(un_word_list)
print(len(unique_word_list))
remove_list = np.array([])
for i in unique_word:
    if np.sum(un_word_list == i) == 3:
        remove_list = np.append(remove_list, i)


top_list = []
#サイトごと
for i, data in enumerate(word_list):
    remove_uni_list = np.array([])
    #remove単語ごとに除去
    for j in remove_list:
        data = [i for i in data if not i  == j]


        '''
        mm = Counter(remove_uni)
        top_count = 100
        if len(set(remove_uni)) < 100:
            top_count = len(set(remove_uni))

        #外部リンクないのtop
        link_top = []
        for i in range(top_count):
            link_top.append(mm.most_common()[i][0])

        '''
    print('dd', data)
    mm = Counter(data)
    top_count = 100
    if len(set(data)) < 100:
        print('111100000000000')
        top_count = len(set(data))

    link_top = []
    for i in range(top_count):
        link_top.append(mm.most_common()[i][0])
    np.savetxt(save_path + i + 'body.txt', link_top,fmt='%s', delimiter=',')
    top_list.append(link_top)

print('uni', remove_uni_list)
print('top', len(top_list[0]))
print('top', len(top_list[1]))

'''
text, links,images = scraping('otonanswer.jp')
print(text)
word = mecab(text)
print(word)
'''
