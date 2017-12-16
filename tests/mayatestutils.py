import logging

from tests import unittestBase
from maya import cmds
logger = logging.getLogger(__name__)


class BaseMayaTest(unittestBase.BaseUnitest):
    """Base class for all maya based unitests, provides helper methods for loading and loading plugins
    """
    loadedPlugins = set()
    application = "maya"

    @classmethod
    def loadPlugin(cls, pluginName):
        """Loads a given plugin and stores it on the class
        :param pluginName: str, the plugin to load
        """
        cmds.loadPlugin(pluginName)
        logger.debug("Loaded Plugin %s" % pluginName)
        cls.loadedPlugins.add(pluginName)

    @classmethod
    def unloadPlugins(cls):
        """Unload all the currently loaded plugins
        """
        for plugin in cls.loadedPlugins:
            cmds.unloadPlugin(plugin)
            logger.debug("unLoaded Plugin %s" % plugin)
        cls.loadedPlugins.clear()

    def tearDown(self):
        cmds.file(f=True, new=True)

    @classmethod
    def tearDownClass(cls):
        """Calls on cls.unloadPlugins()
        """
        super(BaseMayaTest, cls).tearDownClass()
        cls.unloadPlugins()
