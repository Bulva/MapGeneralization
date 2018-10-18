# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MapGeneralization
                                 A QGIS plugin
 Plugin for generalization
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-10-18
        copyright            : (C) 2018 by MUNI
        email                : petrsilhak@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MapGeneralization class from file MapGeneralization.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .map_generalization import MapGeneralization
    return MapGeneralization(iface)