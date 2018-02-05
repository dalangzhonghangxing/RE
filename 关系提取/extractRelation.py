import 关系提取.splitContent as sc

knowledges = []
bikeWords = []
contents = []
relation = [[]]
path = u"F:\学习\一课一练\实验结果\知识点内容"

# 将知识点的映射，爬下来的内容存下来
file = open("F:\学习\一课一练\实验结果\映射的叶子知识点.txt", "r", encoding="utf-8")
for knowledge in file:
    # 存知识点
    knowledges.append(knowledge.split(":")[0])
    # 存知识点对应的百度词条
    bikeWord = set()
    for bk in knowledge.split(":")[1].replace("\n", "").split(" "):
        if bk == "":
            continue
        if (bk.find(">") != -1):
            bikeWord.add(bk.split(">")[0])
        elif (bk.find("#") != -1):
            bikeWord.add(bk.split("#")[0])
        else:
            bikeWord.add(bk)
    bikeWords.append(bikeWord)

    # 存内容，将LemmaSummary与mainContent分开存放
    f = open(path + "\\" + knowledge.split(":")[0] + ".txt", "r", encoding="utf-8")
    flag = False
    lcontent = ""
    mcontent = ""
    for line in f:
        if (line.find("LemmaSummary") != -1):
            flag = True
        elif (line.find("mainContent") != -1):
            flag = False
        else:
            if flag:
                lcontent += line
            else:
                mcontent += line
    content = {"LemmaSummary": sc.splitWords(lcontent), "mainContent": sc.splitWords(mcontent)}
    contents.append(content)


# 比较两个知识点映射到的百度词条是不是同一个
def equal(s1, s2):
    if len(s1) == 1 and len(s1) == len(s2) and s2.issubset(s1):
        return True
    else:
        return False


# 计算得分
def calScore(content, bikeWords):
    llen = len(content["LemmaSummary"])
    mlen = len(content["mainContent"])
    l = 0
    m = 0
    for bw in bikeWords:
        if llen > 0:
            l += content["LemmaSummary"].count(bw)
        if mlen > 0:
            m += content["mainContent"].count(bw)
        if llen + mlen == 0:
            return 0
    return l + m


# 计算第i,j两个知识点之间的得分
def calRelationScore(i, j):
    if i == j:
        return 0
    bwi = bikeWords[i]
    bwj = bikeWords[j]
    if equal(bwi, bwj) == False:  # 如果这两个知识点不同，则计算它们
        return calScore(contents[i], bwj)
    else:
        return 0


for i, _ in enumerate(knowledges):
    r = knowledges[i] + ":"
    flag = False
    for j, _ in enumerate(knowledges):
        score = calRelationScore(i, j)
        if (score >= 10 * len(knowledges[j])):  # 如果评分大于5，则j是i的前驱
            r += knowledges[j] + " "
            flag = True
    if flag == True:
        print(r + "\n")
