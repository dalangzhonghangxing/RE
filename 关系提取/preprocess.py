import Utils
import 关系提取.bikeOperation as bo
import os
import numpy as np
import jieba


# Loading bikewords from the specified file
def getBikeWordSet():
    bikeWordSet = set()
    # for fileName in os.listdir("../bikewordContent"):
    #     bikeWordSet.add(fileName.split(".")[0])
    for line in open(u"初中知识点_目录.txt", "r", encoding="utf-8"):
        bikewords = line.split(" ")
        for bikeword in bikewords:
            if bikeword != "" and bikeword != "\n":
                bikeWordSet.add(bikeword.replace("\n", ""))
    print(len(bikeWordSet), " words are loaded")
    return bikeWordSet


# According the bike words to crawl content
def getBikeWordContent():
    # bikeWordSet = getBikeWordSet()
    bikeWordSet = ['频数']
    exceptedWords = []
    i = 1
    titleSet = set()
    for bikeword in bikeWordSet:
        try:
            res = bo.parseContent(bikeword)
        except:
            exceptedWords.append(bikeword)

        Utils.writeFile("../bikewordContent/" + bikeword + ".txt", res[1])
        titleSet = titleSet | res[0]
        print(i)
        i += 1
    print(exceptedWords)
    titles = ""
    for title in titleSet:
        titles += title + " "
    Utils.writeFile("titles.txt", titles)


# Generating wordBase.txt to split words of bike content
def generateWordBase():
    words = getBikeWordSet()
    print("The number of BikeBords is", len(words))
    c = ""
    for word in words:
        c += word + "\n"
    Utils.writeFile("wordBase.txt", c)


# Generating bikeWords.txt to save the order of bike words
def generateBikeWords():
    words = getBikeWordSet()
    c = ""
    for word in words:
        c += word.replace("\n", "") + " "
    Utils.writeFile("bikeWords.txt", c)


def isContain(title, keyWord):
    if title.find(keyWord) != -1:
        return True
    return False


# 对百度百科的内容进行分词
def splitWords():
    jieba.load_userdict("wordBase.txt")
    for fileName in os.listdir("../bikewordContent"):
        splitOneDocument(fileName)


def splitOneDocument(fileName):
    # 先将知识点的内容进行拼接
    content = ""
    file = open(os.path.join('%s%s' % ("../bikewordContent/", fileName)), 'r', encoding="utf-8")
    for line in file:
        content += line

    # 进行分词
    words = list(jieba.cut(content))

    # 进行存储
    content = ""
    for w in words:
        content += w + " "
    Utils.writeFile("../splitedBikeContent/" + fileName, content)


# 生成百度百科知识点的包含矩阵
def generateOccurrenceMatrix():
    jieba.load_userdict("wordBase.txt")
    # 先读出所有百科词语
    file = open("知识点目录顺序.txt", 'r', encoding='utf-8')
    line = file.readline()
    bikewords = line.split(" ")

    # 初始化包含矩阵
    matrix = np.zeros((len(bikewords), len(bikewords)), dtype=np.int)

    j = 1
    for fileName in os.listdir("../splitedBikeContent"):
        currentBikeWord = fileName.split(".")[0].replace("\n", "")
        print(j, currentBikeWord)
        j = j + 1
        # 读取每个知识点对应的分词后的百度百科
        content = []
        file = open(os.path.join('%s%s' % ("../splitedBikeContent/", fileName)), 'r', encoding="utf-8")
        for line in file:
            for w in line.split(" "):
                content.append(w)

        for i, bikeword in enumerate(bikewords):
            count = content.count(bikeword)
            matrix[bikewords.index(currentBikeWord)][i] = count
        # print(matrix[bikewords.index(currentBikeWord)])

    np.save("occurrenceMatrix.npy", matrix)


# 爬取组卷网映射的所有的百科词条的百科内容
# getBikeWordSet() # get the number of bike words
# getBikeWordContent()  # crawl the content of bike words
# generateWordBase() # generate the wordBase.txt,which used to split words
# generateBikeWords() # generate the order of bike words(bikeWords.txt)
# splitWords()  # split words according to wordBase.txt
# generateOccurrenceMatrix() # generate occurrence matrix according to splited words
splitOneDocument("频数.txt")
