# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TareaMaster
                                 A QGIS plugin
 Programa que realiza diferentes operaciones con SHP
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-04-22
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Nicolas Molano
        email                : nicolas.molano@usal.es
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from PyQt5.QtWidgets import QAction, QFileDialog
from qgis.core import QgsProject
from PyQt5.QtWidgets import QTableWidgetItem, QApplication, QMainWindow, QTableWidget, QWidget, QFileDialog
from qgis.core import QgsGeometry
from qgis.core import QgsPointXY
from qgis.core import QgsFeature
from qgis.core import QgsVectorLayer
from PyQt5 import QtWidgets
from qgis.PyQt.QtGui import *


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .TareaMaster_dialog import TareaMasterDialog
import os.path
import sys, csv

class TareaMaster:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'TareaMaster_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Tarea Programacion')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('TareaMaster', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/TareaMaster/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Tarea Master'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Tarea Programacion'),
                action)
            self.iface.removeToolBarIcon(action)

    def select_output_file(self):
        # Funcion que despliega la ventana para seleccionar la carpeta y nombre de archivo a generar
        filename, _filter = QFileDialog.getSaveFileName(
            self.dlg, "Select   output file ", "", '*.csv')
        self.dlg.lineEdit_2.setText(filename)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = TareaMasterDialog()
            self.dlg.lineLengthButton.clicked.connect(self.generarLinderos)
            self.dlg.pushButton.clicked.connect(self.select_output_file)
            self.dlg.pushButton_2.clicked.connect(self.exportar)

        # Fetch the currently loaded layers
        layers = QgsProject.instance().layerTreeRoot().children()
        # Clear the contents of the comboBox from previous runs

        self.dlg.comboBox_2.clear()
        self.dlg.comboBox_3.clear()
        self.dlg.lineEdit.clear()

        # Populate the comboBox with names of all the loaded layers

        self.dlg.comboBox_2.addItems([layer.name() for layer in layers])
        self.dlg.comboBox_3.addItems([layer.name() for layer in layers])


        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass



    def exportar(self):
        # Funcion que toma los datos de tabla_Linderos, y los organiza para la exportacion al fichero
        # definido en la funcion select_output_file
        layers = QgsProject.instance().layerTreeRoot().children()
        path = self.dlg.lineEdit_2.text()
        with open(path, 'w') as output_file:
                writer = csv.writer(output_file)
                for row in range(self.dlg.tabla_Linderos.rowCount()):
                    rowdata = []
                    for column in range (self.dlg.tabla_Linderos.columnCount()):
                        item = self.dlg.tabla_Linderos.item(row,column)
                        if item is not None:
                            rowdata.append(item.text())
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)
                rowdata = []
                # Asi mismo, se exporta el dato almacenado en los lineEdit correspondientes al perimetro y area del predio
                rowdata.append("El area del predio es: " + self.dlg.lineEdit_3.text())
                writer.writerow(rowdata)
                rowdata = []
                rowdata.append("El perimetro del predio es: " + self.dlg.lineEdit.text())
                writer.writerow(rowdata)



    def generarLinderos(self):
        #
        contador = []
        longitud = []
        coordx1 = []
        coordy1 = []
        coordx2 = []
        coordy2 = []
        featu = QgsFeature()
        point_layer = QgsVectorLayer("Point?crs=epsg:3115", "point_layer", "memory")
        pr = point_layer.dataProvider()

        layers2 = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = self.dlg.comboBox_2.currentIndex()

        layers3 = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex2 = self.dlg.comboBox_3.currentIndex()
        layer = layers2[selectedLayerIndex].layer()
        layer2 = layers3[selectedLayerIndex2].layer()
        self.dlg.tabla_Datos.clearContents()
        self.dlg.tabla_Datos.setRowCount(0)

        header = self.dlg.tabla_Datos.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)

        self.dlg.tabla_Linderos.clearContents()
        self.dlg.tabla_Linderos.setRowCount(0)
        header2 = self.dlg.tabla_Linderos.horizontalHeader()
        header2.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

        
        if layer.geometryType() == 1:
            total_length = 0

            for feat in layer.getFeatures():
                totalentidad = layer.featureCount()
                geometry = feat.geometry()
                total_length += geometry.length()
                contador = (feat.id() + 1)
                contador2 = contador+1
                longitud = str('{:03.2f}'.format(geometry.length()))

                self.dlg.tabla_Datos.insertRow(self.dlg.tabla_Datos.rowCount())
                self.dlg.tabla_Linderos.insertRow(self.dlg.tabla_Linderos.rowCount())


                geom = feat.geometry().asMultiPolyline()

                for line in geom:
                    start_point = QgsPointXY(geom[0][0])
                    end_point = QgsPointXY(geom[-1][-1])
                    coordx1 = str('{:03.2f}'.format(start_point.x()))
                    coordy1 = str('{:03.2f}'.format(start_point.y()))
                    coordx2 = str('{:03.2f}'.format(end_point.x()))
                    coordy2 = str('{:03.2f}'.format(end_point.y()))
                    featu.setGeometry(QgsGeometry.fromPointXY(start_point))
                    pr.addFeatures([featu])
                    featu.setGeometry(QgsGeometry.fromPointXY(end_point))
                    pr.addFeatures([featu])

                self.dlg.tabla_Datos.setItem(self.dlg.tabla_Datos.rowCount() - 1, 0, QTableWidgetItem(str(contador)))
                self.dlg.tabla_Datos.setItem(self.dlg.tabla_Datos.rowCount() - 1, 1, QTableWidgetItem(longitud))
                self.dlg.tabla_Datos.setItem(self.dlg.tabla_Datos.rowCount() - 1, 2, QTableWidgetItem(coordx1))
                self.dlg.tabla_Datos.setItem(self.dlg.tabla_Datos.rowCount() - 1, 3, QTableWidgetItem(coordy1))
                self.dlg.tabla_Datos.setItem(self.dlg.tabla_Datos.rowCount() - 1, 4, QTableWidgetItem(coordx2))
                self.dlg.tabla_Datos.setItem(self.dlg.tabla_Datos.rowCount() - 1, 5, QTableWidgetItem(coordy2))

                if contador == totalentidad:
                    self.dlg.tabla_Linderos.setItem(self.dlg.tabla_Linderos.rowCount() - 1, 0, QTableWidgetItem("Del punto " + str(contador) + " de coordenadas E:" + coordx1 +"m N: " + coordy1 + "m hasta encontrar el punto 1 de coordenadas E: " + coordx2 + "m N: " + coordy2 + " en una distancia de " + str(longitud) + "m"))
                else:
                    self.dlg.tabla_Linderos.setItem(self.dlg.tabla_Linderos.rowCount() - 1, 0, QTableWidgetItem(
                        "Del punto " + str(
                            contador) + " de coordenadas E:" + coordx1 + "m N: " + coordy1 + "m hasta encontrar el punto " + str(
                            contador2) + " de coordenadas E: " + coordx2 + "m N: " + coordy2 + " en una distancia de " + str(
                            longitud) + "m"))


            self.dlg.lineEdit.setText(str('{:03.2f}'.format(total_length)) + " m")


            QgsProject.instance().addMapLayer(point_layer)
        else:
            self.dlg.lineEdit.setText("La capa no es valida")

        if layer2.geometryType() == 2:
            for feature in layer2.getFeatures():
                geom = feature.geometry()
                area = geom.area()
            self.dlg.lineEdit_3.setText(str(int(area))+" m2")
        else:
            self.dlg.lineEdit_3.setText("La capa no es valida")


