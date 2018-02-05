import jieba

stopWords = ["（", "）", "\n", ".", "．", ")", "(", "“", "”", "，", "。", ",", "；", "：", "、", " ", "的", "是", "且", "如果",
             "等于", "就", "惟一", "唯一"]

saveFromStopWords = ["幂", "圆", "线", "角", "积", "比", "根", "体", "形", "弦", "弧", "扇", "图", "差", "频", "点"]

jieba.load_userdict("wordBase.txt")

def splitWords(content):
    words = list(jieba.cut(content))
    res = []
    for word in words:
        if word not in stopWords and (len(word) > 1 or word in saveFromStopWords):
            res.append(word)
    return res
