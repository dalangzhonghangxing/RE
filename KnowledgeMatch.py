# _*_coding:utf-8_*_
import os

zjw_knowledge_path = "F:\学习\一课一练\组卷网平台知识点\初中.csv"
third_knowledge_path = "F:\学习\一课一练\沪教版数学知识点整理\preprocess"

stop_words = [u"的", "与", "问题", "和"]
knowledge_base = [u"科学计数法", "完全平方",
                  "平方差", "有理数", "无理数", "代数式", "三角形", "不等式", "相反数", "绝对值", "四边形", "轴对称", "不等式", "可能性",
                  "根式", "线段", "整除", "正数", "方程", "距离", "随机",
                  "梯形", "概率", "坐标", "倒数", "平方", "等式", "勾股", "平移", "相似",
                  "函数", "分式", "分数", "实数", "图形", "项式", "因式", "向量", "整式", "整数", "数轴", "乘方", "旋转", "对称",
                  "幂", "圆", "线", "角", "积", "比", "根", "体", "形", "弦", "弧", "扇", "图", "差", "频", "点"]
third_knowledges = []
zjw_knowledges = []


def getKey(k1, k2):
    flag1 = False
    flag2 = False
    key1 = None
    key2 = None
    for key in knowledge_base:
        if flag1 and flag2: break;
        if flag1 == False and k1.find(key) != -1:
            key1 = key
            flag1 = True;
        if flag2 == False and k2.find(key) != -1:
            key2 = key
            flag2 = True;
    return (key1, key2)


def calScore(k1, k2, baseScore):
    same = 0
    last = baseScore
    for c1 in k1:
        for c2 in k2:
            if c1 == c2:
                same = same + last
                last = last * 2
            else:
                last = baseScore
    return same


def similarity(k1, k2):
    for stopWord in stop_words:
        k1 = k1.replace(stopWord, "")
        k2 = k2.replace(stopWord, "")

    length = len(k1) + len(k2)
    score = 0
    (key1, key2) = getKey(k1, k2)

    if key1 != None and key2 != None:
        if key1 == key2:
            # print("关键词:" + key1 + "------>" + k1 + "\t" + k2)
            score = calScore(k1, k2, length)
        else:
            return 0
    else:
        score = calScore(k1, k2, 1)

    return score / length


def inKnowledgeBase(knowledge):
    for key in knowledge_base:
        if knowledge.find(key) != -1:
            return key
    return None


for root, dirs, files in os.walk(third_knowledge_path):
    for file in files:
        third_knowledges.append(file.split(".")[0].split("：")[0])

file = open(zjw_knowledge_path, "r", encoding="utf-8")
for line in file:
    zjw_knowledges.append(line.split(",")[1])

for third_knowledge in third_knowledges:
    maxSimilarity = -1
    candinate = -1;
    for zjw_knowledge in zjw_knowledges:
        currentSimilarity = similarity(zjw_knowledge.split("-")[0], third_knowledge)
        if currentSimilarity > maxSimilarity:
            maxSimilarity = currentSimilarity
            candinate = zjw_knowledges.index(zjw_knowledge)
    if (maxSimilarity <= 1):
        print(third_knowledge + "->" + zjw_knowledges[candinate], maxSimilarity)
# print(similarity("统计与概率", "事件的概率"))
# for third_knowledge in third_knowledges:
#     if third_knowledge.find("的") != -1:
#         print(third_knowledge.split("的")[0])

# for zjw_knowledge in zjw_knowledges:
#     key_knowledge = inKnowledgeBase(zjw_knowledge)
#     if key_knowledge == None:
# print(key_knowledge + ":" + zjw_knowledge)
# print("未分配:" + zjw_knowledge)
# else:
#     print("未分配:" + zjw_knowledge)
