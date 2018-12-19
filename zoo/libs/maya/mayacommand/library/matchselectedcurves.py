from zoo.libs.command import command
from zoo.libs.maya.api import scene, curves
from maya.api import OpenMaya as om2


class MatchSelectedCurves(command.ZooCommand):
    """This command Creates a meta node from the registry.
    """
    id = "zoo.maya.curves.match"
    creator = "David Sparrow"
    isUndoable = True
    uiData = {"icon": "",
              "tooltip": "Matches the selected curves, the first selected node is the driver",
              "label": "Match selected curves",
              "color": "",
              "backgroundColor": ""
              }

    def resolveArguments(self, arguments):
        selected = scene.getSelectedNodes()
        if len(selected) < 2:
            self.cancel("Please Select at least 2 nodes")
        driver = om2.MObjectHandle(selected[0])  # driver
        driven = map(om2.MObjectHandle, selected[1:])  # driven
        arguments["driver"] = driver
        arguments["driven"] = driven
        return arguments

    def doIt(self, driver=None, driven=None):
        """Create the meta node based on the type parameter, if the type isn't specified then the baseMeta class will
        be used instead

        """
        curves.matchCurves(driver.object(), [n.object() for n in driven])
        return True

    def undoIt(self):
        #todo: yeah need to deal with undo
        pass