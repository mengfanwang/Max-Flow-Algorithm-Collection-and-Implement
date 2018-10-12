import pandas as pd
import numpy as np

class Dinic:
    ## Dinic with current arc optimaztion

    # initialize edge, source and sink
    # edge is a n*3 dataframe. n is the number of edges. One edge and its reversed edge should occur together.
    def __init__(self, edge, source, sink):
        self.edge = edge
        self.edge['start'] = self.edge['start'].astype('int32')
        self.edge['end'] = self.edge['end'].astype('int32')
        self.s = np.int32(source)
        # sink is the last node all the time
        self.t = np.int32(sink)

    # use BFS to build level graph
    def BFS(self, residual):
        visited = [False] * (self.t+1)
        wait = []
        level = -1*np.int32(np.ones(self.t+1))

        # start from source
        visited[self.s] = True
        wait.append(self.s)
        level[self.s] = 0

        # loop
        while wait:
            parentNode = wait.pop(0)
            for ind in self.edge[self.edge.start == parentNode].index:
                node = self.edge.end[ind]
                if (visited[node] == False) and (residual[ind]) > 0:
                    wait.append(node)
                    visited[node] = True
                    level[node] = level[parentNode] + 1
                    if node == self.t:
                        return level
        return level
    
    #use DFS to find augmenting path based on level graph
    def DFS(self, residual, level,cur):
        visited = [False] * (self.t+1)
        parentPath = -1*np.int32(np.ones(self.t+1))
        wait = []         

        # start from source
        visited[self.s] = True
        wait.append(self.s)

        # loop
        while wait:
            parentNode = wait.pop()
            for ind in self.edge[(self.edge.start == parentNode)&(self.edge.index<=cur[parentNode])].index: #
                node = self.edge.end[ind]
                if (visited[node] == False) and (residual[ind] > 0) and (level[node] == level[parentNode] + 1):
                    wait.append(node)
                    visited[node] = True
                    parentPath[node] = ind
                    if node == self.t:
                        return True, parentPath
        return False, []

    def maxflow(self):
        # main function
        maxValue = 0
        count = 0 # the number of augmenting path
        
        residual = self.edge.weight.copy()
        maxFlow = self.edge.weight.copy()
        maxFlow[:] = 0

        while True:
            level = self.BFS(residual)
            if level[self.t] == -1:
                return maxValue, maxFlow, count
            
            cur = max(self.edge.index)*np.int32(np.ones(self.t+1)) # current arc optimaztion 
            while True:
                flag, parentPath = self.DFS(residual,level,cur)
                count = count + 1
                if not flag:
                    break   

                # find the path from s to t
                node = self.t
                bottleneck = float('inf')
                while node != self.s:
                    path = parentPath[node]
                    bottleneck = min(residual[path], bottleneck)
                    node = self.edge.start[path]
                    cur[node] = path
                    
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