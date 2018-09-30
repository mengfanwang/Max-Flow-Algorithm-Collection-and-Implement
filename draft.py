import os
import sys
import h5py
import pandas as pd
import time
import EdmondsKarp

if __name__ == "__main__":

    # change the path to where the script located
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

    # read data
    data = h5py.File(
        'dataset/2-2-4-K2.h5', 'r')
    edge = pd.DataFrame(data['whole'].value.T, columns=[
        'start', 'end', 'weight'])
    source = data['s2'].value[0, 0]
    sink = data['t2'].value[0, 0]
    maxValueOrgin = data['maxValue'].value[0, 0]
    runningTimeOrgin = data['time'].value[0, 0]
    print(maxValueOrgin)

    
    graph = EdmondsKarp.EdmondsKarp(edge, source, sink)
    tic = time.time()
    maxValue = graph.maxflow()
    runningTime = time.time() - tic

    print(maxValue, maxValueOrgin, maxValue-maxValueOrgin)
    print(runningTime, runningTimeOrgin)
