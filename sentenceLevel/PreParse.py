import nltk
from nltk.parse import stanford
import jieba
import numpy as np
from collections import Counter
from gensim.models import Word2Vec
from multiprocessing import cpu_count
import threading
import Utils
from sentenceLevel.mutiple_thread import myThread


# 将句子进行pos标注，并生成dependency tree
class PreParse():
    def __init__(self, dataset_path):
        jieba.load_userdict("wordBase.txt")
        self.dataset_path = dataset_path
        self.parser = stanford.StanfordParser(path_to_jar=u"/Users/hang/nlp/stanford-parser.jar",
                                              path_to_models_jar=u"/Users/hang/nlp/stanford-parser-3.9.1-models.jar",
                                              model_path=u'/Users/hang/nlp/chinesePCFG.ser.gz')
        self.load_sentence()
        self.load_word2vec_model()

    def load_word2vec_model(self):
        self.word2vec_model = Word2Vec.load("one_hop_model.txt")

    def load_sentence(self):
        self.sentences = []
        self.target_pairs = []
        self.labels = []
        for line in open(self.dataset_path, "r", encoding="utf-8"):
            value = line.replace("\n", "").split(" ")
            sentence = value[0]
            sentence_list = list(jieba.cut(sentence))
            if value[1] in sentence_list and value[2] in sentence_list:
                self.sentences.append(sentence_list)
                self.target_pairs.append([value[1], value[2]])
                self.labels.append(value[3])
            else:
                print(line)

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

    def mutiple_thread(self):
        length = len(self.sentences)
        thread_numbers = cpu_count()
        step = length // thread_numbers
        for i in range(thread_numbers - 1):
            t = myThread("thread" + str(i), self.generate_sentences_feature_matrix, i * step, (i + 1) * step - 1)
            t.start()
            # threading._start_new_thread(self.generate_sentences_feature_matrix,
            #                             ("thread" + str(i), i * step, (i + 1) * step - 1,))
        myThread("thread" + str(thread_numbers - 1), self.generate_sentences_feature_matrix,
                 step * (thread_numbers - 1),
                 length - 1).start()
        # threading._start_new_thread(self.generate_sentences_feature_matrix,
        #                             ("thread" + str(thread_numbers - 1), step * length, length - 1,))

    # 生成句子特征矩阵
    def generate_sentences_feature_matrix(self, begin, end):
        feature_matrix = []  # 所有句子的特征
        error_sentences_index = ""
        for i in range(begin, end):
            print(i)
            try:
                res = list(self.parser.parse(self.sentences[i]))
                for item in res:
                    SDP_POS = self.get_SDP(item, self.target_pairs[i][0], self.target_pairs[i][1])
                    sentence_feature = []  # 每句话的特征
                    for node in SDP_POS:
                        one_hot = self.one_hot(node[1])
                        word2vec = self.word2vec_model[node[0]]
                        feature = np.hstack((word2vec, one_hot))
                        sentence_feature.append(feature)
                    feature_matrix.append(sentence_feature)
            except:
                error_sentences_index += str(i) + " "
                print(self.sentences[i])
        np.array(feature_matrix)
        np.save('../sentenceLevelData/feature_matrix' + str(begin) + '.txt', feature_matrix)
        Utils.writeFile_Add("../sentenceLevelData/error_sentences.txt", error_sentences_index)

    def get_SDP(self, dependency_tree, t1, t2):
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

        if len(dependency_tree[tree_location1[0:i]].leaves()) > len(dependency_tree[tree_location2[0:j]].leaves()):
            SDP_tree = dependency_tree[tree_location2[0:j - 1]]
        else:
            SDP_tree = dependency_tree[tree_location1[0:i - 1]]

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
pos.mutiple_thread()
# stanford.StanfordParser
