import torch.nn as nn
import torch

class DistributedModel(nn.Module):

    def __init__(self):
        super().__init__(
            embedding=nn.Embedding(1000, 10),
            rnn=nn.Linear(10, 10).cuda(0),
        )

    def forward(self, x):
        # Compute embedding on CPU
        x = self.embedding(x)

        # Transfer to GPU
        x = x.cuda(0)

        # Compute RNN on GPU
        x = self.rnn(x)
        return x

if torch.cuda.is_available():
    # creates a LongTensor and transfers it
    # to GPU as torch.cuda.LongTensor
    print(torch.cuda.device_count())
