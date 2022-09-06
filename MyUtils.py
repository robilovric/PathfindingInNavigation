from PyQt5.QtWidgets import *

class Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.left = 100
        self.top = 100
        self.width = 1000
        self.height = 700
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.show()


def createTable(G, route, nodesVsited):
    tableWidget = QTableWidget()
    tableWidget.setColumnCount(5)
    tableWidget.setHorizontalHeaderLabels(["Action", "Street name", "Length [m]",
                                           "Travel time [s]", "Speed limit [km/h]"])
    params = ["name", "length", "travel_time", "speed_kph"]
    row = 0
    totalDistance = 0
    totalTime = 0

    for i in range(len(route)-1):
        tableWidget.insertRow(row)
        tableWidget.setItem(row, 0, QTableWidgetItem("Stay on"))
        col = 1
        for param in params:
            try:
                temp = G[route[i]][route[i+1]][0][param]
                if param == "travel_time":
                    totalTime += temp
                if param == "length":
                    totalDistance += temp
                    temp = round(temp, 2)
                tableWidget.setItem(row, col, QTableWidgetItem(str(temp)))
                col += 1
            except KeyError:
                tableWidget.setItem(row, 0, QTableWidgetItem("Turn accordingly"))
                temp = G[route[i]][route[i + 1]][0]["highway"]
                tableWidget.setItem(row, 1, QTableWidgetItem("Turn type: " + temp))
                col += 1
                continue
        row += 1
    tableWidget.insertRow(row)
    tableWidget.setItem(row, 0, QTableWidgetItem("DESTINATION REACHED!"))
    tableWidget.setItem(row, 1, QTableWidgetItem("TOTAL:"))
    totalDistance /= 1000
    totalDistance = round(totalDistance, 2)
    tableWidget.setItem(row, 2, QTableWidgetItem(str(totalDistance) + " km"))
    min, s = divmod(totalTime, 60)
    h, min = divmod(min, 60)
    if h == 0:
        tableWidget.setItem(row, 3, QTableWidgetItem(f"{min:.0f} min {s:.0f} s"))
    else:
        tableWidget.setItem(row, 3, QTableWidgetItem(f"{h:.0f} h {min:.0f} min {s:.0f} s"))
    row += 1
    tableWidget.insertRow(row)
    tableWidget.setItem(row, 1, QTableWidgetItem("NODES VISITED:"))
    tableWidget.setItem(row, 2, QTableWidgetItem(str(nodesVsited)))

    tableWidget.horizontalHeader().setStretchLastSection(True)
    tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    return tableWidget

def ValidateData(lat, lon):
    min_lat = - 90
    max_lat = 90
    min_lon = - 180
    max_lon = 180
    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return False
    else:
        if min_lat < lat < max_lat and min_lon < lon < max_lon:
            return True
        else:
            return False
    return False

def GetStats(G, route, nodesVisited, shortest=True):
    dlg = Dialog()
    table = createTable(G, route, nodesVisited)
    dlg.layout.addWidget(table)
    if shortest:
        dlg.title = "Shortest path statistics"
        dlg.setWindowTitle(dlg.title)
    else:
        dlg.title = "Fastest path statistics"
        dlg.setWindowTitle(dlg.title)
    dlg.exec_()
