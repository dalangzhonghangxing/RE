import os
import Utils
import jieba
import sentenceLevel.bikeOperation as bo
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from sentenceLevel.auto_label import AutoLabel


# a iterator to load sentence for training word2vec
class Sentences(object):
    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for fname in os.listdir(self.dirname):
            for line in open(os.path.join(self.dirname, fname)):
                yield list(jieba.cut(line))


# load the knowledges from specified file
def load_knowledge(knowledge_file_path):
    with open(knowledge_file_path, "r", encoding="utf-8") as file:
        line = file.readline()
        knowledges = line.replace("\n", "").split(" ")
        print("load %d knowledges", len(knowledges))
        return knowledges


# split the paragraph
def split_paragraph(paragraph):
    sentences = []
    for jh in paragraph.split("。"):
        for dot in jh.split("."):
            for fh in dot.split(";"):
                sentences.append(fh.replace(" ", "").replace("　", ""))
    return sentences


# split paragraph and find the sentence which contains other knowledge.
# rebuild the sentence into       origin sentence + " " + + document_knowledge + " " + other knowledge.
def get_sentences_from_paragraph_other_knowledges(paragraph, knowledges, document_knowledge):
    result = []
    sentences = split_paragraph(paragraph)
    for sentence in sentences:
        splited_sentence = list(jieba.cut(sentence))
        for knowledge in knowledges:
            if knowledge != document_knowledge and knowledge in splited_sentence:
                result.append(sentence.replace("\n", "") + " " + document_knowledge + " " + knowledge)
                print(sentence + " " + document_knowledge + " " + knowledge)
    return result


# split paragraph and find the sentence which contains at least two knowledge
def get_sentences_from_paragraph_two_knowledges(paragraph, knowledges, document_knowledge):
    result = []
    sentences = split_paragraph(paragraph)
    for sentence in sentences:
        splited_sentence = list(jieba.cut(sentence))

        # statistics the knowledge appeared in the sentence
        appear_knowledges = []
        for knowledge in knowledges:
            if knowledge in splited_sentence:
                appear_knowledges.append(knowledge)

        # if this sentence contains more than two knowledge, rebuild the sentence by combining all the knowledge
        if len(appear_knowledges) > 1:
            for i in range(len(appear_knowledges)):
                for j in range(i + 1, len(appear_knowledges)):
                    result.append(sentence.replace("\n", "") + " " + appear_knowledges[i] + " " + appear_knowledges[j])
    return result


##
# according the existing knowledge to find other candidate knowledge
def crawl_bikewords_according_existing_knowledge(knowledge_file_path):
    knowledges = set(load_knowledge(knowledge_file_path))
    newBikewords = set()
    i = 0
    for knowledge in knowledges:
        i += 1
        bikewords = bo.parseOutLinkFromContent(knowledge)
        newBikewords = newBikewords | bikewords
        print(i / len(knowledges))

    content = ""
    for bikewords in (newBikewords | knowledges):
        content += bikewords + " "
        print(bikewords)
    print(len(newBikewords | knowledges))
    Utils.writeFile("bikewords.txt", content)


##
# extract useful sentences from knowledge documents
def extract_sentences(folder_path, knowledge_file_path):
    jieba.load_userdict("wordBase.txt")
    knowledges = load_knowledge(knowledge_file_path)
    content = ""
    for fileName in os.listdir(folder_path):
        document = open(os.path.join('%s/%s' % (folder_path, fileName)), "r", encoding="utf-8")
        for line in document:
            sentences = get_sentences_from_paragraph_two_knowledges(line, knowledges, fileName.split(".")[0])
            for sentence in sentences:
                content += sentence + "\n"
    Utils.writeFile("dataset_one_hop.txt", content)


##
# crawl bike content according to the bikewords file, and generate the new knowledge set without duplication.
def crawl_bikecontent_and_generate_knowledge_set(bikewords_file_path):
    with open(bikewords_file_path, "r", encoding="utf-8") as bikewords_file:
        knowledges = set()
        progress = 0
        for line in bikewords_file:
            progress += 1
            values = line.replace("\n", "").split(" ")
            if values[0] in knowledges:
                continue
            try:
                if len(values) > 1:
                    title, content = bo.parseContent(values[0], values[1])
                else:
                    title, content = bo.parseContent(values[0])
                Utils.writeFile("../bikewordContent/" + values[0] + ".txt", content)
                knowledges.add(values[0])
            except:
                Utils.writeFile_Add("error_2.txt", line)
                print(line)
            print(progress)

        knowledges_content = ""
        for knowledge in knowledges:
            knowledges_content += knowledge + " "
        # Utils.writeFile("one_hop_knowledges.txt", knowledges_content)


##
# train word2vec with all bike page content through gensim's word2vec module
def train_word2vec(folder_path):
    sentences = Sentences(folder_path)
    model = Word2Vec(sentences, size=100, workers=8)
    model.save("one_hop_model.txt")


##
# extract knowledge pairs from dataset.
def extract_knowledge_pair_from_dataset(dataset_file_path):
    knowledge_pairs = set()
    with open(dataset_file_path, "r", encoding="utf-8") as dataset_file:
        for line in dataset_file:
            values = line.split(" ")
            knowledge_pairs.add(values[1] + " " + values[2] + " ")

    print("There are %d knowledge pairs" % len(knowledge_pairs))

    knowledge_pairs_content = ""
    for knowledge_pair in knowledge_pairs:
        knowledge_pairs_content += knowledge_pair + "\n"

    Utils.writeFile("knowledge_pairs.txt", knowledge_pairs_content)


##
# Remove the unrelated pairs from the specified candidate knowledge pairs.
def split_related_and_unrelated_pairs(knowledge_pairs_path="knowledge_pairs.txt",
                                      bike_content_folder_path="../bikewordContent"):
    al = AutoLabel(knowledge_pairs_path, bike_content_folder_path)
    al.remove_unrelated_pairs()
    related_pairs = al.get_related_pairs()
    unrelated_pairs = al.get_unrelated_pairs()

    print("%d candidate pairs" % len(related_pairs))
    print("%d unrelated pairs" % len(unrelated_pairs))

    related_pairs_content = ""
    for pair in related_pairs:
        related_pairs_content += pair + "\n"

    unrelated_pairs_content = ""
    for pair in unrelated_pairs:
        unrelated_pairs_content += pair + "\n"

    Utils.writeFile("../sentenceLevelData/candidate_pairs.txt", related_pairs_content)
    Utils.writeFile("../sentenceLevelData/unrelated_pairs.txt", unrelated_pairs_content)


##
# Delete the specified pairs
def delete_unrelated_pairs_from_labeled_pairs(labeled_pairs_path="../sentenceLevelData/labeled_pairs.txt",
                                              delete_file_path="../sentenceLevelData/删除.txt"):
    content = ""
    # load pairs which should be deleted
    delete_pairs = []
    for line in open(delete_file_path, "r", encoding="utf-8"):
        delete_pairs.append(line.replace("\n", ""))

    for line in open(labeled_pairs_path, "r", encoding="utf-8"):
        values = line.replace("\n", "").split(" ")
        if values[0] not in delete_pairs and values[1] not in delete_pairs:
            content += line

    Utils.writeFile("../sentenceLevelData/processed_labeled_pairs.txt", content)


def label_sentences(dataset_path="../sentenceLevelData/dataset_one_hop.txt",
                    labeled_pairs_path="../sentenceLevelData/processed_labeled_pairs.txt"):
    pairs_dict = {}
    content = ""
    for line in open(labeled_pairs_path, "r", encoding="utf-8"):
        values = line.replace("\n", "").split(" ")
        pairs_dict[values[0] + " " + values[1]] = values[2]

    for line in open(dataset_path, "r", encoding="utf-8"):
        values = line.replace("\n", "").split(" ")
        key = values[1] + " " + values[2]
        if key not in pairs_dict.keys():
            continue
        label = pairs_dict[values[1] + " " + values[2]]
        if label != None:
            content += values[0] + " " + values[1] + " " + values[2] + " " + label + "\n"

    Utils.writeFile("../sentenceLevelData/labeled_sentence.txt", content)


# extract_sentences("../bikewordContent", "one_hop_knowledges.txt")
# crawl_bikewords_according_existing_knowledge("知识点目录顺序.txt")
# crawl_bikecontent_and_generate_knowledge_set("bikewords.txt")
# train_word2vec("../bikewordContent")
# model = Word2Vec.load("one_hop_model.txt")
# print(model.similarity('圆', '直角三角形'))
# extract_knowledge_pair_from_dataset("dataset_one_hop.txt")
# split_related_and_unrelated_pairs()
# delete_unrelated_pairs_from_labeled_pairs()
label_sentences()
