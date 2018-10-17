import pandas as pd
import numpy as np

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
            if active_s:
                parentNode = active_s.pop(0)
                for ind in self.edge[self.edge.start == parentNode].index:
                    node = self.edge.end[ind]
                    if residual[ind]>0:
                        if tree_t.__contains__(node):
                            active_s.insert(0, parentNode)  # this step is necessary
                            connectPath = ind
                            return True, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, connectPath
                        else:
                            if visited[node] == False:
                                active_s.append(node)
                                visited[node] = True
                                tree_s[node] = []
                                tree_s[parentNode].append(node)
                                parentPath_s[node] = ind
            # sink part
            if active_t:
                parentNode = active_t.pop(0)
                for ind in self.edge[self.edge.end == parentNode].index:
                    node = self.edge.start[ind]
                    if residual[ind] > 0:
                        if tree_s.__contains__(node):
                            active_t.insert(0, parentNode)
                            connectPath = ind
                            return True, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, connectPath
                        else:
                            if visited[node] == False:
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
                # delete from its parent
                if tree_s.__contains__(parent_orgin):
                    tree_s[parent_orgin].remove(orphan_node)
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
                            tree_s[parent_poss].append(orphan_node)
                            parentPath_s[orphan_node] = ind
                            break
                # second part
                if not flag_findParent:
                    visited[orphan_node] = False
                    if orphan_node in active_s:
                        active_s.remove(orphan_node)
                    # add its children as orphans
                    for node in tree_s[orphan_node]:
                        if not (node in orphan_s):    
                            orphan_s.append(node)
                            orphanParent_s.append(orphan_node)
                            parentPath_s[node] = -1
                    # add its neighbors as actives
                    for ind in self.edge[self.edge.end == orphan_node].index:
                        node = self.edge.start[ind]
                        if residual[ind] > 0 and tree_s.__contains__(node) and not (node in active_s):
                            active_s.insert(0,node)
                    # delete from tree
                    del tree_s[orphan_node]
            # sink tree
            while orphan_t:
                orphan_node = orphan_t.pop(0)
                parent_orgin = orphanParent_t.pop(0)
                flag_findParent = False
                # delete from its parent
                if tree_t.__contains__(parent_orgin):
                    tree_t[parent_orgin].remove(orphan_node)
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
                            tree_t[parent_poss].append(orphan_node)
                            parentPath_t[orphan_node] = ind
                            break
                # second part
                if not flag_findParent:
                    visited[orphan_node] = False
                    if orphan_node in active_t:
                        active_t.remove(orphan_node)
                    for node in tree_t[orphan_node]: 
                        if not (node in orphan_t):
                            orphan_t.append(node)
                            orphanParent_t.append(orphan_node)
                            parentPath_t[node] = -1
                    for ind in self.edge[self.edge.start == orphan_node].index:
                        node = self.edge.end[ind]
                        if residual[ind] > 0 and tree_t.__contains__(node) and not (node in active_t):
                            active_t.insert(0,node)
                    del tree_t[orphan_node]