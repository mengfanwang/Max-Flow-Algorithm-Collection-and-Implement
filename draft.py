import os
import sys
import h5py
import pandas as pd
import numpy as np
import time
import Validation
import Dinic2

if __name__ == "__main__":

    # change the path to where the script located
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

    # read data
    # data = h5py.File(
    #     'GTW dataset/2-2-2-K2.h5', 'r')
    data = h5py.File(
        'GTW dataset/9-15-10/9-15-10-KInf.h5', 'r')
    edge = pd.DataFrame(data['whole'].value.T, columns=[
        'start', 'end', 'weight'])
    source = data['s2'].value[0, 0]
    sink = data['t2'].value[0, 0]
    maxValueOrgin = data['maxValue'].value[0, 0]
    runningTimeOrgin = data['time'].value[0, 0]
    print(maxValueOrgin)

    class BoykovKolmogorov:
        # nothing to explain. BK is BK. Implemented with dict and list.
        def __init__(self, edge, source, sink):
        self.edge = edge
        self.edge['start'] = self.edge['start'].astype('int32')
        self.edge['end'] = self.edge['end'].astype('int32')
        self.s = np.int32(source)
        # sink is the last node all the time
        self.t = np.int32(sink)

        def Growth(self, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited)
        # Step 1. Growth with BFS
        while active_s or active_t:
            # source part
            parentNode = active_s.pop(0)
            for ind in self.edge[self.edge.start == parentNode].index:
                node = self.edge.end[ind]
                if not tree_t.get(node):
                    if (visited[node] == False) and (residual[ind]) > 0:
                        active_s.append(node)
                        visited[node] = True
                        tree_s[node] = []
                        tree_s[parentNode].append(node)
                        parentPath_s[node] = ind
                else:
                    # i'm not sure this step is necessory or not, which maybe deleted in the future
                    active_s.insert(0, parentNode)
                    connectPath = ind
                    return True, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, connectPath
            # sink part
            parentNode = active_t.pop(0)
            for ind in self.edge[self.edge.end == parentNode].index:
                node = self.edge.start[ind]
                if not tree_s.get(node):
                    if (visited[node] == False) and (residual[ind]) > 0:
                        active_t.append(node)
                        visited[node] = True
                        tree_t[node] = []
                        tree_t[parentNode].append(node)
                        parentPath_t[node] = ind
                else:
                    active_t.insert(0, parentNode)  # same not necessary
                    connectPath = ind
                    return True, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, connectPath
        return False, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, connectPath

        def maxflow(self):
            # main function
        maxValue = 0
        count = -1  # the number of augmenting path

        residual = self.edge.weight.copy()
        maxFlow = self.edge.weight.copy()
        maxFlow[:] = 0

        # Initialization
        tree_s = {}
        tree_t = {}
        tree_s[self.s] = []
        tree_t[self.t] = []
        orphan_s = []
        orphan_t = []
        active_s = [self.s]
        active_t = [self.t]
        visited = [False] * (self.t+1)
        parentPath_s = -1*np.int32(np.ones(self.t+1))
        parentPath_t = -1*np.int32(np.ones(self.t+1))
        visited[self.s] = True
        visited[self.t] = True

        while True:
            # Step 1
            flag, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, connectPath = Growth(
                tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited)
            if not flag:
                return maxValue, maxFlow, count

            # Step 2. Augmentation  
            # find the path from s to t
            bottleneck = residual[connectPath]
            # source tree search
            orphan_s = []
            orphan_t = []
            orphanParent_s = []
            orphanParent_t = []
            while node != self.s:
                path = parentPath_s[node]
                if residual[path] < bottleneck:
                    bottleneck = residual[path]
                    orphan_s = [node]
                    orphanParent_s = [self.edge.start[path]]
                elif residual[path] == bottleneck:
                    orphan_s.append(node)
                    orphanParent_s.append(self.edge.start[path])
                node = self.edge.start[path]
            # sink tree search
            while node != self.t:
                path = parentPath_t[node]
                if residual[path] < bottleneck:
                    bottleneck = residual[path]
                    orphan_s = []
                    orphanParent_s = []
                    orphan_t = [node]
                    orphanParent_t = [self.edge.end[path]]
                elif residual[path] == bottleneck:
                    orphan_t.append(node)
                    orphanParent_t.append(self.edge.end[path])
                node = self.edge.end[path]

            maxValue += bottleneck
            print(maxValue)
            # augment the path
            # connect part augmention
            if connectPath % 2 == 0:
                residual[path] -= bottleneck
                residual[path+1] += bottleneck
            else:
                residual[path-1] += bottleneck
                residual[path] -= bottleneck
            # source tree augmention
            node = self.edge.start[path]
            while True:
                path = parentPath[node]
                if path % 2 == 0:
                    residual[path] -= bottleneck
                    residual[path+1] += bottleneck
                else:
                    residual[path-1] += bottleneck
                    residual[path] -= bottleneck
                maxFlow[path] += bottleneck
                node = self.edge.start[path]
                if node == self.s:
                    break
            # sink tree augmention
            node = self.edge.end[path]
            while True:
                path = parentPath[node]
                if path % 2 == 0:
                    residual[path] -= bottleneck
                    residual[path+1] += bottleneck
                else:
                    residual[path-1] += bottleneck
                    residual[path] -= bottleneck
                maxFlow[path] += bottleneck
                node = self.edge.end[path]
                if node == self.t:
                    break

            # Step 3. Adoption
            # source tree
            while orphan_s:
                orphan_node = orphan_s.pop(0)
                # try to find a new parent
                findParent = False
                for ind in self.edge[self.edge.end == orphan_node].index:
                    parentNode = self.edge.start[ind]
                    if residual[ind] > 0 and tree_s.get(parentNode):
                        orgin_parentNode = orphanParent_s.pop(0)
                        tree_s[orgin_parentNode].remove(orphan_node)
                        tree_s[parentNode].append(orphan_node)
                        findParent = True
                        break
                if not findParent:
                    
            # sink tree
                    
    # build graph and calculate
    graph = Dinic2.Dinic(edge, source, sink)
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

    Validation.validate(graph, maxFlow, maxValue,
                        maxValueOrgin, np.int32(data['sCut'].value[0]))

    input()
