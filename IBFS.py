import pandas as pd
import numpy as np

class IBFS:
    # IBFS is an extension algorithm of BK
    def __init__(self, edge, source, sink):
        self.edge = edge
        self.edge['start'] = self.edge['start'].astype('int32')
        self.edge['end'] = self.edge['end'].astype('int32')
        self.s = np.int32(source)
        # sink is the last node all the time
        self.t = np.int32(sink)

    def Growth(self, residual, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, Ds, Dt, distance_s, distance_t, current_arc_s, current_arc_t, inactive_s, inactive_t):
        # Step 1. Growth with BFS
        increment_s = True
        increment_t = True
        while increment_s or increment_t:
            # source part
            increment_s = False
            increment_t = False
            while active_s:
                parentNode = active_s.pop(0)
                for ind in self.edge[self.edge.start == parentNode].index:
                    node = self.edge.end[ind]
                    if residual[ind] > 0:
                        if tree_t.__contains__(node):
                            # this step is necessary
                            active_s.insert(0, parentNode)
                            connectPath = ind
                            return True, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, connectPath, Ds, Dt, distance_s, distance_t, current_arc_s, current_arc_t, inactive_s, inactive_t
                        else:
                            if visited[node] == False:
                                increment_s = True
                                current_arc_s[node] = self.edge[self.edge.end ==
                                                                node].index[0]
                                distance_s[node] = distance_s[parentNode]+1
                                visited[node] = True
                                tree_s[node] = []
                                tree_s[parentNode].append(node)
                                parentPath_s[node] = ind
            if not active_s:
                Ds = Ds + 1
                active_s = ((np.argwhere(distance_s == Ds).T.tolist()[
                    0]))  # find distance == Ds
                # if -Ds == inactive_s[0]:
                #     for node in inactive_s:
                #         if node in active_s:
                #             active_s.remove(node)

            # sink part
            while active_t:
                parentNode = active_t.pop(0)
                for ind in self.edge[self.edge.end == parentNode].index:
                    node = self.edge.start[ind]
                    if residual[ind] > 0:
                        if tree_s.__contains__(node):
                            active_t.insert(0, parentNode)
                            connectPath = ind
                            return True, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, connectPath, Ds, Dt, distance_s, distance_t, current_arc_s, current_arc_t, inactive_s, inactive_t
                        else:
                            if visited[node] == False:
                                increment_t = True
                                current_arc_t[node] = self.edge[self.edge.start ==
                                                                node].index[0]
                                distance_t[node] = distance_t[parentNode]+1
                                visited[node] = True
                                tree_t[node] = []
                                tree_t[parentNode].append(node)
                                parentPath_t[node] = ind
            if not active_t:
                Dt = Dt + 1
                active_t = (np.argwhere(distance_t == Dt).T.tolist()[
                    0])  # find distance == Dt
                # if -Dt == inactive_t[0]:
                #     for node in inactive_t:
                #         if node in active_t:
                #             active_t.remove(node)

        return False, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, 0, Ds, Dt, distance_s, distance_t, current_arc_s, current_arc_t, inactive_s, inactive_t

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
        Ds = 0
        Dt = 0
        distance_s = -1*np.int32(np.ones(self.t+1))
        distance_s[self.s] = 0
        distance_t = -1*np.int32(np.ones(self.t+1))
        distance_t[self.t] = 0
        current_arc_s = -1*np.int32(np.ones(self.t+1))
        current_arc_t = -1*np.int32(np.ones(self.t+1))
        inactive_s = [1]
        inactive_t = [1]

        while True:
            # Step 1
            flag, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, connectPath, Ds, Dt, distance_s, distance_t, current_arc_s, current_arc_t, inactive_s, inactive_t = self.Growth(
                residual, tree_s, tree_t, active_s, active_t, parentPath_s, parentPath_t, visited, Ds, Dt, distance_s, distance_t, current_arc_s, current_arc_t, inactive_s, inactive_t)
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
            if inactive_s[0] != -Ds-1:
                inactive_s = [-Ds-1]
            while orphan_s:
                orphan_node = orphan_s.pop(0)
                parent_orgin = orphanParent_s.pop(0)
                # delete from its parent
                if tree_s.__contains__(parent_orgin):
                    tree_s[parent_orgin].remove(orphan_node)
                flag_findParent = False
                # relabel operation
                for ind in self.edge[(self.edge.index >= current_arc_s[orphan_node]) & (self.edge.end == orphan_node)].index:
                    parent_poss = self.edge.start[ind]
                    if (distance_s[parent_poss] == distance_s[orphan_node] - 1) and residual[ind] > 0 and tree_s.get(parent_poss):
                        flag_findParent = True
                        current_arc_s[orphan_node] = ind
                        tree_s[parent_poss].append(orphan_node)
                        parentPath_s[orphan_node] = ind
                        break
                # orphan relabel operation
                if not flag_findParent:
                    distance = Ds + 1
                    for ind in self.edge[self.edge.end == orphan_node].index:
                        node = self.edge.start[ind]
                        if 0 < distance_s[node] < distance and residual[ind] > 0:
                            distance = distance_s[node]
                            parent_poss = node
                            parentPath = ind
                    if distance <= Ds:
                        flag_findParent = True
                        current_arc_s[orphan_node] = parentPath
                        tree_s[parent_poss].append(orphan_node)
                        parentPath_s[orphan_node] = parentPath
                        distance_s[orphan_node] = distance_s[parent_poss] + 1
                        # add its children as orphans
                        for node in tree_s[orphan_node]:
                            if not (node in orphan_s):
                                orphan_s.append(node)
                                orphanParent_s.append(orphan_node)
                                parentPath_s[node] = -1
                        # add its neighbors as actives
                        # for ind in self.edge[self.edge.end == orphan_node].index:
                        #     node = self.edge.start[ind]
                        #     if residual[ind] > 0 and tree_s.__contains__(node) and not (node in active_s):
                        #         active_s.insert(0,node)
                # third part
                if not flag_findParent:
                    visited[orphan_node] = False
                    distance_s[orphan_node] = -1
                    current_arc_s[orphan_node] = -1
                    # add its children as orphans
                    for node in tree_s[orphan_node]:
                        if not (node in orphan_s):
                            orphan_s.append(node)
                            orphanParent_s.append(orphan_node)
                            parentPath_s[node] = -1
                    # add its neighbors as actives
                    # for ind in self.edge[self.edge.end == orphan_node].index:
                    #     node = self.edge.start[ind]
                    #     if residual[ind] > 0 and tree_s.__contains__(node) and not (node in active_s):
                    #         active_s.insert(0,node)
                    # delete from tree
                    del tree_s[orphan_node]
                if orphan_node in active_s and not flag_findParent:
                    active_s.remove(orphan_node)
                if distance_s[orphan_node] == Ds + 1:
                    inactive_s.append(orphan_node)

            # sink tree
            if inactive_t[0] != -Dt-1:
                inactive_t = [-Dt-1]
            while orphan_t:
                orphan_node = orphan_t.pop(0)
                parent_orgin = orphanParent_t.pop(0)
                # delete from its parent
                if tree_t.__contains__(parent_orgin):
                    tree_t[parent_orgin].remove(orphan_node)
                flag_findParent = False
                # relabel operation
                for ind in self.edge[(self.edge.index >= current_arc_t[orphan_node]) & (self.edge.start == orphan_node)].index:
                    parent_poss = self.edge.end[ind]
                    if residual[ind] > 0 and (distance_t[parent_poss] == distance_t[orphan_node] - 1) and tree_t.get(parent_poss):
                        flag_findParent = True
                        current_arc_t[orphan_node] = ind
                        tree_t[parent_poss].append(orphan_node)
                        parentPath_t[orphan_node] = ind
                        break
                # orphan relabel operation
                if not flag_findParent:
                    distance = Dt
                    for ind in self.edge[self.edge.start == orphan_node].index:
                        node = self.edge.end[ind]
                        if 0 < distance_t[node] < distance and residual[ind] > 0:
                            distance = distance_t[node]
                            parent_poss = node
                            parentPath = ind
                    if distance < Dt:
                        flag_findParent = True
                        current_arc_t[orphan_node] = parentPath
                        tree_t[parent_poss].append(orphan_node)
                        parentPath_t[orphan_node] = parentPath
                        distance_t[orphan_node] = distance_t[parent_poss] + 1
                        # add its children as orphans
                        for node in tree_t[orphan_node]:
                            if not (node in orphan_t):
                                orphan_t.append(node)
                                orphanParent_t.append(orphan_node)
                                parentPath_t[node] = -1
                        # add its neighbors as actives
                        # for ind in self.edge[self.edge.start == orphan_node].index:
                        #     node = self.edge.end[ind]
                        #     if residual[ind] > 0 and tree_t.__contains__(node) and not (node in active_t):
                        #         active_t.insert(0,node)
                # third part
                if not flag_findParent:
                    visited[orphan_node] = False
                    distance_t[orphan_node] = -1
                    current_arc_t[orphan_node] = -1
                    # add its children as orphans
                    for node in tree_t[orphan_node]:
                        if not (node in orphan_t):
                            orphan_t.append(node)
                            orphanParent_t.append(orphan_node)
                            parentPath_t[node] = -1
                    # add its neighbors as actives
                    # for ind in self.edge[self.edge.start == orphan_node].index:
                    #     node = self.edge.end[ind]
                    #     if residual[ind] > 0 and tree_t.__contains__(node) and not (node in active_t):
                    #         active_t.insert(0,node)
                    # delete from tree
                    del tree_t[orphan_node]
                if orphan_node in active_t and not flag_findParent:
                    active_t.remove(orphan_node)
                if distance_t[orphan_node] == Dt and orphan_node in active_t:
                    inactive_t.append(orphan_node)
                    # active_t.remove(orphan_node)
