# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from PyQt5.QtCore import *
from math import sqrt, atan, degrees, acos, atan2
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterNumber,
                       QgsField,
                       QgsMessageLog,
                       QgsPointXY,
                       QgsPoint,
                       QgsFeature,
                       QgsGeometry
                       )

class SimplifyLines(QgsProcessingAlgorithm):

    INPUT1 = 'INPUT1'
    INPUT2 = 'INPUT2'
    OUTPUT = 'OUTPUT'
    
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return SimplifyLines()

    def name(self):
        return 'SimplifyLines'

    def displayName(self):
        return self.tr('SimplifyLines')

    def group(self):
        return self.tr('MapGeneralization')

    def groupId(self):
        return 'MapGeneralization'

    def shortHelpString(self):
        return self.tr("This tool is for simplifying line features using modificated Jenks algorithm. Minimum value is minimum distance [m] of vertex deviaton. \nVersion: 0.1, Date: 5.1.2019 \nAuthor: Tomas Bernat")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT1,
                self.tr('Input line'),
                types=[QgsProcessing.TypeVector]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                name=self.INPUT2,
                description=self.tr('Minimum value [m]'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=100,
                optional=False,
                minValue=0,
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output line')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """Here is where the processing itself takes place."""
        
        def get_line_coords(f):
            """Get line coordinates as array of vertexes"""
            geom = f.geometry()
            wkt = geom.asWkt()
            string = " " + wkt.split("((")[1].split("))")[0]
            array = string.split(",")
            coords = []
            for v in array:
                vertex = []
                vertex.append(float(v.split(' ')[1]))
                vertex.append(float(v.split(' ')[2]))
                coords.append(vertex)
            return(coords)

        def distance(A,P,B):
            """Calculate distance between point P and line defined by points A and B"""
            d = abs((B[1]-A[1])*P[0]-(B[0]-A[0])*P[1]+B[0]*A[1]-B[1]*A[0])/sqrt((B[1]-A[1])**2+(B[0]-A[0])**2)
            return(d)

        def generalize(line,min):
            """Removing vertexes from line using jenks modification algorithm"""
            before = line[0]
            for i in range(1,len(line)-1):
                if distance(before,line[i],line[i+1]) < min:
                    line[i] = 'del'
                else:
                    before = line[i]
            while line.count('del') > 0:
                line.remove('del')
        
        def make_line_feature(line):
            """Make line feature from coordinates array""" 
            coords = []
            for i in range(len(line)):
                coords.append(QgsPoint(line[i][0],line[i][1]))
            feature = QgsFeature()
            feature.setGeometry(QgsGeometry.fromPolyline(coords))
            return(feature)
        
        inline = self.parameterAsVectorLayer(parameters, self.INPUT1, context)
        min = self.parameterAsDouble(parameters, self.INPUT2, context)
        (outline, dest_id) = self.parameterAsSink(parameters,self.OUTPUT,context,inline.fields(),inline.wkbType(),inline.sourceCrs())

        for f in inline.getFeatures():
            line = get_line_coords(f)
            generalize(line,min)
            feature = make_line_feature(line)
            feature.setAttributes(f.attributes())
            outline.addFeature(feature, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: dest_id}
