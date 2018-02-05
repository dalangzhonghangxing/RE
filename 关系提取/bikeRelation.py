import numpy as np
import Utils


# 初始化函数
def init(cluster_path, concurrent_matrix_path, bike_words_path, zeta=1):
    # 加载共现矩阵
    matrix = np.load(concurrent_matrix_path)
    clusters = []
    groupFile = open(cluster_path, "r", encoding="utf-8")
    for line in groupFile:
        clusters.append(line.split(" "))

    file = open(bike_words_path, 'r', encoding='utf-8')
    line = file.readline()
    bikewords = line.split(" ")
    return matrix, zeta, clusters, bikewords


# matrix是共现矩阵
# A、B分别是知识点的索引
def RefD(matrix, A, B, max_time=15):
    # A知识点在所有知识点中的重要程度，即第A列的和
    impA = 0
    for i in matrix[:, A]:
        if i != 0:
            impA += min(i, 5)

    # A知识点在AB共现的百科中的重要程度，即AB两列都不为0的行的值中，A的值的和
    impAtoAB = 0
    for i in range(0, matrix.shape[0] - 1):
        if matrix[i][B] != 0 and matrix[i][A] != 0:
            impAtoAB += min(matrix[i][A], 5)

    # B知识点在所有知识点中的重要程度，即第B列的和
    impB = 0
    for i in matrix[:, B]:
        if i != 0:
            impB += min(i, 5)

    # B知识点在AB共现的百科中的重要程度
    impBtoAB = 0
    for i in range(0, matrix.shape[0] - 1):
        if matrix[i][B] != 0 and matrix[i][A] != 0:
            impBtoAB += min(matrix[i][B], 5)

    if impA == 0:
        IA = 0
    else:
        IA = impAtoAB / impA
    if impB == 0:
        IB = 0
    else:
        IB = impBtoAB / impB

    # print("impA", impA)
    # print("impAtoAB", impAtoAB)
    # print("impB", impB)
    # print("impBtoAB", impBtoAB)
    return IA - IB


# calculate the refd score between knowledge_A and knowledge_B
def calRefDScore(bikewords, matrix, knowledge_A, knowledge_B, max_time=15):
    A = bikewords.index(knowledge_A.replace("\n", ""))
    B = bikewords.index(knowledge_B.replace("\n", ""))
    if A != B:
        return RefD(matrix, A, B, max_time=15), A, B
    else:
        return 0.0, A, B


# 使用RefD方生成关系矩阵
def generateRelationByRefD(zeta=0.5, max_time=15):
    init_value = init("初中知识点_目录.txt", "occurrenceMatrix.npy", "bikeWords.txt", zeta)
    matrix = init_value[0]
    zeta = init_value[1]
    clusters = init_value[2]
    bikewords = init_value[3]

    relationMatrix = np.zeros((matrix.shape[0], matrix.shape[1]), dtype=np.double)

    for cluster in clusters:
        for c1 in cluster:
            for c2 in cluster:
                refd_result = calRefDScore(bikewords, matrix, c1, c2, max_time=15)
                refd = refd_result[0]
                i = refd_result[1]
                j = refd_result[2]
                if refd > zeta:
                    relationMatrix[j][i] = refd
                elif refd < -zeta:
                    relationMatrix[i][j] = -refd

    # for i in range(0, matrix.shape[0] - 1):
    #     for j in rang  e(i + 1, matrix.shape[0] - 1):
    #         refd = br.RefD(matrix, i, j)
    #         if refd > zeta:
    #             relationMatrix[j][i] = refd
    #         elif refd < -zeta:
    #             relationMatrix[i][j] = -refd
    np.save("relationMatrix.npy", relationMatrix)


# 获取当前index的直接后继
def getNextConceptsIndex(relationMatrix, index, deep):
    if deep > 6:  # 当深度超过10，则可能进入环路，返回空集
        return []
    res = []
    for i in range(0, relationMatrix.shape[0]):
        if relationMatrix[index][i] != 0:
            res.append(i)
            nextConcepts = getNextConceptsIndex(relationMatrix, i, deep + 1)
            for k in nextConcepts:
                res.append(k)
    return res


# 消除中间关系
def removeMiddleRelation(relationMatrix):
    for i in range(0, relationMatrix.shape[0]):
        print(i)
        for j in range(0, relationMatrix.shape[1]):
            if relationMatrix[i][j] != 0:
                nextConcepts = getNextConceptsIndex(relationMatrix, j, 0)
                for k in nextConcepts:
                    relationMatrix[i][k] = 0
    return relationMatrix


# 获取直接前驱关系
def getDirectedRelation():
    relationMatrix = np.load("relationMatrix.npy")
    print(len(relationMatrix[relationMatrix > 0]))

    # 中间关系消除
    # directedRelationMatrix = removeMiddleRelation(relationMatrix)
    # np.save("directedRelationMatrix.npy", directedRelationMatrix)
    # print(len(relationMatrix[directedRelationMatrix > 0]))
    # printRelation(directedRelationMatrix)
    printRelation(relationMatrix)


# 根据relationMatrix打印出关系
def printRelation(relationMatrix):
    file = open("知识点目录顺序.txt", 'r', encoding='utf-8')
    line = file.readline()
    bikewords = line.split(" ")
    relations = ""

    for i in range(0, relationMatrix.shape[0] - 1):
        for j in range(0, relationMatrix.shape[1] - 1):
            if relationMatrix[i][j] != 0:
                print(relationMatrix[i][j], bikewords[i] + "--->" + bikewords[j])
                relations += bikewords[i] + " " + bikewords[j] + "\n"
    Utils.writeFile("relation.txt", relations)


# label the error relation according to concept order
def labelErrorRelation(orderFilePath, relationFilePath):
    # load the catalog order of knowledges
    order = []
    with open(orderFilePath, "r", encoding="utf-8") as orderFile:
        line = orderFile.readline()
        order = line.split(" ")

    # according to the order of knowledges, label the error relations
    with open(relationFilePath, "r", encoding="utf-8") as relationFile:
        error = 0
        candinate = 0
        error_relations = ""
        candinate_relation = ""
        for line in relationFile:
            knowledges = line.split(" ")
            first_index = order.index(knowledges[0])
            second_index = order.index(knowledges[1].replace("\n", ""))
            if first_index > second_index:
                error_relations += line
                error += 1
            else:
                candinate_relation += line
                candinate += 1
        Utils.writeFile("error_relation.txt", error_relations)
        Utils.writeFile("candinate_relation.txt", candinate_relation)
        print("error", error)
        print("candinate", candinate)


# according to the labeled relation, judge candinate relation
def judgeCandinateRelation(labeled_relaiton_file_path, candinate_relation_file_path):
    # load the labeled relation from file
    labeledRelations = {}
    with open(labeled_relaiton_file_path, "r", encoding="utf-8") as labeled_relation:
        for line in labeled_relation:
            # print(line)
            a, b, l = line.split(" ")
            labeledRelations[a + " " + b] = l.replace("\n", "")

    # judge the candinate relation,print the correct, error number and unlabeled relation
    with open(candinate_relation_file_path, "r", encoding="utf-8") as candinate_relation:
        correct = 0
        error = 0
        uncertain = 0
        hit = 0
        for line in candinate_relation:
            label = labeledRelations.get(line.replace("\n", ""))
            if label == None:
                uncertain += 1
                print(line.replace("\n", ""))
            else:
                hit += 1
            if label == "1":
                correct += 1
                print(line.replace("\n", ""), 1)
            if label == "2":
                error += 1
                print(line.replace("\n", ""), 2)
                # print("error", line)
        print("Correct", correct)
        print("Error", error)
        print("Accurancy", correct / (correct + error))
        print("uncertain", uncertain)
        print("hit", hit)


def generateRelationMatrix(cencepts_file_path, relation_file_path):
    # load concepts
    concept_order = []
    with open(cencepts_file_path, "r", encoding="utf-8") as concept_order:
        line = concept_order.readline()
        concept_order = line.split(" ")
        print("total load %d concept" % (len(concept_order)))

    # initialize the relation matrix
    relationMatrix = np.zeros((len(concept_order), len(concept_order)), dtype=np.double)

    with open(relation_file_path, "r", encoding="utf-8") as relations:
        for line in relations:
            values = line.replace("\n", "").split(" ")
            index_a = concept_order.index(values[0])
            index_b = concept_order.index(values[1])
            relationMatrix[index_a][index_b] = 1.0

    # print the directed relation
    printRelation(removeMiddleRelation(relationMatrix))


# init_value = init("初中知识点_目录.txt", "occurrenceMatrix.npy", "知识点目录顺序.txt", zeta=0.9)
# matrix = init_value[0]
# bikewords = init_value[3]
# refd_result = calRefDScore(bikewords, matrix, "分数", "实数")# --->
# print(refd_result[0])


# generateRelationByRefD(zeta=0.25, max_time=100)
# getDirectedRelation()
# labelErrorRelation("知识点目录顺序.txt", "relation.txt")
judgeCandinateRelation("labeled_data_set.txt", "candinate_relation.txt")
# generateRelationMatrix("知识点目录顺序.txt", "relation.txt")
