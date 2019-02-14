# -*- coding: utf-8 -*-
import argparse
from pprint import pprint
import requests
from bs4 import BeautifulSoup
import numpy as np
import os
import lxml.html
import sys
import pandas as pd
import MeCab
from collections import Counter
import re

__VERSION__ = '0.0.1'
__AUTHOR__ = 'Akari Nishikawa (a_nishikawa@fancs.com)'

HOME = '/home/a_nishikawa'
LOGDIR = os.path.join(HOME, 'log')

save_path = '/home/a_nishikawa/scrapingv2/data/'


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


def url_major(site_name):
    """
    サイトのトップページurl抽出
    """
    split_sitename = len(site_name.split('/'))
    site_major = site_name.rsplit('/',split_sitename - 3)
    return site_major[0]

def extract_major(site_name,link,top_count):
    """
    リンク先分類
    """
    site_major = url_major(site_name)
    link_list = []
    in_link = 0
    page_link_num = 0
    for count, ll in enumerate(link):
        if ll != None:
            link_major_1 = url_major(ll)
            if link_major_1 != None:
                try:
                    if link_major_1[0] == '#':
                        #ページ内リンク
                        page_link_num += 1
                    elif link_major_1 != site_major:
                        if link_major_1[0] == 'h':
                            #外部リンクだけ
                            link_list.append(link_major_1)
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

def print_version():
    """
    Scriptのバージョンを表示する
    """
    print("Version: {}".format(__VERSION__))

def main():
    parser = argparse.ArgumentParser(description='サイトの特徴量抽出')
    parser.add_argument('--url', help = 'URL of scraping site')
    parser.add_argument('--keyword', help = 'Count keyword')
    parser.add_argument('--dir', help = 'Save dir_path')
    args = parser.parse_args()
    site_name = args.url
    keyword = args.keyword
    if args.dir != None:
        dir_path = args.dir
    else:
        dir_path = os.getcwd() + '/'
    print_version()

    text,links,images = scraping(site_name)
    noun, word, keyword_match,adjective, adjective_verb, verb = mecab(keyword,text)

    link_top,link_in_link,link_out_link,page_link_num = extract_major(site_name,links,10)
    image_top,image_in_link,image_out_link,img_link_num = extract_major(site_name,images,10)

    data_list = [[site_name, word, noun,adjective,adjective_verb,verb, keyword_match,link_in_link,link_out_link,page_link_num, link_top, image_top],[0,0,0,0,0,0,0,0,0]]
    df = pd.DataFrame(data_list, columns = ['url', 'word','noun','adjective','adjective_verb','verb','keyword_match','in_link','out_link','pagein_link','link_top','img_top'])
    df = df.drop(1)
    df.to_csv(dir_path + 'db.csv')
    print('Directory of File >>>', dir_path+ 'db.csv')

if __name__ == '__main__':
    main()
