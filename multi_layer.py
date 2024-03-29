import onnx as O
import os
import sys
import time
from collections import OrderedDict, namedtuple
import numpy as np
from helper import CreateConvOps, reluLayer_wrapper, poolingLayer_wrapper, GAPLayer_wrapper
import re
import json
import xlrd
from single_layer import buildSingleLayerONNX


def buildMultiLayerONNX(cfgDict1, cfgDict2):
    needFlatten = True
    jsonfile1, singleLayer1 = buildSingleLayerONNX(cfgDict1, needFlatten,layeridx=1, )

    layer1NodeOpType_lst = []
    for node in singleLayer1.node_list:
        layer1NodeOpType_lst.append(node.op_type)
    needFlatten = False if "Gemm" in layer1NodeOpType_lst else True
    
    jsonfile2, singleLayer2 = buildSingleLayerONNX(cfgDict2, needFlatten,layeridx=2, prevalueinfo=singleLayer1.values_out[0])


    my_node_list = singleLayer1.node_list + singleLayer2.node_list

    my_values_in = singleLayer1.values_in
    if singleLayer2.cfgDict["conv_mode_in_hw_setting"] in ["11", "16"] and singleLayer2.cfgDict["conv/pfunc"] == "CONV":
        my_values_in.append( singleLayer2.values_in[-1]) # this is for two input case


    my_values_out = singleLayer2.values_out
    if singleLayer2.values_in == singleLayer2.values_out:
        my_values_out = singleLayer1.values_out
    my_values_info=singleLayer1.values_info+singleLayer2.values_info[1:]
    MutiLayer = namedtuple("MultiLayer", ["node_list", "cfgDict", "values_in", "values_out" , "values_info"])

    muti_layer = MutiLayer(my_node_list, cfgDict2, my_values_in, my_values_out, my_values_info)

    jsonfile = {**jsonfile1, **jsonfile2}
    return jsonfile, muti_layer





    # if conv_mode == 5 11 12 13 14 15 16  pfuncpool:
    #  outputchannel =    inputchannel
    # else:
    #     outputchannel = read from cfg


