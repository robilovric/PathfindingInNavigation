import osmnx as ox
import networkx as nx
import geopandas
import folium
from folium.plugins import MousePosition, Geocoder
import io
import sys
from PyQt5 import QtWebEngineWidgets, QtWidgets
import MyDijkstra


class Window(QtWidgets.QMainWindow):
    startMarkerCount = 0
    destMarkerCount = 0
    startPoint = []
    destinationPoint = []

    def __init__(self):
        super().__init__()
        self.InitWindow()

    def InitWindow(self):
        self.setWindowTitle(self.tr("DIJKSTRA FOR NAVIGATION"))
        self.setFixedSize(1500, 800)
        self.ArrangeUI()

    def ArrangeUI(self):
        self.startLatLabel = QtWidgets.QLabel(self.tr("Start latitude:"))
        self.startLonLabel = QtWidgets.QLabel(self.tr("Start longitude:"))
        self.startLatEdit = QtWidgets.QLineEdit()
        self.startLonEdit = QtWidgets.QLineEdit()
        self.destLatLabel = QtWidgets.QLabel(self.tr("Destination latitude:"))
        self.destLonLabel = QtWidgets.QLabel(self.tr("Destination longitude:"))
        self.destLatEdit = QtWidgets.QLineEdit()
        self.destLonEdit = QtWidgets.QLineEdit()
        self.addStartMarkerBtn = QtWidgets.QPushButton(self.tr("Add start location"))
        self.addDestMarkerBtn = QtWidgets.QPushButton(self.tr("Add destination location"))
        self.findPathButton = QtWidgets.QPushButton(self.tr("Visualize path"))
        self.clearButton = QtWidgets.QPushButton(self.tr("Clear map"))

        self.addStartMarkerBtn.clicked.connect(self.AddStartButtonClicked)
        self.addDestMarkerBtn.clicked.connect(self.AddDestButtonClicked)
        self.findPathButton.clicked.connect(self.plot_path)
        self.clearButton.clicked.connect(self.ClearMap)

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setContentsMargins(5, 5, 5, 5)

        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)
        mainLayout = QtWidgets.QHBoxLayout(centralWidget)

        controlContainer = QtWidgets.QWidget()
        gridLayout = QtWidgets.QGridLayout(controlContainer)
        gridLayout.addWidget(self.startLatLabel, 0, 0)
        gridLayout.addWidget(self.startLatEdit, 0, 1)
        gridLayout.addWidget(self.startLonLabel, 1, 0)
        gridLayout.addWidget(self.startLonEdit, 1, 1)
        gridLayout.addWidget(self.addStartMarkerBtn, 2, 0, 1, 2)
        gridLayout.addWidget(self.destLatLabel, 3, 0)
        gridLayout.addWidget(self.destLatEdit, 3, 1)
        gridLayout.addWidget(self.destLonLabel, 4, 0)
        gridLayout.addWidget(self.destLonEdit, 4, 1)
        gridLayout.addWidget(self.addDestMarkerBtn, 5, 0, 1, 2)
        gridLayout.addWidget(self.findPathButton, 6, 0, 1, 2)
        gridLayout.addWidget(self.clearButton, 7, 0, 1, 2)
        mainLayout.addWidget(controlContainer)
        mainLayout.addWidget(self.view, stretch=1)

        self.m = folium.Map(
            location=[43.5347, 16.3600],
            tiles="OpenStreetMap",
            zoom_start=13
        )
        self.m.add_child(folium.LatLngPopup())

        MousePosition(
            position="bottomleft",
            separator=" | ",
            empty_string="NaN",
            num_digits=7,
            prefix="Coordinates:",
        ).add_to(self.m)

        Geocoder().add_to(self.m)

        data = io.BytesIO()
        self.m.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())

    def AddStartButtonClicked(self):
        if Window.startMarkerCount == 1:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)
            msgBox.setText("You can have only one starting point!\nUse Clear map button to be able to add a new point.")
            msgBox.setWindowTitle("WARNING")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msgBox.exec()
            return
        lat = self.startLatEdit.text()
        lon = self.startLonEdit.text()
        Window.startMarkerCount += 1
        Window.startPoint.append(float(lat))
        Window.startPoint.append(float(lon))
        self.UpdateMap(lat, lon, "blue", "fa-rocket", "Starting point!")

    def AddDestButtonClicked(self):
        if Window.destMarkerCount == 1:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)
            msgBox.setText("You can have only one destination!\nUse Clear map button to be able to add a new point.")
            msgBox.setWindowTitle("WARNING")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msgBox.exec()
            return
        lat = self.destLatEdit.text()
        lon = self.destLonEdit.text()
        Window.destMarkerCount += 1
        Window.destinationPoint.append(float(lat))
        Window.destinationPoint.append(float(lon))
        self.UpdateMap(lat, lon, "red", "fa-star", "Destination point!")

    def UpdateMap(self, lat, lon, color, icon, popup):
        self.m.location = [float(lat), float(lon)]
        folium.Marker(
            location=[float(lat), float(lon)],
            icon=folium.Icon(color=color, icon=icon, prefix="fa"),
            popup=popup
        ).add_to(self.m)
        data = io.BytesIO()
        self.m.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())
        self.statusBar().showMessage("Marker added!")

    def ClearMap(self):
        if len(Window.startPoint) == 2:
            self.m = folium.Map(
                location=[Window.startPoint[0], Window.startPoint[1]],
                tiles="OpenStreetMap",
                zoom_start=13
            )
            self.m.add_child(folium.LatLngPopup())

            MousePosition(
                position="bottomleft",
                separator=" | ",
                empty_string="NaN",
                num_digits=7,
                prefix="Coordinates:"
            ).add_to(self.m)

            Geocoder().add_to(self.m)

            data = io.BytesIO()
            self.m.save(data, close_file=False)
            self.view.setHtml(data.getvalue().decode())

            Window.startMarkerCount = 0
            Window.destMarkerCount = 0
            Window.startPoint = []
            Window.destinationPoint = []

    def plot_path(self):
        self.Graph = MyDijkstra.PrepareMinimalGraph(Window.startPoint, Window.destinationPoint)
        originNode = ox.nearest_nodes(self.Graph, Window.startPoint[1], Window.startPoint[0])
        destinationNode = ox.nearest_nodes(self.Graph, Window.destinationPoint[1], Window.destinationPoint[0])
        ox.add_edge_speeds(self.Graph)
        ox.add_edge_travel_times(self.Graph)
        #route = nx.shortest_path(self.Graph, origin_node, destination_node, weight="length")
        shortestRoute = MyDijkstra.Dijkstra(self.Graph, originNode, destinationNode)
        fastestRoute = MyDijkstra.Dijkstra(self.Graph, originNode, destinationNode, mode="travel_time")
        ox.plot_route_folium(self.Graph, shortestRoute,
                             route_map=self.m,
                             popup_attribute="name",
                             tiles="OpenStreetMap",
                             zoom=13
                             )
        ox.plot_route_folium(self.Graph, fastestRoute,
                             route_map=self.m,
                             tiles="OpenStreetMap",
                             zoom=13, color="red")
        data = io.BytesIO()
        self.m.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())


if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec())
