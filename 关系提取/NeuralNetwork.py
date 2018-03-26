import torch
from torch.autograd import Variable
import torch.nn.functional as F
import numpy as np
from gensim.models.doc2vec import Doc2Vec
import random
import math


class OneLayerNet(torch.nn.Module):
    def __init__(self, D_in):
        super(OneLayerNet, self).__init__()
        self.bilinear = torch.nn.Bilinear(D_in, D_in, 1)
        self.linear_1 = torch.nn.Linear(D_in, D_in)
        self.relu = torch.nn.ReLU(inplace=True)
        self.dropout = torch.nn.Dropout(0.1)
        # self.linear_2 = torch.nn.Linear(D_in, 1)

    def forward(self, x_1, x_2):
        # d1 = self.relu(self.linear_1(x_1))
        # d2 = self.relu(self.linear_1(x_2))
        # y_pred = F.sigmoid(self.dropout(self.bilinear(x_1, x_2)))
        y_pred = F.sigmoid(self.bilinear(x_1, x_2))
        return y_pred


class NeuralNetwork():
    def __init__(self, doc2vec_model_path="doc2vec_model.txt", dataset_path="labeled_data_set.txt",
                 concept_order_path="知识点目录顺序.txt", concept_group_path="初中知识点_目录.txt",
                 iterate=1, isTrain=True, D_in=100, sample_rate=5, repeat=10):
        self.D_in = D_in
        self.first_train = True
        if isTrain:
            self.doc2vec_model_path = doc2vec_model_path
            self.dataset_path = dataset_path
            self.concept_order_path = concept_order_path
            self.iterate = iterate
            self.sample_rate = sample_rate

            self.loadConceptOrder()
            self.preprocess()
            self.prepare_Variable()
            # for i in range(0, repeat):
            #     self.iterate_index = i
            #     self.sampling()
            #     self.prepare_Variable()
            #     self.train()
            #     self.first_train = False
            self.verifyTrainResult()
        else:
            self.doc2vec_model_path = doc2vec_model_path
            self.concept_order_path = concept_order_path
            self.concept_group_path = concept_group_path

            self.loadConceptOrder()
            self.discoverGlobalRelation()
            # self.discoverGroupRelation()

    def discoverGroupRelation(self):
        # load the concept group
        group = []
        with open(self.concept_group_path, "r", encoding="utf-8") as concept_group:
            for line in concept_group:
                concepts = line.replace("\n", "").split(" ")
                group.append(concepts)

        # load the model
        model = OneLayerNet(self.D_in)
        model.load_state_dict(torch.load('model_parameters.pkl'))

        # load the doc2vec
        docModel = Doc2Vec.load(self.doc2vec_model_path)

        x1 = []
        x2 = []
        l1 = []
        l2 = []
        for g in group:
            for i in range(0, len(g)):
                for j in range(i + 1, len(g)):
                    x1.append(docModel.docvecs[i])
                    x2.append(docModel.docvecs[j])
                    l1.append(g[i])
                    l2.append(g[j])

        dtype = torch.FloatTensor
        vx1 = Variable(torch.from_numpy(np.array(x1)).type(dtype), requires_grad=True)
        vx2 = Variable(torch.from_numpy(np.array(x2)).type(dtype), requires_grad=True)
        y_pred = model(vx1, vx2)
        index = 0
        relation_number = 0
        for y in y_pred.data:
            if y[0] > 0.5:
                relation_number += 1
                print(l1[index], " ", l2[index])
            index += 1
        print("find %d relations" % relation_number)
        print("solution space is %d" % len(x1))

    def discoverGlobalRelation(self):
        model = OneLayerNet(self.D_in).cuda()
        model.load_state_dict(torch.load('model_parameters.pkl'))
        docModel = Doc2Vec.load(self.doc2vec_model_path)
        x1 = []
        x2 = []
        l1 = []
        l2 = []
        for i in range(0, len(self.concept_order)):
            # just consider the next len(self.concept_order) / 5 concepts
            # for j in range(i + 1, len(self.concept_order)):
            for j in range(i + 1, len(self.concept_order)):
                x1.append(docModel.docvecs[i])
                x2.append(docModel.docvecs[j])
                l1.append(self.concept_order[i])
                l2.append(self.concept_order[j])

        dtype = torch.FloatTensor
        vx1 = Variable(torch.from_numpy(np.array(x1)).type(dtype), requires_grad=True).cuda()
        vx2 = Variable(torch.from_numpy(np.array(x2)).type(dtype), requires_grad=True).cuda()
        y_pred = model(vx1, vx2)
        index = 0
        relation_number = 0
        for y in y_pred.data:
            if y[0] > 0.5:
                relation_number += 1
                print(y[0],l1[index], " ", l2[index])
            index += 1
        print(relation_number)

    def loadConceptOrder(self):
        # load the order of concept, which is the order of documents' vector
        self.concept_order = []
        with open(self.concept_order_path) as concept_order:
            line = concept_order.readline()
            self.concept_order = line.split(" ")
            print("total load %d concept" % (len(self.concept_order)))

    # transfer the
    def prepare_Variable(self):
        dtype = torch.FloatTensor
        self.vx1 = Variable(torch.from_numpy(np.array(self.x1)).type(dtype), requires_grad=True).cuda()
        self.vx2 = Variable(torch.from_numpy(np.array(self.x2)).type(dtype), requires_grad=True).cuda()
        self.vy = Variable(torch.from_numpy(np.array(self.y)).type(dtype)).cuda()

    # process the
    def preprocess(self):
        # load doc2vec model
        docModel = Doc2Vec.load(self.doc2vec_model_path)

        self.x1 = []
        self.x2 = []
        self.y = []
        self.x1_index = []  # record the index of concept
        self.x2_index = []
        # load the labeled dataset, x1 -> x2, y is the label(1 means true, 0 means false)
        with open(self.dataset_path, "r", encoding="utf-8") as dataset:
            for line in dataset:
                values = line.replace("\n", "").split(" ")
                if (values[1] not in self.concept_order or values[0] not in self.concept_order):
                    continue
                self.x1.append(docModel.docvecs[self.concept_order.index(values[0])])
                self.x2.append(docModel.docvecs[self.concept_order.index(values[1])])
                self.x1_index.append(self.concept_order.index(values[0]))
                self.x2_index.append(self.concept_order.index(values[1]))
                if (values[2] == "1"):
                    self.y.append(1.0)
                    self.x1.append(docModel.docvecs[self.concept_order.index(values[1])])
                    self.x2.append(docModel.docvecs[self.concept_order.index(values[0])])
                    self.x1_index.append(self.concept_order.index(values[1]))
                    self.x2_index.append(self.concept_order.index(values[0]))
                    self.y.append(0.0)
                else:
                    self.y.append(0.0)

        # save the dimension of x1's col
        # self.D_in = len(self.x1[0])

    # sampling negative samples
    def sampling(self):
        docModel = Doc2Vec.load(self.doc2vec_model_path)

        # calculate the number of samples(positive_samples_number * sample_rate)
        sample_number = len([x for x in self.y if x == 1]) * self.sample_rate - len([x for x in self.y if x < 0.5])

        # sampling the negative samples until the number of negative samples equal sample_number
        s = 0
        while (s < sample_number):
            r1 = int(random.uniform(0, len(self.concept_order)))
            r2 = int(random.uniform(0, len(self.concept_order)))

            # this combination of concepts do not exist in existing samples
            s1 = [index for index, _ in enumerate(self.x1_index) if self.x1_index[index] == r1]
            s2 = [index for index, _ in enumerate(self.x2_index) if self.x2_index[index] == r2]
            if len(set(s1).intersection(set(s2))) == 0:
                self.x1.append(docModel.docvecs[r1])
                self.x2.append(docModel.docvecs[r2])
                self.x1_index.append(r1)
                self.x2_index.append(r2)
                self.y.append(0.0)

                s += 1

    def train(self):
        model = OneLayerNet(self.D_in).cuda()
        # model = torch.nn.Sequential(
        #     torch.nn.Bilinear(self.D_in, self.D_in, 1),
        #     torch.nn.Dropout(0.5),
        #     torch.nn.Sigmoid()
        # ).cuda()
        if self.first_train == False:
            model.load_state_dict(torch.load('model_parameters.pkl'))
        loss_func = torch.nn.MSELoss(size_average=False)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        # optimizer = torch.optim.LBFGS(model.parameters(),)
        last_loss = 0

        for i in range(0, int(self.iterate)):

            y_pred = model(self.vx1, self.vx2)
            loss = loss_func(y_pred, self.vy)

            # # break when model is convergence
            # if math.fabs(loss.data[0] - last_loss) < 0.00000000000000000001:
            #     break
            # last_loss = loss.data[0]

            # self.iterate - 1
            if (i % 100 == 0):
                print(self.iterate_index, i, loss.data[0])

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        correct = 0
        error = 0
        index = 0
        for y in y_pred.data:
            if y[0] > 0.5:
                if self.y[index] > 0.5:
                    correct += 1
                else:
                    error += 1
            index += 1
        print("correct = %d \t error = %d" % (correct, error))
        print("accuracy:", correct / (correct + error))
        print("recall:", correct / len([x for x in self.y if x > 0.5]))
        # save the parameters of model
        torch.save(model.state_dict(), 'model_parameters.pkl')

        # # load the parameters of model
        # model_object.load_state_dict(torch.load('model_parameters.pkl'))

    def verifyTrainResult(self):
        model = OneLayerNet(self.D_in).cuda()
        model.load_state_dict(torch.load('model_parameters.pkl'))

        #  predicate relations from x1 and x2
        y_pred = model(self.vx1, self.vx2)

        # index = 0
        # error = 0.0
        # for y in y_pred.data:
        #     if (y[0] > 0.5 and self.y[index] < 0.5):
        #         print(y[0], self.concept_order[self.x1_index[index]], self.concept_order[self.x2_index[index]])
        #         error += 1
        #     if (y[0] <= 0.5 and self.y[index] > 0.5):
        #         print(y[0], self.concept_order[self.x1_index[index]], self.concept_order[self.x2_index[index]])
        #         error += 1
        #     index += 1
        # print("accurancy:", (index - error) / index)

        index = 0
        positive = 0
        for y in y_pred.data:
            if y[0] >0.5:
                print(self.concept_order[self.x1_index[index]], self.concept_order[self.x2_index[index]])
                positive += 1
            index +=1
        print(positive)

NeuralNetwork(isTrain=False, D_in=25, sample_rate=3, iterate=2000000, repeat=2)
# NeuralNetwork(isTrain=False, D_in=25)
