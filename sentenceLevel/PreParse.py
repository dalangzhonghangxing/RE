import nltk
from nltk.parse import stanford
import jieba
import pandas as pa
import numpy as np
from collections import Counter


# 将句子进行pos标注，并生成dependency tree
class PreParse():
    def __init__(self, dataset_path):
        jieba.load_userdict("wordBase.txt")
        self.dataset_path = dataset_path
        # os.environ['STANFORD_PARSER'] = "~/nlp/stanford-parser.jar"
        # os.environ['STANFORD_MODELS'] = "~/nlp/stanford-parser-3.9.1-models.jar"
        self.parser = stanford.StanfordParser(path_to_jar=u"/Users/hang/nlp/stanford-parser.jar",
                                              path_to_models_jar=u"/Users/hang/nlp/stanford-parser-3.9.1-models.jar",
                                              model_path=u'/Users/hang/nlp/chinesePCFG.ser.gz')
        self.load_sentence()

    def load_sentence(self):
        self.sentences = []
        self.target_pairs = []
        self.labels = []
        for line in open(self.dataset_path, "r", encoding="utf-8"):
            value = line.replace("\n", "").split(" ")
            sentence = value[0]
            self.sentences.append(list(jieba.cut(sentence)))
            self.target_pairs.append([value[1], value[2]])
            self.labels.append(value[3])

    def pos_tag(self):
        types = []
        res = nltk.pos_tag_sents(self.sentences)
        for sentence in res:
            for item in sentence:
                types.append(item[1])
        print(Counter(types))
        # one_hot = self.one_hot(item[1])
        # print(np.sum(one_hot == 1), one_hot)
        # types.add(item[1])
        # print(types)

    def generate_dependency_tree(self):
        for i, sentence in enumerate(self.sentences):
            res = list(self.parser.parse(sentence))
            for item in res:
                print(item)
                self.get_SDP(item, self.target_pairs[i][0], self.target_pairs[i][1])

    def get_SDP(self, dependency_tree, t1, t2):
        # path1 = self.get_path_from_root(dependency_tree, t1)
        # path2 = self.get_path_from_root(dependency_tree, t2)

        leaf_values = dependency_tree.leaves()

        if t1 in leaf_values:
            leaf_index = leaf_values.index(t1)
            tree_location1 = dependency_tree.leaf_treeposition(leaf_index)

        if t2 in leaf_values:
            leaf_index = leaf_values.index(t2)
            tree_location2 = dependency_tree.leaf_treeposition(leaf_index)

        i = -1
        while True:
            if t2 in dependency_tree[tree_location1[0:i]].leaves():
                break
            i -= 1

        j = -1
        while True:
            if t1 in dependency_tree[tree_location2[0:j]].leaves():
                break
            j -= 1

        SDP_tree = []
        if len(dependency_tree[tree_location1[0:i]].leaves()) > len(dependency_tree[tree_location2[0:j]].leaves()):
            SDP_tree = dependency_tree[tree_location2[0:j-1]]
        else:
            SDP_tree = dependency_tree[tree_location1[0:i-1]]

        return SDP_tree.pos()

    def one_hot(self, label):
        total_labels = ['CD', "''", 'VB', '$', 'DT', ')', '(', 'NNS', 'VBN', 'PRP', 'POS', 'MD', 'CC', 'FW', ':', 'VBZ',
                        'RB', '.', 'UH', 'NNPS', ',', 'PDT', 'NNP', 'VBP', 'LS', 'TO', 'SYM', 'VBD', 'JJ', 'IN', 'NN']
        one_hot = np.zeros((len(total_labels) + 1,), dtype=np.float)
        if label not in total_labels:
            one_hot[-1] = 1
        else:
            one_hot[total_labels.index(label)] = 1
        return one_hot


# nltk.download('averaged_perceptron_tagger')
pos = PreParse("../sentenceLevelData/labeled_sentence.txt")
# pos.pos_tag()
pos.generate_dependency_tree()
# stanford.StanfordParser
