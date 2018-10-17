import os
import sys
import h5py
import pandas as pd
import numpy as np
import time
import Validation


if __name__ == "__main__":

    # change the path to where the script located
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

    # read data
    data = h5py.File(
        'GTW dataset/2-2-4-K2.h5', 'r')
    # data = h5py.File(
    #     'GTW dataset/6-10-4/6-10-4-K30.h5', 'r')
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

        def Growth(self, residual, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited):
            # Step 1. Growth with BFS
            while active_s or active_t:
                # source part
                parentNode = active_s.pop(0)
                for ind in self.edge[self.edge.start == parentNode].index:
                    node = self.edge.end[ind]
                    try:
                        tree_t[node]
                        # i'm not sure this step is necessory or not, which maybe deleted in the future
                        if residual[ind] > 0:
                            active_s.insert(0, parentNode)
                            connectPath = ind
                            return True, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, connectPath
                    except KeyError:
                        if (visited[node] == False) and (residual[ind]) > 0:
                            active_s.append(node)
                            visited[node] = True
                            tree_s[node] = []
                            tree_s[parentNode].append(node)
                            parentPath_s[node] = ind
                # sink part
                parentNode = active_t.pop(0)
                for ind in self.edge[self.edge.end == parentNode].index:
                    node = self.edge.start[ind]
                    try:
                        tree_s[node]
                        if residual[ind] > 0:
                            active_t.insert(0, parentNode)  # same not necessary
                            connectPath = ind
                            return True, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, connectPath
                    except KeyError:
                        if (visited[node] == False) and (residual[ind]) > 0:
                            active_t.append(node)
                            visited[node] = True
                            tree_t[node] = []
                            tree_t[parentNode].append(node)
                            parentPath_t[node] = ind
            return False, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, 0

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
                flag, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, connectPath = self.Growth(
                    residual, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited)
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
                node = self.edge.start[connectPath]
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
                node = self.edge.end[connectPath]
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
                    residual[connectPath] -= bottleneck
                    residual[connectPath+1] += bottleneck
                else:
                    residual[connectPath-1] += bottleneck
                    residual[connectPath] -= bottleneck
                maxFlow[connectPath] += bottleneck
                # source tree augmention
                node = self.edge.start[connectPath]
                while True:
                    path = parentPath_s[node]
                    if path % 2 == 0:
                        residual[path] -= bottleneck
                        residual[path+1] += bottleneck
                    else:
                        residual[path-1] += bottleneck
                        residual[path] -= bottleneck
                    # modify parentPath
                    if residual[path] == 0:
                        parentPath_s[node] = -1
                    maxFlow[path] += bottleneck
                    node = self.edge.start[path]
                    if node == self.s:
                        break
                # sink tree augmention
                node = self.edge.end[connectPath]
                while True:
                    path = parentPath_t[node]
                    if path % 2 == 0:
                        residual[path] -= bottleneck
                        residual[path+1] += bottleneck
                    else:
                        residual[path-1] += bottleneck
                        residual[path] -= bottleneck
                    if residual[path] == 0:
                        parentPath_t[node] = -1
                    maxFlow[path] += bottleneck
                    node = self.edge.end[path]
                    if node == self.t:
                        break

                # Step 3. Adoption
                # source tree
                while orphan_s:
                    orphan_node = orphan_s.pop(0)
                    parent_orgin = orphanParent_s.pop(0)
                    flag_findParent = False
                    # first part find parent
                    for ind in self.edge[self.edge.end == orphan_node].index:
                        parent_poss = self.edge.start[ind]
                        if residual[ind] > 0 and tree_s.get(parent_poss):
                            # judge it's root
                            node = parent_poss
                            while True:
                                path = parentPath_s[node]
                                if path == -1:
                                    flag_root = False
                                    break
                                node = self.edge.start[path]
                                if node == self.s:
                                    flag_root = True
                                    break
                            if flag_root:
                                flag_findParent = True
                                try:
                                    tree_s[parent_orgin].remove(orphan_node)
                                except:
                                    pass
                                tree_s[parent_poss].append(orphan_node)
                                parentPath_s[orphan_node] = ind
                                break
                    # second part
                    if not flag_findParent:
                        visited[orphan_node] = False
                        try:
                            active_s.remove(orphan_node)
                        except:
                            pass
                        for node in tree_s[orphan_node]:
                            orphan_s.append(node)
                            orphanParent_s.append(orphan_node)
                            parentPath_s[node] = -1
                        for ind in self.edge[self.edge.end == orphan_node].index:
                            node = self.edge.start[ind]
                            if residual[ind] > 0 and tree_s.get(node):
                                active_s.insert(0,node)
                        print(orphan_s)
                        del tree_s[orphan_node]
                # sink tree
                while orphan_t:
                    orphan_node = orphan_t.pop(0)
                    parent_orgin = orphanParent_t.pop(0)
                    flag_findParent = False
                    # first part find parent
                    for ind in self.edge[self.edge.start == orphan_node].index:
                        parent_poss = self.edge.end[ind]
                        if residual[ind] > 0 and tree_t.get(parent_poss):
                            # judge it's root
                            node = parent_poss
                            while True:
                                path = parentPath_t[node]
                                if path == -1:
                                    flag_root = False
                                    break
                                node = self.edge.end[path]
                                if node == self.t:
                                    flag_root = True
                                    break
                            if flag_root:
                                flag_findParent = True
                                try:
                                    tree_t[parent_orgin].remove(orphan_node)
                                except:
                                    pass
                                tree_t[parent_poss].append(orphan_node)
                                parentPath_t[orphan_node] = ind
                                break
                    # second part
                    if not flag_findParent:
                        visited[orphan_node] = False
                        try:
                            active_t.remove(orphan_node)
                        except:
                            pass
                        for node in tree_t[orphan_node]:
                            orphan_t.append(node)
                            orphanParent_t.append(orphan_node)
                            parentPath_t[node] = -1
                        for ind in self.edge[self.edge.start == orphan_node].index:
                            node = self.edge.end[ind]
                            if residual[ind] > 0 and tree_t.get(node):
                                active_t.insert(0,node)
                        del tree_t[orphan_node]

    # build graph and calculate
    graph = BoykovKolmogorov(edge, source, sink)
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
