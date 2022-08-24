import osmnx as ox
import networkx as nx

def PrepareMinimalGraph(startPoint, destinationPoint):
    if (startPoint[0] > destinationPoint[0]
            and startPoint[1] > destinationPoint[1]):
        myG = ox.graph_from_bbox(
            startPoint[0]+0.007, destinationPoint[0]-0.007,
            startPoint[1]+0.007, destinationPoint[1]-0.007,
            network_type="drive",
            truncate_by_edge=True
        )
        ox.plot_graph(myG)
    elif (startPoint[0] > destinationPoint[0]
          and startPoint[1] < destinationPoint[1]):
        myG = ox.graph_from_bbox(
            startPoint[0]+0.007, destinationPoint[0]-0.007,
            destinationPoint[1]+0.007, startPoint[1]-0.007,
            network_type="drive",
            truncate_by_edge=True
        )
        ox.plot_graph(myG)
    elif (startPoint[0] < destinationPoint[0]
          and startPoint[1] > destinationPoint[1]):
        myG = ox.graph_from_bbox(
            destinationPoint[0]+0.007, startPoint[0]-0.007,
            startPoint[1]+0.007, destinationPoint[1]-0.007,
            network_type="drive",
            truncate_by_edge=True
        )
        ox.plot_graph(myG)
    else:
        myG = ox.graph_from_bbox(
            destinationPoint[0]+0.007, startPoint[0]-0.007,
            destinationPoint[1]+0.007, startPoint[1]-0.007,
            network_type="drive",
            truncate_by_edge=True
        )
        ox.plot_graph(myG)
