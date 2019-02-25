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
import urllib
import datetime

__VERSION__ = '0.0.1'
__AUTHOR__ = 'Akari Nishikawa (a_nishikawa@fancs.com)'

HOME = '/home/a_nishikawa'
LOGDIR = os.path.join(HOME, 'log')

save_path = HOME + '/scrapingv2/data/'
USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'


def scraping(url):
    """
    スクレイピング
    """
    headers={'User-Agent':USER_AGENT}
    HTML = requests.get(url, headers=headers)
    #mecab用処理
    text_soup = lxml.html.fromstring(HTML.content)
    soup_body = text_soup.body
    text = soup_body.xpath('//text()[name(..)!="script"][name(..)!="style"]')
    #\nがsoup_bodyに含まれているため，除去
    text = ''.join(text)
    text = text.replace('\n', '')
    #text = [e for e in text if not e.startswith('\n')]

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
        elif link.get("src").endswith(".gif"):
        	images.append(link.get("src"))
        elif link.get("src").endswith(".svg"):
        	images.append(link.get("src"))
        elif link.get("src").endswith(".tif"):
        	images.append(link.get("src"))

    return text,links,images


def using_mecab(keyword,sentence):
    '''
    mecabで品詞抽出
    '''
    noun = 0
    word = 0
    adjective = 0
    adjective_verb = 0
    verb = 0
    keyword_cnt = []
    for i in range(len(keyword)):
        keyword_cnt.append(0)

    t = MeCab.Tagger()
    #each_sentenceには単語ではなく，文が格納
    for each_sentence in sentence:
        t.parse('')
        node = t.parseToNode(each_sentence)
        while node:
            if node.feature.split(',')[0] == '名詞':
                noun += 1
            elif node.feature.split(',')[0] == '形容詞':
                adjective += 1
            elif node.feature.split(',')[0] == '形容動詞語幹':
                adjective_verb +=1
            elif node.feature.split(',')[0] == '動詞':
                verb += 1
            word += 1
            #count keyword
            for j,each_keyword in enumerate(keyword):
                if node.surface == each_keyword:
                    keyword_cnt[j] += 1
            node = node.next

    #キーワードマッチ数
    return noun,word,adjective, adjective_verb, verb,keyword_cnt


def get_top_url(url):
    """
    サイトのトップページurl抽出
    """
    parse_url = urllib.parse.urlparse(url)
    top_url = parse_url.scheme + '://' + parse_url.netloc
    return top_url

def extract_major(site_name,link,top_count):
    """
    リンク先分類
    """
    site_major = get_top_url(site_name)
    link_list = []
    in_link = 0
    page_link_num = 0
    for count, ll in enumerate(link):
        if ll != None:
            link_major_1 = get_top_url(ll)
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
    #外部リンク内のtop
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
    parser.add_argument('--keyword', nargs='*',help = 'Count keyword')
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
    noun, word,adjective, adjective_verb, verb,keyword_cnt = using_mecab(keyword,text)

    link_top,in_link_cnt,out_link_cnt,page_link_cnt = extract_major(site_name,links,10)
    image_top,image_in_link_cnt,image_out_link_cnt,img_link_cnt = extract_major(site_name,images,10)

    data_list = [[site_name, word, noun,adjective,adjective_verb,verb, keyword_cnt,in_link_cnt,out_link_cnt,page_link_cnt, link_top, image_top],[0,0,0,0,0,0,0,0,0]]
    df = pd.DataFrame(data_list, columns = ['url', 'word','noun','adjective','adjective_verb','verb','keyword_match','in_link','out_link','pagein_link','link_top','img_top'])
    df = df.drop(1)
    now = datetime.datetime.now()
    print(keyword_cnt)
    #df.to_csv(dir_path + '{0:%Y%m%d%H%M}'.format(now)+'.csv')
    print('Directory of File >>>', dir_path+ '{0:%Y%m%d%H%M}'.format(now)+'.csv')
if __name__ == '__main__':
    main()
