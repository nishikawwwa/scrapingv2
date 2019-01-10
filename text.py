#!/usr/bin/python
# -*- coding: utf-8 -*-

import MeCab

sentence = """AWSの有名なサービスにAmazon Elastic Compute Cloud (EC2) とAmazon Simple Storage Service (S3) がある。
これまでのクライアントが保有していた物理的なサーバファームと比較してAWSは大規模な計算処理能力を速やかに提供出来ることが強みである。"""

t = MeCab.Tagger()
t.parse('')
m = t.parseToNode(sentence)
m2 = t.parseToNode(sentence)
keywords = []
key = []
print(m)
while m:
    if m.feature.split(',')[0] == '名詞':
        keywords.append(m.surface)
    m = m.next


while m2:
    key.append(m2.surface)
    m2 = m2.next

print(keywords)
print('key',key)
