import os
import sys
import h5py
import pandas as pd
import time
import EdmondsKarp

if __name__ == "__main__":
    # It's used to implement my idea that for GTW graph, calculate the max flow of
    # a single graph seprately and then calculate the max flow of residual graph is
    # quicker than calculaing the max flow on the whole graph directly.

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

    localS = pd.DataFrame(data['local/s'].value.T)
    localT = pd.DataFrame(data['local/t'].value.T)
    localW = pd.DataFrame(data['local/w'].value.T)

    for ind in localS.T.index:
        edge = pd.DataFrame({'start': localS[ind], 'end': localT[ind], 'weight': localW[ind]})
        print(1)

    print(1)
