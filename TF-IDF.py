# _*_coding:utf-8_*_
import os
import math

splitFilePrefix = u"F:\学习\一课一练\沪教版数学知识点整理\spiltWords"

contentList = []


def tf_idf(content):
    wordMap = dict()
    wordSet = set()
    for w in content:
        wordSet.add(w)
    for w in wordSet:
        cc = 0
        for c in contentList:
            if w in c:
                cc += 1
        wordMap[w] = content.count(w) / len(wordSet) * math.log(len(contentList) / cc, 10)
        print w
    return wordMap


for root, dirs, files in os.walk(splitFilePrefix):
    for file in files:
        currentFile = open(os.path.join(splitFilePrefix, file), "r")
        content = u""
        for line in currentFile:
            content = content + line.decode("utf-8")
        contentList.append(content.split(u" "))

for content in contentList:
    tfResult = tf_idf(content)
    print tfResult
