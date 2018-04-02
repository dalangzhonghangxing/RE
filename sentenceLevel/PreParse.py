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

    def load_sentence(self):
        self.sentences = []
        for line in open(self.dataset_path, "r", encoding="utf-8"):
            sentence = line.split(" ")[0]
            self.sentences.append(list(jieba.cut(sentence)))

    def pos_tag(self):
        self.load_sentence()
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
        self.load_sentence()
        for sentence in self.sentences:
            res = list(self.parser.parse(sentence))
            for item in res:
                print(item)

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
pos.pos_tag()
# pos.generate_dependency_tree()
# stanford.StanfordParser
