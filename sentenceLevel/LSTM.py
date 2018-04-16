import torch
from torch import nn
from torch.autograd import Variable
import torchvision.datasets as datasets
import torchvision.transforms as transforms

class LSTM(nn.Module):
    def __init__(self):
        self.EPOCH = 10
        self.LR = 0.01

