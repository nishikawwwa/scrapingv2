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
save_path = '/home/a_nishikawa/scrapingv2/data/top100/'
mecab_save_path = '/home/a_nishikawa/scrapingv2/data/learn_data/'
top10save_path = '/home/a_nishikawa/scrapingv2/data/'
def scraping(domain):
    # requestsの場合
    #headers={'User-Agent':USER_AGENT}
    #HTML = requests.get(url, headers=headers)

    try:
        url = 'http://' + domain
        HTML = requests.get(url)
        #print('http')
    except:
        url = 'https://' + domain
        HTML = requests.get(url)
        #print('https')

    #mecab用処理
    url_soup = lxml.html.fromstring(HTML.content)
    lim = url_soup.body
    text = lim.xpath('//text()[name(..)!="script"][name(..)!="style"]')
    text = np.array(text)
    text = [e for e in text if not e.startswith('\n')]
    text = [e for e in text if not e.startswith('\t')]
    text = [e for e in text if not e.startswith('\r')]

    return text

def format_text(texts):
    '''
    MeCabに入れる前のツイートの整形方法例
    '''

    texts=re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", texts)
    texts=re.sub(r'[!-/:-@[-`{-~]', "", texts)#半角記号,数字,英字
    texts=re.sub(r'[︰-＠]', "", texts)#全角記号
    texts=re.sub('\n', " ", texts)#改行文字
    texts=re.sub(r'[「」.,:【】〈〉]', "", texts)#改行文字

    return texts



def mecab(sentence):
    word = []

    t = MeCab.Tagger()
    for each_sentence in sentence:
        each_sentence = format_text(each_sentence)
        t.parse('')
        m = t.parseToNode(each_sentence)
        #print(m)


        while m:
            if m.feature.split(',')[0] == '名詞' or m.feature.split(',')[0] == '形容詞' or m.feature.split(',')[0] == '動詞' or m.feature.split(',')[0] == '形容動詞語幹':
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

#domain_list = domain_list[0:10]

word_list = []
true_list = []
un_word_list = np.array([])
for counts, j in enumerate(domain_list):
    list = []
    print(j)
    try:
        text = scraping(j)
        word = mecab(text)
        true_list.append(j)
        np.savetxt(mecab_save_path + str(counts) + '.txt', word,fmt='%s', delimiter=',')
        #print('word',word)
        #print('word')
        unique_word = np.array(word)
        #格サイト内の重複除去
        unique_word = np.unique(unique_word)
        un_word_list = np.append(un_word_list, unique_word)
        word_list.append(word)
        count += 1
    except:
        pass

#print('unique',unique_word)
#print(len(word_list))
#print(len(un_word_list))
#全てのサイト内で重複除去
unique_word_list = np.unique(un_word_list)
#print(len(unique_word_list))
remove_list = np.array([])
for i in unique_word_list:
    #全てのサイトに含まれているのか，除去する単語リスト
    if np.sum(un_word_list == i) >= len(true_list) * 0.5:
        remove_list = np.append(remove_list, i)

print('re',remove_list)

top_list = [[]]
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
    #print('dd', data)
    mm = Counter(data)
    top_count = 100
    if len(set(data)) < 100:
        #print('111100000000000')
        top_count = len(set(data))

    link_top = [true_list[i]]

    for cou in range(top_count):
        link_top.append(mm.most_common()[cou][0])

    top_list.append(link_top)
    link_top = np.array(link_top)
    #np.savetxt(save_path + str(i) + 'body.txt', link_top,fmt='%s', delimiter=',')

#print('uni', top_list)
#print('top', len(top_list[0]))
#print('top', len(top_list[1]))

column_name = ['site_name']
for i in range(1,101):
    column_name.append('top' + str(i))
print(column_name)
df =pd.DataFrame(data = top_list, columns = column_name)

df.to_csv('top100.csv')


#tf-idf抽出
tfidf_vectorizer = TfidfVectorizer(input ='filename', norm='l2')


files = ['data/learn_data/' + path for path in os.listdir('data/learn_data')]
files = sorted(files)
tfidf = tfidf_vectorizer.fit_transform(files).toarray()
#print(files)

index = tfidf.argsort(axis=1)[:,::-1]
feature_names = np.array(tfidf_vectorizer.get_feature_names())
feature_words = feature_names[index]


n = 10
m = len(os.listdir('data/learn_data'))

tfidf_data = [[]]
for i,fwords in enumerate(feature_words[:m,:n]):
    print(i)
    tfidf_words = np.array([true_list[i]])
    tfidf_words = np.append(tfidf_words, fwords)
    tfidf_words = tfidf_words.tolist()
    tfidf_data.append(tfidf_words)

tfcolumn_name = ['site_name']
for i in range(1,11):
    tfcolumn_name.append('top' + str(i))
print(tfidf_data)
tf_df =pd.DataFrame(data = tfidf_data, columns = tfcolumn_name)

tf_df.to_csv(top10save_path + 'tf_idf_top10.csv')

'''
text, links,images = scraping('otonanswer.jp')
print(text)
word = mecab(text)
print(word)
'''
