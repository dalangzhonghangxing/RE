import jieba
import os


# filter the candidate concept pairs which contains two bike words without citing to each other.
class AutoLabel():
    def __init__(self, knowledge_pairs_path, bike_content_folder_path):
        self.knowledge_pairs_path = knowledge_pairs_path
        self.bike_content_folder_path = bike_content_folder_path
        jieba.load_userdict("wordBase.txt")

    def load_knowledge_pairs(self):
        self.knowledge_pairs = set()
        with open(self.knowledge_pairs_path, "r", encoding="utf-8") as knowledge_pairs_file:
            for line in knowledge_pairs_file:
                self.knowledge_pairs.add(line.replace("\n", ""))

    def load_bike_content(self):
        self.bike_contents = {}
        for fileName in os.listdir(self.bike_content_folder_path):
            document = open(os.path.join('%s/%s' % (self.bike_content_folder_path, fileName)), "r",
                            encoding="utf-8")
            content = ""
            for line in document:
                content += line.replace("\n","")
            self.bike_contents[fileName.split(".")[0]] = list(jieba.cut(content))
            # self.bike_contents.put(fileName.split(".")[0], [jieba.cut(document)])


    def is_related(self, k1, k2):
        content1 = self.bike_contents.get(k1)
        if content1 == None or k1 == None:
            print("k1:"+k1)
        content2 = self.bike_contents.get(k2)
        if content2 == None or k2 == None:
            print("k2:"+k2)
        if k2 in content1 or k1 in content2:
            return True
        return False


    def remove_unrelated_pairs(self):
        self.load_knowledge_pairs()
        self.load_bike_content()
        self.related = []
        self.unrelated = []
        for knowledge_pair in self.knowledge_pairs:
            values = knowledge_pair.split(" ")
            if self.is_related(values[0], values[1]):
                self.related.append(knowledge_pair)
            else:
                self.unrelated.append(knowledge_pair)


    def get_related_pairs(self):
        return self.related


    def get_unrelated_pairs(self):
        return self.unrelated
