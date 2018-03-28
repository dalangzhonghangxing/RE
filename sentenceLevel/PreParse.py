import nltk
from nltk.parse import stanford
import jieba
import os


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
        res = nltk.pos_tag_sents(self.sentences)
        for sr in res:
            print(sr)

    def generate_dependency_tree(self):
        self.load_sentence()
        for sentence in self.sentences:
            res = list(self.parser.parse(sentence))
            print(res)


# nltk.download('averaged_perceptron_tagger')
pos = PreParse("../sentenceLevelData/labeled_sentence.txt")
pos.generate_dependency_tree()
# stanford.StanfordParser
