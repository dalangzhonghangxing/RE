#!/usr/bin/python
# coding:utf-8
import sys
import importlib

importlib.reload(sys)
import os
from gensim import corpora, models
import numpy as np
from sklearn import cluster
from sklearn.preprocessing import StandardScaler
import Utils


def get_stop_words_set(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        stop_words = set()
        for line in file:
            stop_words.add(line.strip())
        return stop_words


# 将所有百科文档的单词，去停用词之后，以每个文档为一行存入words_list矩阵
def get_words_list_knowledges(file_package_name, stop_word_file):
    stop_words_set = get_stop_words_set(stop_word_file)
    knowledges = []
    print("共计导入 %d 个停用词" % len(stop_words_set))
    word_list = []
    for root, dirs, files in os.walk(file_package_name):
        for file in files:
            currentFile = open(file_package_name + "/" + file, "r", encoding="utf-8")
            knowledges.append(file.split(".")[0])
            file_word_list = []
            for line in currentFile:
                tmp_list = line.split(" ")
                for tmp_word in tmp_list:
                    if tmp_word.strip() not in stop_words_set:
                        file_word_list.append(tmp_word)
            word_list.append(file_word_list)
    return word_list, knowledges


def LDA(topic_number):
    word_list_knowledges = get_words_list_knowledges("../splitedBikeContent", "../chineseStopWords.txt")  # 读取单词以及知识点列表
    word_list = word_list_knowledges[0]
    word_dict = corpora.Dictionary(word_list)  # 生成文档的词典，每个词与一个整型索引值对应
    corpus_list = [word_dict.doc2bow(text) for text in word_list]  # 词频统计，转化成空间向量格式
    lda = models.ldamodel.LdaModel(corpus=corpus_list, id2word=word_dict, num_topics=topic_number, alpha='auto')
    # for topic in lda.show_topics():
    #     print(topic)
    lda.save("LDA_model.txt")

    # 将每篇文档的主题分布转换成size为topic_number的向量
    documents_topics = []
    for corpus in corpus_list:
        row = np.zeros(topic_number)  # 生成长度为topic_number的向量
        topics = lda.get_document_topics(corpus)  # 获得一篇文档的主题分布
        for topic in topics:  # topic是一个元组，[主题编号，权重]
            row[topic[0]] = topic[1]
        documents_topics.append(row)

    # save documents_topics
    content = ""
    for row in documents_topics:
        for col in row:
            content += str(col) + " "
        content += "\n"
    Utils.writeFile("documents_topics.txt", content)


# load documents_topic from file
def loadDocumentsTopics():
    documents_topics = []
    file = open("documents_topics.txt", "r", encoding="utf-8")
    for line in file:
        document = []
        line = line.replace(" \n", "")
        for number in line.split(" "):
            document.append(float(number))
        documents_topics.append(document)
    return documents_topics


def clusterDocument(cluster_number):
    ''''''
    # load documents_topics
    documents_topics = loadDocumentsTopics()

    # load knowledges
    word_list_knowledges = get_words_list_knowledges("../splitedBikeContent", "../chineseStopWords.txt")  # 读取单词以及知识点列表
    knowledges = word_list_knowledges[1]

    clusters = cluster.k_means(documents_topics, cluster_number)  # 使用K-means聚类

    # standardData = StandardScaler().fit_transform(documents_topics)
    # db = cluster.DBSCAN(eps=0.1).fit(standardData)
    # core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    # core_samples_mask[db.core_sample_indices_] = True
    # labels = db.labels_

    # 将知识点按照类别归类
    dict = {}
    for i in range(0, cluster_number):
        dict[i] = []

    for index, type in enumerate(clusters[1]):
        dict[type].append(knowledges[index])

    for key in dict.keys():
        print(dict[key])


topic_number = 6
K = 5
LDA(topic_number)
clusterDocument(K)
# clusterDocument(topic_number, K)
# clusterDocument(topic_number,5)
# clusterDocument(topic_number,5)
