import os
import sys
import h5py
import pandas as pd
import numpy as np
import time
import Validation
import BoykovKolmogorov

if __name__ == "__main__":
    # It's used to implement my idea that for GTW graph, calculate the max flow of
    # a single graph seprately and then ca  lculate the max flow of residual graph is
    # quicker than calculaing the max flow on the whole graph directly.

    # change the path to where the script located
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0]))) 

    # read data
    # data = h5py.File(
    #     'GTW dataset/2-2-2-K2.h5', 'r')
    data = h5py.File(
        'GTW dataset/6-10-4/6-10-4-K10.h5', 'r')   
    source1 = data['s1'].value[0, 0]
    sink1 = data['t1'].value[0, 0]
    source2 = data['s2'].value[0, 0]
    sink2 = data['t2'].value[0, 0]
    maxValueOrgin = data['maxValue'].value[0, 0]
    runningTimeOrgin = data['time'].value[0, 0]
    print(maxValueOrgin)

    localS = pd.DataFrame(data['local/s'].value.T)
    localT = pd.DataFrame(data['local/t'].value.T)
    localW = pd.DataFrame(data['local/w'].value.T)
    info = data['information'].value[:,0]
    n = np.int32(info[0])
    num_WholeEdge = np.int32(info[1])
    num_Point = np.int32(info[2])
    num_SingleEdge = np.int32(info[3])

    maxFlow_single = np.zeros([num_SingleEdge,n])
    maxValue = 0

    
    # single graph maxflow calculation
    for ind in localW.T.index:
        edge = pd.DataFrame({'start': localS[0], 'end': localT[0], 'weight': localW[ind]})
        graph = BoykovKolmogorov.BoykovKolmogorov(edge, source1, sink1)
        maxValue_single, maxFlow_single[:,ind],count = graph.maxflow()
        maxValue += maxValue_single
    initialFlow = np.vstack((np.reshape(maxFlow_single.T,[num_SingleEdge*n, 1]),np.zeros([num_Point*num_WholeEdge*2, 1])))
    

    # whole graph maxflow calculation
    residualFlow = np.transpose(data['whole'].value[2,:])
    for ind, _ in enumerate(residualFlow):
        if ind%2 == 0:  
            residualFlow[ind] -= initialFlow[ind]
            residualFlow[ind+1] += initialFlow[ind]
        else:
            residualFlow[ind] -= initialFlow[ind]
            residualFlow[ind-1] += initialFlow[ind]

    edge = pd.DataFrame({'start': data['whole'].value[0,:].T, 'end': data['whole'].value[1,:].T, 'weight': residualFlow})
    graph = BoykovKolmogorov.BoykovKolmogorov(edge, source2, sink2)
    
    tic = time.time()
    maxValue_whole, maxFlow_whole,count = graph.maxflow()
    runningTime = time.time() - tic
    maxValue += maxValue_whole
    maxFlow = initialFlow + np.transpose([maxFlow_whole.values])

    ## reduce circle flows
    label_circle = maxFlow>np.transpose([data['whole'].value[2,:]])+0.0000001
    if any(label_circle):
        for ind in edge[label_circle].index:
            if ind % 2 == 0:
                if maxFlow[ind] >= maxFlow[ind+1]:
                    maxFlow[ind] -= maxFlow[ind+1]
                    maxFlow[ind+1] = 0
                else:
                    maxFlow[ind+1] -= maxFlow[ind]
                    maxFlow[ind] = 0
            else:
                if maxFlow[ind] >= maxFlow[ind-1]:
                    maxFlow[ind] -= maxFlow[ind-1]
                    maxFlow[ind-1] = 0
                else:
                    maxFlow[ind-1] -= maxFlow[ind]
                    maxFlow[ind] = 0
    maxFlow = pd.Series(maxFlow.T[0])

    print('running time:',runningTime,'orgin running time', runningTimeOrgin)
    print('Augmenting paths:',count)

    # For validation
    edge = pd.DataFrame(data['whole'].value.T, columns=[
        'start', 'end', 'weight'])
    graph = BoykovKolmogorov.BoykovKolmogorov(edge, source2, sink2)
    Validation.validate(graph,maxFlow,maxValue,maxValueOrgin,np.int32(data['sCut'].value[0]))

    input()
        
    