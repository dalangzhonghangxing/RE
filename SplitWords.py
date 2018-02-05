import jieba
import os
import Utils

third_knowledge_path = "F:\学习\一课一练\沪教版数学知识点整理\preprocess"
splitFilePrefix = "F:\学习\一课一练\沪教版数学知识点整理\spiltWords\\"

stopWords = ["（", "）", "\n", ".", "．", ")", "(", "“", "”", "，", "。", ",", "；", "：", "、", " ", "的", "是", "且", "如果",
             "等于", "就", "惟一", "唯一"]

saveFromStopWords = ["幂", "圆", "线", "角", "积", "比", "根", "体", "形", "弦", "弧", "扇", "图", "差", "频", "点"]

jieba.load_userdict("wordBase.txt")


def splitWords(words, knowledge):
    words = list(jieba.cut(words))
    content = ""
    for word in words:
        if word not in stopWords and (len(word) > 1 or word in saveFromStopWords):
            content = content + word + " "
    # print(content)
    Utils.writeFile(splitFilePrefix + knowledge, content)


# for root, dirs, files in os.walk(third_knowledge_path):
#     for file in files:
#         currentFile = open(third_knowledge_path + "\\" + file, "r", encoding="utf-8")
#         content = ""
#         for line in currentFile:
#             content = content + line
#         splitWords(content, file)
#         # if len(content) < 20:
#         #     print(file)
words = jieba.cut("等边三角形的判定")
for w in words:
    print(w)

