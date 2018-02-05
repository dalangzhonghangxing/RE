import gensim
import os
import Utils

from gensim.models.doc2vec import Doc2Vec, TaggedLineDocument


class doc2vec(object):
    def __init__(self, dir=object):
        self.dir = dir
        self.preprocess()

        # size is the number of features of one document.
        # window is the maximun distance between the predicted word and context words used for prediction within a document.
        # min_count = ignore the all words with total frequency lower than this.
        # workers is the number of threads to train the model.
        self.model = Doc2Vec(self.generateLineDocuments(), size=25, window=8, min_count=2, workers=4)

    # combine multiple documents into one document, each line is a document's words splited by whitespace.
    def preprocess(self):
        concept_order = []
        content_list = []
        for fileName in os.listdir(self.dir):
            content = ""
            for line in open(os.path.join('%s/%s' % (self.dir, fileName)), "r", encoding="utf-8"):
                content += line.replace("\n", " ")
            content_list.append(content)
            concept_order.append(fileName.split(".")[0])
        print("total load %d documents" % len(concept_order))
        self.loadConceptOrder()

        content = ""
        for c in self.concept_order:
            index = concept_order.index(c)
            content += content_list[index] + "\n"

        content = content[0: len(content) - 2]
        Utils.writeFile("documents.txt", content)

    # one document = one line = one TaggedDocument object.
    def generateLineDocuments(self):
        return TaggedLineDocument("documents.txt")

    def loadConceptOrder(self):
        # load the order of concept, which is the order of documents' vector
        self.concept_order = []
        with open("知识点目录顺序.txt", "r", encoding="utf-8") as concept_order:
            line = concept_order.readline()
            self.concept_order = line.split(" ")
            print("total load %d concept" % (len(self.concept_order)))


docModel = doc2vec("../splitedBikeContent")
docModel.model.save("doc2vec_model.txt")
# docModel = Doc2Vec.load("doc2vec_model.txt")
# print(len(docModel.docvecs))
