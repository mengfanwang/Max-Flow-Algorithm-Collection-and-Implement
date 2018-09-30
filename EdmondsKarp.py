import pandas as pd
import numpy as np
import queue

class EdmondsKarp:
    ## This algorithm is using BFS to find the augmenting paths and accomplish the calculation
    ## Input should be simple graph without duplicated edges, loops, and the label of nodes should
    ## be continous. The last two nodes should be the source and sink.

    # initialize edge, source and sink
    # edge is a n*3 dataframe. n is the number of edges. One edge and its reversed edge shhould occur together.
    def __init__(self, edge, source, sink):
        self.edge = edge
        self.edge['start'] = self.edge['start'].astype('int32')
        self.edge['end'] = self.edge['end'].astype('int32')
        self.s = np.int32(source)
        # sink is the biggest node all the time
        self.t = np.int32(sink)

    # use BFS to find a augument path
    def BFS(self, residual):
        # visited is to show a node can be achieved or not, and wait is used for nodes may be achieved.
        # parentPath shows the path from parent to the node after BFS
        visited = [False] * self.t
        wait = queue.Queue()
        parentPath = -1*np.int32(np.ones(self.t))

        # start from source
        visited[self.s - 1] = True
        wait.put(self.s)

        # loop
        while not wait.empty():
            parentNode = wait.get()
            for ind in self.edge[self.edge.start == parentNode].index:
                node = self.edge.end[ind]
                if (visited[node - 1] == False) and (residual[ind]) > 0:
                    wait.put(node)
                    visited[node - 1] = True
                    parentPath[node - 1] = ind
                    if node == self.t:
                        return True, parentPath
        return False, []

    def maxflow(self):
        # main function
        maxValue = 0
        
        residual = self.edge.weight

        while True:

            flag, parentPath = self.BFS(residual)
            if not flag:
                break    # same to loop until

            # find the path from s to t
            node = self.t
            bottleneck = float('inf')
            while node != self.s:
                path = parentPath[node-1]
                bottleneck = min(residual[path], bottleneck)
                node = self.edge.start[path]

            maxValue += bottleneck
            print(maxValue)

            node = self.t
            while True:
                path = parentPath[node-1]
                if path % 2 == 0:
                    residual[path] -= bottleneck
                    residual[path+1] += bottleneck
                else:
                    residual[path-1] += bottleneck
                    residual[path] -= bottleneck
                node = self.edge.start[path]
                if node == self.s:
                    break

        return maxValue
