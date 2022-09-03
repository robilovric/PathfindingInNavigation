import osmnx as ox
import networkx as nx
from math import inf
import heapq

def PrepareMinimalGraph(startPoint, destinationPoint):
    if (startPoint[0] > destinationPoint[0]
            and startPoint[1] > destinationPoint[1]):
        myG = ox.graph_from_bbox(
            startPoint[0]+0.007, destinationPoint[0]-0.007,
            startPoint[1]+0.007, destinationPoint[1]-0.007,
            network_type="drive",
            truncate_by_edge=True
        )
        #ox.plot_graph(myG)
    elif (startPoint[0] > destinationPoint[0]
          and startPoint[1] < destinationPoint[1]):
        myG = ox.graph_from_bbox(
            startPoint[0]+0.007, destinationPoint[0]-0.007,
            destinationPoint[1]+0.007, startPoint[1]-0.007,
            network_type="drive",
            truncate_by_edge=True
        )
        #ox.plot_graph(myG)
    elif (startPoint[0] < destinationPoint[0]
          and startPoint[1] > destinationPoint[1]):
        myG = ox.graph_from_bbox(
            destinationPoint[0]+0.007, startPoint[0]-0.007,
            startPoint[1]+0.007, destinationPoint[1]-0.007,
            network_type="drive",
            truncate_by_edge=True
        )
        #ox.plot_graph(myG)
    else:
        myG = ox.graph_from_bbox(
            destinationPoint[0]+0.007, startPoint[0]-0.007,
            destinationPoint[1]+0.007, startPoint[1]-0.007,
            network_type="drive",
            truncate_by_edge=True
        )
        #ox.plot_graph(myG)

    return myG

def Dijkstra(G, startNode, endNode, mode="length"):
    previous = {nodes: None for nodes in list(G)}
    cost = {nodes: inf for nodes in list(G)}
    cost[startNode] = 0
    visitedNodes = []
    minHeap = []
    heapq.heappush(minHeap, [0, startNode])

    while minHeap:
        currentCost, currentNode = heapq.heappop(minHeap)
        visitedNodes.append(currentNode)
        for neighbor in G.neighbors(currentNode):
            newCost = currentCost + G.get_edge_data(currentNode, neighbor)[0][mode]
            if newCost < cost[neighbor]:
                cost[neighbor] = newCost
                previous[neighbor] = currentNode
                heapq.heappush(minHeap, (cost[neighbor], neighbor))
        if endNode in visitedNodes:
            optimalPath = []
            optimalPath.append(endNode)
            temp = endNode
            while previous[temp] != None:
                optimalPath.append(previous[temp])
                temp = previous[temp]

            optimalPath.reverse()
            return optimalPath









