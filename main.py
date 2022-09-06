from PyQt5 import QtWebEngineWidgets, QtWidgets
from folium.plugins import MousePosition, Geocoder
import folium
import osmnx as ox
import MyDijkstra
import MyUtils
import io
import sys


class Window(QtWidgets.QMainWindow):

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
        self.findPathButton.setEnabled(False)
        self.clearButton = QtWidgets.QPushButton(self.tr("Clear map"))
        self.clearButton.setEnabled(False)
        self.pathFastestStatsBtn = QtWidgets.QPushButton(self.tr("Fastest path statistics"))
        self.pathFastestStatsBtn.setEnabled(False)
        self.pathShortestStatsBtn = QtWidgets.QPushButton(self.tr("Shortest path statistics"))
        self.pathShortestStatsBtn.setEnabled(False)

        self.addStartMarkerBtn.clicked.connect(self.AddStartButtonClicked)
        self.addDestMarkerBtn.clicked.connect(self.AddDestButtonClicked)
        self.findPathButton.clicked.connect(self.PlotPath)
        self.pathFastestStatsBtn.clicked.connect(self.GetStatisticFast)
        self.pathShortestStatsBtn.clicked.connect(self.GetStatisticsShort)
        self.clearButton.clicked.connect(self.ClearMap)

        self.view = QtWebEngineWidgets.QWebEngineView()
        self.view.setContentsMargins(5, 5, 5, 5)

        self.PopulateLayout()
        self.ArrangeMap()
        return

    def PopulateLayout(self):
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
        gridLayout.addWidget(self.findPathButton, 7, 0, 1, 2)
        gridLayout.addWidget(self.pathShortestStatsBtn, 8, 0, 1, 2)
        gridLayout.addWidget(self.pathFastestStatsBtn, 9, 0, 1, 2)
        gridLayout.addWidget(self.clearButton, 10, 0, 1, 2)
        mainLayout.addWidget(controlContainer)
        mainLayout.addWidget(self.view, stretch=1)
        return

    def ArrangeMap(self, zoom=13, lat=43.5347, lon=16.36, clean=False):
        try:
            self.m = folium.Map(
                location=[lat, lon],
                tiles="OpenStreetMap",
                zoom_start=zoom
            )
        except Exception:
            self.m = folium.Map(
                location=[43.5347, 16.36],
                tiles="OpenStreetMap",
                zoom_start=zoom
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
        if clean:
            Window.startMarkerCount = 0
            Window.destMarkerCount = 0
            Window.nodesVisitedFastest = 0
            Window.nodesVisitedShortest = 0
            Window.startPoint = []
            Window.destinationPoint = []

    def LaunchMsgBox(self, title, text, severityHigh=False):
        msgBox = QtWidgets.QMessageBox()
        if severityHigh:
            msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        else:
            msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setWindowTitle(title)
        msgBox.setText(text)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msgBox.exec()
        return

    def AddStartButtonClicked(self):
        if Window.startMarkerCount == 1:
            self.LaunchMsgBox("WARNING",
                              "You can have only one starting point!\n"
                              "Use Clear map button to be able to add a new point.")
            return
        lat = self.startLatEdit.text()
        lon = self.startLonEdit.text()
        if MyUtils.ValidateData(lat, lon):
            lat = float(lat)
            lon = float(lon)
            Window.startMarkerCount += 1
            Window.startPoint.append(lat)
            Window.startPoint.append(lon)
            self.UpdateMap(lat, lon, "blue", "fa-rocket", "Starting point!")
            self.clearButton.setEnabled(True)
            if Window.startMarkerCount + Window.destMarkerCount == 2:
                self.findPathButton.setEnabled(True)
            return
        self.LaunchMsgBox("ERROR",
                          "Please enter valid values as coordinates!\n"
                          "Look at the bottom left corner to get sense for values.", True)

    def AddDestButtonClicked(self):
        if Window.destMarkerCount == 1:
            self.LaunchMsgBox("WARNING", "You can have only one destination!\n"
                                         "Use Clear map button to be able to add a new point.")
            return
        lat = self.destLatEdit.text()
        lon = self.destLonEdit.text()
        if MyUtils.ValidateData(lat, lon):
            lat = float(lat)
            lon = float(lon)
            Window.destMarkerCount += 1
            Window.destinationPoint.append(lat)
            Window.destinationPoint.append(lon)
            self.UpdateMap(lat, lon, "red", "fa-star", "Destination point!")
            self.clearButton.setEnabled(True)
            if Window.startMarkerCount + Window.destMarkerCount == 2:
                self.findPathButton.setEnabled(True)
            return
        self.LaunchMsgBox("ERROR",
                          "Please enter valid values as coordinates!\n"
                          "Look at the bottom left corner to get sense for values.", True)

    def UpdateMap(self, lat, lon, color, icon, popup):
        self.m.location = [lat, lon]
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color=color, icon=icon, prefix="fa"),
            popup=popup,
            zoom=10
        ).add_to(self.m)
        data = io.BytesIO()
        self.m.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())
        self.statusBar().showMessage(f"{popup.split()[0]} marker added!")

    def ClearMap(self):
        self.ArrangeMap(15, Window.startPoint[0],
                        Window.startPoint[1],
                        clean=True)
        self.findPathButton.setEnabled(False)
        self.pathFastestStatsBtn.setEnabled(False)
        self.pathShortestStatsBtn.setEnabled(False)
        self.clearButton.setEnabled(False)

    def PrepareAlgorithmParameters(self):
        self.Graph = MyDijkstra.PrepareMinimalGraph(Window.startPoint, Window.destinationPoint)

        self.originNode = ox.nearest_nodes(self.Graph, Window.startPoint[1], Window.startPoint[0])
        self.destinationNode = ox.nearest_nodes(self.Graph, Window.destinationPoint[1], Window.destinationPoint[0])

        ox.add_edge_speeds(self.Graph)
        ox.add_edge_travel_times(self.Graph)

    def PlotPath(self):
        self.PrepareAlgorithmParameters()
        self.shortestRoute, Window.nodesVisitedShortest = MyDijkstra.Dijkstra(self.Graph, self.originNode, self.destinationNode)
        self.fastestRoute, Window.nodesVisitedFastest = MyDijkstra.Dijkstra(self.Graph, self.originNode,
                                                                            self.destinationNode, mode="travel_time")
        ox.plot_route_folium(self.Graph, self.shortestRoute,
                             route_map=self.m,
                             popup_attribute="name",
                             tiles="OpenStreetMap",
                             zoom=13
                             )
        ox.plot_route_folium(self.Graph, self.fastestRoute,
                             route_map=self.m,
                             tiles="OpenStreetMap",
                             zoom=13, color="red")
        data = io.BytesIO()
        self.m.save(data, close_file=False)
        self.view.setHtml(data.getvalue().decode())
        self.pathFastestStatsBtn.setEnabled(True)
        self.pathShortestStatsBtn.setEnabled(True)
        self.statusBar().showMessage("Path visualised!")

    def GetStatisticsShort(self):
        MyUtils.GetStats(self.Graph, self.shortestRoute, Window.nodesVisitedShortest)

    def GetStatisticFast(self):
        MyUtils.GetStats(self.Graph, self.fastestRoute, Window.nodesVisitedFastest, shortest=False)

    startMarkerCount = 0
    destMarkerCount = 0
    nodesVisitedFastest = 0
    nodesVisitedShortest = 0
    startPoint = []
    destinationPoint = []


if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(App.exec())
