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
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import imp

#USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'

HOME = '/home/a_nishikawa'
save_path = HOME + '/scrapingv2/data/top100/'
mecab_save_path = HOME + '/scrapingv2/data/learn_data/'
top10save_path = HOME + '/scrapingv2/data/'


def scrape(domain):
    """
    スクレイピング
    """
    # requestsの場合
    #headers={'User-Agent':USER_AGENT}
    #HTML = requests.get(url, headers=headers)

    try:
        url = 'http://' + domain
        HTML = requests.get(url)
    except:
        url = 'https://' + domain
        HTML = requests.get(url)

    #mecab用処理
    url_soup = lxml.html.fromstring(HTML.content)
    lim = url_soup.body
    text = lim.xpath('//text()[name(..)!="script"][name(..)!="style"]')
    for count, each_text in enumerate(text):
        text[count] = each_text.replace('\n','')
    return text


def shape_format(texts):
    '''
    MeCabに入れる前のの整形
    '''
    texts=re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", texts)
    texts=re.sub(r'[!-/:-@[-`{-~]', "", texts)#半角記号,数字,英字
    texts=re.sub(r'[︰-＠]', "", texts)#全角記号
    texts=re.sub('\n', " ", texts)#改行文字
    texts=re.sub(r'[「」.,:【】〈〉]', "", texts)#改行文字

    return texts


def extract_keyword(sentence):
    """
    mecabでトークン分割
    """
    word = []
    t = MeCab.Tagger()
    for each_sentence in sentence:
        each_sentence = shape_format(each_sentence)
        t.parse('')
        node = t.parseToNode(each_sentence)
        while node:
            if node.feature.split(',')[0] == '名詞' or node.feature.split(',')[0] == '形容詞' or node.feature.split(',')[0] == '動詞' or node.feature.split(',')[0] == '形容動詞語幹':
                word.append(node.surface)
            node = node.next
    return word


def extract_effect_url(domain_list):
    """
    アクセス出来るサイトとサイト内のuniqueな単語抽出
    """
    word_list = []
    effect_url = []
    un_word_list = np.array([])
    for count, domain in enumerate(domain_list):
        try:
            text = scrape(domain)
            word = extract_keyword(text)
            effect_url.append(domain)
            np.savetxt(mecab_save_path + str(count) + '.txt',word, fmt='%s',delimiter=',')
            #各サイト内の重複単語除去
            unique_word = np.array(word)
            unique_word = np.unique(unique_word)
            un_word_list = np.append(un_word_list, unique_word)
            word_list.append(word)
        except:
            pass
    return effect_url, un_word_list, word_list


def extract_remove_word(un_word_list,effect_url):
    """
    除去する単語抽出
    """
    #全てのサイトでのuniqueな単語抽出
    unique_word_all = np.unique(un_word_list)
    #除去する単語抽出
    remove_list = np.array([])
    ratio = 0.5
    for i in unique_word_all:
        if np.sum(un_word_list == i) >= len(effect_url) * ratio:
            remove_list = np.append(remove_list, i)
    return remove_list


def remove_word(effect_url,word_list,remove_list):
    """
    各サイトからremove_listに含まれる単語を除去&top100抽出
    """
    top_list = [[]]
    #各サイトからremove_listに含まれる単語を除去
    for i, data in enumerate(word_list):
        remove_uni_list = np.array([])
        #remove単語ごとに除去
        for j in remove_list:
            data = [i for i in data if not i  == j]

        mm = Counter(data)
        top_count = 100
        #wordが100以下の場合
        if len(set(data)) < top_count:
            top_count = len(set(data))

        link_top = [effect_url[i]]

        for cou in range(top_count):
            link_top.append(mm.most_common()[cou][0])

        top_list.append(link_top)
        link_top = np.array(link_top)
    return top_list


def extract_tfidf(effect_url):
    """
    tfidf抽出
    """
    tfidf_vectorizer = TfidfVectorizer(input ='filename', norm='l2')


    files = ['data/learn_data/' + path for path in os.listdir('data/learn_data')]
    files = sorted(files)
    tfidf = tfidf_vectorizer.fit_transform(files).toarray()

    index = tfidf.argsort(axis=1)[:,::-1]
    feature_names = np.array(tfidf_vectorizer.get_feature_names())
    feature_words = feature_names[index]


    n = 10
    m = len(os.listdir('data/learn_data'))

    tfidf_data = [[]]
    for i,fwords in enumerate(feature_words[:m,:n]):
        tfidf_words = np.array([effect_url[i]])
        tfidf_words = np.append(tfidf_words, fwords)
        tfidf_words = tfidf_words.tolist()
        tfidf_data.append(tfidf_words)
    return tfidf_data


def main():
    df = pd.read_excel('20190110.xlsx', skiprows=0, header=0, index_col=2)
    data = np.array(df)
    count = 0
    #ドメイン抽出
    domain_list = []
    for i in data:
        domain_list.append(i[1])
    #domain_list = domain_list[0:10]
    domain_list.append('blog.livedoor.jp/kinisoku/archives/5013621.html')
    effect_url, un_word_list, word_list = extract_effect_url(domain_list)
    remove_list = extract_remove_word(un_word_list,effect_url)
    top_list = remove_word(effect_url,word_list,remove_list)
    column_name = ['site_name']
    for i in range(1,101):
        column_name.append('top' + str(i))
    df =pd.DataFrame(data = top_list, columns = column_name)
    df.to_csv('top100.csv')

    #tfidf抽出
    tfidf_data = extract_tfidf(effect_url)
    tfcolumn_name = ['site_name']
    for i in range(1,11):
        tfcolumn_name.append('top' + str(i))
    tf_df =pd.DataFrame(data = tfidf_data, columns = tfcolumn_name)

    tf_df.to_csv(top10save_path + 'tf_idf_top10.csv')


if __name__ == '__main__':
    main()
