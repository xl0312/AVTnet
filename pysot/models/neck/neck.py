# Copyright (c) SenseTime. All Rights Reserved.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import torch.nn as nn
import torch

class AdjustLayer(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(AdjustLayer, self).__init__()
        self.downsample = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(out_channels),
            )

    def forward(self, x):
        x = self.downsample(x)
        row_x = torch.tensor([0]).cuda()
        if x.size(3) < 20:
            row_x = x
        if x.size(3) < 20:
            l = 4
            r = l + 7
            x = x[:, :, l:r, l:r]
        return x, row_x



class AdjustAllLayer(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(AdjustAllLayer, self).__init__()
        self.num = len(out_channels)
        if self.num == 1:
            self.downsample = AdjustLayer(in_channels[0], out_channels[0])
        else:
            for i in range(self.num):
                self.add_module('downsample'+str(i+2),
                                AdjustLayer(in_channels[i], out_channels[i]))

    def forward(self, features):
        if self.num == 1:
            return self.downsample(features)
        else:
            out = []
            out_row = []
            for i in range(self.num):
                adj_layer = getattr(self, 'downsample'+str(i+2))
                mix = adj_layer(features[i])
                out.append(mix[0].contiguous())
                out_row.append(mix[1].contiguous())
            return out, out_row
