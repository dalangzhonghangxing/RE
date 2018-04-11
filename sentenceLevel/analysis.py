import jieba
from nltk.parse import stanford


class Analysis():
    def __init__(self, *args):
        self.args = args
        self.load_stanford_parser()

    def load_stanford_parser(self):
        self.parser = stanford.StanfordParser(
            path_to_jar=u"/home/hang/PycharmProjects/ykyl/experiment_enviroment/sentenceLevel/stanford-parser.jar",
            path_to_models_jar=u"/home/hang/PycharmProjects/ykyl/experiment_enviroment/sentenceLevel/stanford-parser-3.9.1-models.jar",
            model_path=u'/home/hang/PycharmProjects/ykyl/experiment_enviroment/sentenceLevel/chinesePCFG.ser.gz')

    def load_sentence(self):
        jieba.load_userdict("wordBase.txt")
        self.sentences = []
        self.target_pairs = []
        self.labels = []
        self.lines = []
        for line in open(self.args[1], "r", encoding="utf-8"):
            self.lines.append(line.replace("\n", ""))
            value = line.replace("\n", "").split(" ")
            sentence = value[0]
            sentence_list = list(jieba.cut(sentence))
            if value[1] in sentence_list and value[2] in sentence_list:
                self.sentences.append(sentence_list)
                self.target_pairs.append([value[1], value[2]])
                self.labels.append(value[3])
            else:
                print(line)

    def stanford_parse_error_sentence(self):
        self.load_sentence()
        with open(self.args[0], "r", encoding="utf-8") as error_sentences:
            line = error_sentences.readline()
            sentence_indexes = line.split(" ")
            for index in sentence_indexes:
                print(self.lines[int(index)])

    def parse_sentence(self, sentence):
        tree = list(self.parser.parse(list(jieba.cut(sentence))))
        # tree.draw()


ana = Analysis("../sentenceLevelData/error_sentences.txt", "../sentenceLevelData/labeled_sentence.txt")
# ana.stanford_parse_error_sentence()
ana.parse_sentence("8、等腰梯形对角线的平方等于腰的平方与上、下底积的乘积和，如图2")
