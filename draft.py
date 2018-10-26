import os
import sys
import h5py
import pandas as pd
import numpy as np
import time
import Validation
# import IBFS


if __name__ == "__main__":

    # change the path to where the script located
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

    # read data
    # data = h5py.File(
    #     'GTW dataset/2-2-4-K2.h5', 'r')
    data = h5py.File(
        'GTW dataset/6-10-4/6-10-4-K20.h5', 'r')
    edge = pd.DataFrame(data['whole'].value.T, columns=[
        'start', 'end', 'weight'])
    source = data['s2'].value[0, 0]
    sink = data['t2'].value[0, 0]
    maxValueOrgin = data['maxValue'].value[0, 0]
    runningTimeOrgin = data['time'].value[0, 0]
    print(maxValueOrgin)

    class GeneralPR:
        # general push-label method
        def __init__(self, edge, source, sink):
            self.edge = edge
            self.edge['start'] = self.edge['start'].astype('int32')
            self.edge['end'] = self.edge['end'].astype('int32')
            self.s = np.int32(source)
            # sink is the last node all the time
            self.t = np.int32(sink)

        def maxflow(self):
            # main function
            maxValue = 0
            count = -1  # the number of augmenting path

            residual = self.edge.weight.copy()
            maxFlow = self.edge.weight.copy()
            maxFlow[:] = 0
            active = [i for i in range(1, self.s)]

            # initilaization
            height = 0*np.int32(np.ones(self.t+1))
            excess = 0*np.ones(self.t+1)
            height[self.s] = self.t   # source height = |V|
            excess[self.s] = np.float('inf')
            for ind in self.edge[self.edge.start == self.s].index:
                node = self.edge.end[ind]
                maxFlow[ind] = self.edge.weight[ind]
                residual[ind] = 0
                excess[node] = maxFlow[ind]

            p = 0
            while p < self.s - 1:
                active_node = active[p]
                while excess[active_node]:
                    push_flag = False
                    path_list = self.edge[self.edge.start ==
                                            active_node].index
                    # try push
                    for ind in path_list:
                        node = self.edge.end[ind]
                        if residual[ind] > 0 and height[active_node] == height[node] + 1:
                            push_flag = True
                            bottleneck = min(
                                residual[ind], excess[active_node])
                            excess[active_node] -= bottleneck
                            excess[node] += bottleneck
                            maxFlow[ind] += bottleneck
                            if ind % 2 == 0:
                                residual[ind] -= bottleneck
                                residual[ind+1] += bottleneck
                            else:
                                residual[ind-1] += bottleneck
                                residual[ind] -= bottleneck
                    # try relabel
                    if not push_flag:
                        find_flag = False
                        label = np.float('inf')
                        for ind in path_list:
                            node = self.edge.end[ind]
                            if residual[ind] > 0 and label > height[node]:
                                find_flag = True
                                label = height[node]
                        if find_flag:
                            active.insert(0,active.pop(p))
                            height[active_node] = label + 1
                            p = -1
                p += 1


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
            for ind in self.edge[self.edge.start == self.s].index:
                if maxFlow[ind + 1] != 0:
                    if maxFlow[ind] >= maxFlow[ind+1]:
                        maxFlow[ind] -= maxFlow[ind+1]
                        maxFlow[ind+1] = 0
                    else:
                        maxFlow[ind+1] -= maxFlow[ind]
                        maxFlow[ind] = 0
            for ind in self.edge[self.edge.end == self.t].index:
                if maxFlow[ind + 1] != 0:
                    if maxFlow[ind] >= maxFlow[ind+1]:
                        maxFlow[ind] -= maxFlow[ind+1]
                        maxFlow[ind+1] = 0
                    else:
                        maxFlow[ind+1] -= maxFlow[ind]
                        maxFlow[ind] = 0

            maxValue = excess[self.t]

            return maxValue, maxFlow, count

            

    # build graph and calculate
    graph = GeneralPR(edge, source, sink)
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

    result = Validation.validate(graph, maxFlow, maxValue,
                                 maxValueOrgin, np.int32(data['sCut'].value[0]))

    input()
