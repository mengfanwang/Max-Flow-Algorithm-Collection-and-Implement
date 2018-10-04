import pandas as pd
import numpy as np

class AugmentDFS:
    # This algorithm is using DFS to find the augmenting paths and accomplish the calculation
    # Input should be simple graph without duplicated edges, loops, and the label of nodes should
    # be continous. The last two nodes should be the source and sink.

    # initialize edge, source and sink
    # edge is a n*3 dataframe. n is the number of edges. One edge and its reversed edge should occur together.
    def __init__(self, edge, source, sink):
        self.edge = edge
        self.edge['start'] = self.edge['start'].astype('int32')
        self.edge['end'] = self.edge['end'].astype('int32')
        self.s = np.int32(source) 
        # sink is the last node all the time
        self.t = np.int32(sink)

    def DFS(self, residual):
        # visited is to show a node can be achieved or not, and wait is used for nodes may be achieved.
        # parentPath shows the path from parent to the node after BFS
        visited = [False] * (self.t+1)
        parentPath = -1*np.int32(np.ones(self.t+1))
        wait = []         

        # start from source
        visited[self.s] = True
        wait.append(self.s)

        # loop
        while wait:
            parentNode = wait.pop()
            for ind in self.edge[self.edge.start == parentNode].index:
                node = self.edge.end[ind]
                if (visited[node] == False) and (residual[ind]) > 0:
                    wait.append(node)
                    visited[node] = True
                    parentPath[node] = ind
                    if node == self.t:
                        return True, parentPath
        return False, []

    def maxflow(self):
        # main function
        maxValue = 0
        count = -1  # the number of augmenting path
        

        residual = self.edge.weight.copy()
        maxFlow = self.edge.weight.copy()
        maxFlow[:] = 0

        while True:

            flag, parentPath = self.DFS(residual)
            count = count + 1
            if not flag:
                break    # same to loop until

            # find the path from s to t
            node = self.t
            bottleneck = float('inf')
            while node != self.s:
                path = parentPath[node]
                bottleneck = min(residual[path], bottleneck)
                node = self.edge.start[path]

            maxValue += bottleneck
            print(maxValue)

            node = self.t
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
        return maxValue, maxFlow, count

