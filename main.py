import logging

import maya.cmds as cmds

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from PySide2.QtCore import QFile, QObject
from PySide2 import QtGui, QtWidgets, QtCore


logger = logging.getLogger("outliner")
logger.setLevel(logging.WARNING)

# create console handler with debug log level
c_handler = logging.StreamHandler()

#create file handler with debug log level
log_path = "/Users/sanazsanayei/Library/Preferences/Autodesk/maya/2022/scripts/MayaOutliner/log.log"
f_handler = logging.FileHandler(filename=log_path)

# create formatter and add it to handlers
formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
c_handler.setFormatter(formatter)
# f_handler.setFormatter(formatter)

# add handlers to logger
logger.addHandler(c_handler)
# logger.addHandler(f_handler)


class SceneOutliner(QObject):

        def __init__(self, ui_file, parent=None):
            super(SceneOutliner, self).__init__(parent)
            ui_file = QFile(ui_file)
            ui_file.open(QFile.ReadOnly)

            loader = QUiLoader()
            self.window = loader.load(ui_file)
            ui_file.close()

            self.window.setWindowTitle("Maya Outliner")
            # set icons and store them in variables
            self.transform_icon = QtGui.QIcon(":transform.svg")
            self.camera_icon = QtGui.QIcon(":Camera.png")
            self.mesh_icon = QtGui.QIcon(":mesh.svg")

            # allow multiple selection
            self.window.treeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

            #connections
            self.window.refresh_btn.clicked.connect(self.refresh_tree_widget())

            self.window.treeWidget.itemCollapsed.connect(self.update_icon)
            self.window.treeWidget.itemExpanded.connect(self.update_icon)

            self.window.treeWidget.itemSelectionChanged.connect(self.selected_items)

        # add all the top level objects in the scene to the tree widget
        def refresh_tree_widget(self):
            # make sure the tree widget is empty
            self.window.treeWidget.clear()
            # show all the top level dag objects
            top_level_object_name = cmds.ls(assemblies=True)
            # iterate over top level items and add them to the tree
            for name in top_level_object_name:
                item = self.create_item(name)
                self.window.treeWidget.insertTopLevelItem(0, item)

        # take the name of the object and create a tree_widget_item instance and return it
        def create_item(self, name):
            item = QtWidgets.QTreeWidgetItem([name])
            self.add_children(item)
            self.update_icon(item)

            return item

        # take object and if any children exist add them to item
        def add_children(self, item):
            # pass name of the object which store in item.text index 0
            children = cmds.listRelatives(item.text(0), children=True)
            if children:
                for child in children:
                    child_item = self.create_item(child)
                    item.addChild(child_item)

        # selecting corresponding object in the scene
        def selected_items(self):
            # holds all items that are selected
            items = self.window.treeWidget.selectedItems()
            names = []
            for item in items:
                names.append(item.text(0))
            cmds.select(names, replace=True)

        # check object_type and add proper icon
        def update_icon(self, item):
            object_type = ""
            if item.isExpanded():
                object_type = "transform"
            else:
                child_count = item.childCount()
                if child_count == 0:
                    object_type = cmds.objectType(item.text(0))
                elif child_count == 1:
                    child_item = item.child(0)
                    object_type = cmds.objectType(child_item.text(0))
                else:
                    object_type = "transform"
            if object_type == "transform":
                item.setIcon(0, self.transform_icon)
            elif object_type == "camera" :
                item.setIcon(0, self.camera_icon)
            elif object_type == "mesh":
                item.setIcon(0, self.mesh_icon)








def launch():
    print("launch application")
    form = SceneOutliner('/Users/sanazsanayei/PycharmProjects/pythonProject/my_tool/outliner.ui')
    form.window.exec_()