from os import path

from PyQt5.QtWidgets import QPushButton, QDialog, QVBoxLayout, QLineEdit, QLabel
from PyQt5.QtGui import QIntValidator
from qgis.gui import QgsFileWidget
from qgis.core import QgsVectorLayer, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsVectorFileWriter

def remove_init(main_dialog, layout):
    button = QPushButton('Remove small polygons')
    button.clicked.connect(lambda: show_dialog(main_dialog))
    layout.addWidget(button)

def show_dialog(main_dialog):
    Dialog = WidgetDialog(main_dialog)

class WidgetDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.addContent()

    def addContent(self):
        self.show()
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        layer_input = QgsFileWidget(self)
        resolution_input = QLineEdit(self)
        
        layout.addWidget(QLabel("Select layer:"))
        layout.addWidget(layer_input)
        layout.addWidget(QLabel("Desired resolution 1:"))
        layout.addWidget(resolution_input)

        resolution_input.setPlaceholderText("Desired resolution")
        resolution_input.setValidator(QIntValidator())

        button = QPushButton('Remove small polygons')
        button.clicked.connect(lambda: calculate(resolution_input, layer_input))
        layout.addWidget(button)
    
def calculate(resolution_input, layer_input):
    layer_path = layer_input.filePath()
    splitext = path.splitext(layer_path)
    layer_file_name = splitext[0]
    layer_file_extension = splitext[1]
    parent_dir = path.dirname(layer_file_name)
    layer_file_name = path.basename(layer_file_name)

    layer = QgsVectorLayer(layer_path, "original", "ogr")
    result_path = path.join(parent_dir, layer_file_name + "_removed_small_polygons" + layer_file_extension)
    QgsVectorFileWriter.writeAsVectorFormat(
        layer,
        result_path,
        "utf-8",
        layer.crs(),
        "ESRI Shapefile"
        )
    new_layer = QgsVectorLayer(result_path, "removed small polygons", "ogr")

    data_provider = new_layer.dataProvider()
    data_provider.truncate()
    source_crs = layer.sourceCrs()
    dest_crs = QgsCoordinateReferenceSystem("EPSG:3857")
    if not layer.isValid():
        raise Exception("Layer failed to load!")
    min_meters = 0.0000001225 # 0.35mm x 0.35mm on map
    limit = min_meters * (float(resolution_input.text()) ** 2)
    features = layer.getFeatures()
    # features_to_add = []
    for feature in features:
        geom = feature.geometry()
        tr = QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance())
        geom.transform(tr)
        area = geom.area()
        # print(limit)
        # print(area)
        if area >= limit:
            # features_to_add.append(feature)
            added = data_provider.addFeature(feature)
            # print(added)
            # print(feature)
    # new_layer.addFeatures(features_to_add)
    return True
