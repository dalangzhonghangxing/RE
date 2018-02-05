import Utils

leafKnowledges = []
mappedKnowledges = []

file = open("F:\学习\一课一练\实验结果\组卷网初中知识点映射结果.txt", "r", encoding="utf-8")
for line in file:
    mappedKnowledges.append(line)

file = open("F:\学习\一课一练\组卷网平台知识点\初中叶子知识点.csv", "r", encoding="utf-8")
for line in file:
    leafKnowledges.append(line.split(",")[1])

content = ""
for mappedKnowledge in mappedKnowledges:
    if mappedKnowledge.split(":")[0] in leafKnowledges:
        content += mappedKnowledge
        leafKnowledges.remove(mappedKnowledge.split(":")[0])

Utils.writeFile("F:\学习\一课一练\实验结果\映射的叶子知识点.txt", content)
