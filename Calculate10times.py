import os
import sys
import h5py
import pandas as pd
import numpy as np
import time
import Validation
import IBFS


if __name__ == "__main__":

    # change the path to where the script located
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

    # read data
    filename = 'GTW dataset/30-50-5/30-50-5-K'
    smooth = ['10','20','30','40','50','100','1000','10000','Inf']
    txtname = 'calculate_result.txt'
    txt = open(txtname, "w")
    for smooth_ind in smooth:
        data = h5py.File(filename + smooth_ind + '.h5', 'r')
        edge = pd.DataFrame(data['whole'].value.T, columns=[
            'start', 'end', 'weight'])
        source = data['s2'].value[0, 0]
        sink = data['t2'].value[0, 0]
        maxValueOrgin = data['maxValue'].value[0, 0]
        runningTimeOrgin = data['time'].value[0, 0]
        print(maxValueOrgin)

        # build graph and calculate
        graph = IBFS.IBFS(edge, source, sink)
        tic = time.time()
        maxValue, maxFlow, count = graph.maxflow()
        runningTime = time.time() - tic

        # reduce circle flows
        label_circle = maxFlow > graph.edge.weight+0.0000001
        if any(label_circle):
            for ind in graph.edge[label_circle].index:
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

        print('running time:', runningTime, 'orgin running time', runningTimeOrgin)
        print(smooth_ind) 

        result = Validation.validate(graph, maxFlow, maxValue,
                                    maxValueOrgin, np.int32(data['sCut'].value[0]))

        if result:
            txt.write(filename+smooth_ind+'         '+str(runningTime)+'         '+str(runningTimeOrgin)+'\n')
        else:
            txt.write(filename+smooth_ind+'         '+'Something is incorrect.\n')
    txt.close()
    print('Finished!')
    input()