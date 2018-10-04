import pandas as pd
import numpy as np
import queue


def BFS(residual, s, t):
    # visited is to show a node can be achieved or not, and wait is used for nodes may be achieved.
    # parentPath shows the path from parent to the node after BFS
    visited = [False] * (t+1)
    wait = queue.Queue()

    # start from source
    visited[s] = True
    wait.put(s)
    cut = []

    # loop
    while not wait.empty():
        parentNode = wait.get()
        for ind in residual[residual.start == parentNode].index:
            node = residual.end[ind]
            if (visited[node] == False) and (residual.weight[ind]) > 0.0000001:
                wait.put(node)
                visited[node] = True
                cut.append(node)

    return cut


def validate(graph, flow, value, maxValue, sCut):
    # graph is the original graph. flow/valye is the result, maxFlow/maxValue/sCut/tCut are the reference
    error = 0.0000001

    # 1.flow should larger than zero
    flag_zero = all(flow >= -error)
    print('All flows larger than zero:', flag_zero)

    # 2.smaller than capacity
    flag_capacity = all(flow <= graph.edge.weight + error)
    print('All flows smaller than capacity:', flag_capacity)

    # 3.flow in = flow out
    flag_io = True
    for node in range(1, graph.s):
        flow_in = sum(flow[graph.edge.end == node])
        flow_out = sum(flow[graph.edge.start == node])
        if abs(flow_in - flow_out) > error:
            flag_io = False
    print('For all nodes, in flows equal to out flows:', flag_io)

    # 4. soruce flow = sink flow = max flow
    flag_st = True
    flow_source = sum(flow[graph.edge.start == graph.s])
    flow_sink = sum(flow[graph.edge.end == graph.t])
    if abs(flow_source - maxValue) > error:
        flag_st = False
    if abs(flow_sink - maxValue) > error:
        flag_st = False
    if abs(value - maxValue) > error:
        flag_st = False
    print('The result of max value is:', flag_st)

    # 5. find cut. sCut doesn't include the source
    residualFlow = graph.edge.weight.copy()
    for ind in residualFlow.index:
        if ind % 2 == 0:
            residualFlow[ind] -= flow[ind]
            residualFlow[ind+1] += flow[ind]
        else:
            residualFlow[ind] -= flow[ind]
            residualFlow[ind-1] += flow[ind]
    residual = pd.DataFrame({'start': graph.edge.start.values, 'end': graph.edge.end.values, 'weight': residualFlow.values })
    cut = BFS(residual, graph.s, graph.t)
    cut = set(cut)
    print('Cut is correct:',cut == set(sCut))

    if flag_zero and flag_capacity and flag_io and flag_st and cut == set(sCut):
        print('All conditions are statisfied! Congratulations!')
    else:
        print('Some condtions are wrong. Please check again.')  