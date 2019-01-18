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

    soup = BeautifulSoup(HTML.text, 'lxml')
    #リンク
    links = [a.get("href") for a in soup.find_all("a")]

    #画像
    images = []
    for link in soup.find_all("img"):
        if link.get("src").endswith(".jpg"): # imgタグ内の.jpgであるsrcタグを取得
            images.append(link.get("src")) # imagesリストに格納
        elif link.get("src").endswith(".png"): # imgタグ内の.pngであるsrcタグを取得
        	images.append(link.get("src"))

    return text,links,images



def mecab(keyword):
    sentence,link,images = scraping(site_name)
    #print(sentence)

    noun = []
    word = []
    adjective = []
    adjective_verb = []
    verb = []

    t = MeCab.Tagger()
    for each_sentence in sentence:

        t.parse('')
        m = t.parseToNode(each_sentence)
        m2 = t.parseToNode(each_sentence)
        m3 = t.parseToNode(each_sentence)
        m4 = t.parseToNode(each_sentence)
        m5 = t.parseToNode(each_sentence)
        print(m)
        while m:
            if m.feature.split(',')[0] == '名詞':
                noun.append(m.surface)
            m = m.next


        while m2:
            word.append(m2.surface)
            m2 = m2.next

        while m3:
            if m3.feature.split(',')[0] == '形容詞':
                adjective.append(m3.surface)
            m3 = m3.next

        while m4:
            if m4.feature.split(',')[0] == '形容動詞語幹':
                adjective_verb.append(m4.surface)
            m4 = m4.next

        while m5:
            if m5.feature.split(',')[0] == '動詞':
                verb.append(m5.surface)
            m5 = m5.next



    #キーワードマッチ数
    keyword_match = len(sentence[sentence== keyword])

    return len(noun),len(word),keyword_match,link,images, len(adjective), len(adjective_verb), len(verb)


site_name = 'http://blog.livedoor.jp/kinisoku/archives/5013621.html'
noun, word, keyword_match,link,images,adjective, adjective_verb, verb = mecab('私')

split_sitename = len(site_name.split('/'))
site_major = site_name.rsplit('/',split_sitename - 3)

print('keywords',noun)
print('key',word)
print('keyword_match',keyword_match)
print('images',images)
#リンク先の分類
def extract_major(link,top_count):
    link_list = []
    in_link = 0
    for count, ll in enumerate(link):
        if ll != None:
            split_num = len(ll.split('/'))
            link_major = ll.rsplit('/',split_num - 3)
            if link_major != site_major:
                #外部リンクだけ
                link_list.append(link_major[0])
            else:
                #内部リンク数カウント
                in_link += 1

        #外部リンク数
        out_link = len(link_list)

    #uniqueなリンク数が10以下の場合
    if len(set(link_list)) < 10:
        top_count = len(set(link_list))

    mm = Counter(link_list)

    link_top = []
    for i in range(top_count):
        link_top.append(mm.most_common()[i][0])

    return link_top, in_link, out_link

link_top,link_in_link,link_out_link = extract_major(link,10)

image_top,image_in_link,image_out_link = extract_major(images,10)
print(link_top)
print(image_top)


data_list = [[site_name, word, noun,adjective,adjective_verb,verb, keyword_match,, link_top, image_top],[0,0,0,0,0,0]]

df = pd.DataFrame(data_list, columns = ['url', 'word','noun','adjective','adjective_verb','verb','keyword_match','link_top','img_top'])

df = df.drop(1)
df.to_csv('db.csv')
'''
for links in link:
    print('links',links)
    split_num = links.split('/')
    link_major = links.rsplit('/',len(split_num) - 3)
    link_list.append(link_major[0])

print(link_list)
'''
