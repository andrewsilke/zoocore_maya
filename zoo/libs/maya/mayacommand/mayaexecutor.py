# @note if the executed command is not maya based its still going to be part of maya internal undo stack
# which could be bad but maybe not :D
import traceback

import sys
from maya import cmds
from maya.api import OpenMaya as om2
from zoo.libs.command import base
from zoo.libs.command import errors


class MayaExecutor(base.ExecutorBase):
    def __init__(self):
        super(MayaExecutor, self).__init__()
        om2._COMMANDEXECUTOR = self

    def execute(self, commandName=None, *args, **kwargs):
        command = self.findCommand(commandName)
        if command is None:
            raise ValueError("No command by the name -> {} exists within the registry!".format(commandName))
        if om2._COMMANDEXECUTOR is None:
            om2._COMMANDEXECUTOR = self
        command = command()
        command._prepareCommand()
        if not command.isEnabled:
            return
        try:
            command._resolveArguments(kwargs)
        except errors.UserCancel:
            raise
        except Exception:
            raise
        exc_tb = None
        exc_type = None
        exc_value = None
        command.stats = base.CommandStats(command)
        try:
            if command.isUndoable:
                cmds.undoInfo(openChunk=True)
            om2._ZOOCOMMAND = command
            cmds.zooAPIUndo(id=command.id)
        except errors.UserCancel:
            command.stats.finish(None)
        except Exception:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            raise
        finally:
            tb = None
            if exc_type and exc_value and exc_tb:
                tb = traceback.format_exception(exc_type, exc_value, exc_tb)
            if command.isUndoable and not tb:
                self.undoStack.append(command)
                cmds.undoInfo(closeChunk=True)
            command.stats.finish(tb)
            return command._returnResult

    def undoLast(self):
        if not self.undoStack:
            return False
        command = self.undoStack[-1]
        if command is None or not command.isUndoable:
            return False
        exc_tb = None
        exc_type = None
        exc_value = None
        # todo need to check against mayas undo?
        try:
            command.stats = base.CommandStats(command)
            cmds.undo()
        except errors.UserCancel:
            command.stats.finish(None)
            return
        except Exception:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            raise
        finally:
            tb = None
            if exc_type and exc_value and exc_tb:
                tb = traceback.format_exception(exc_type, exc_value, exc_tb)
            elif command.isUndoable:
                self.undoStack.remove(command)
            self.redoStack.append(command)
            command.stats.finish(tb)
        return True

    def redoLast(self):
        if not self.redoStack:
            return
        result = None
        command = self.redoStack[-1]
        if command is None:
            return result

        exc_tb = None
        exc_type = None
        exc_value = None
        try:
            command.stats = base.CommandStats(command)
            cmds.redo()
        except errors.UserCancel:
            command.stats.finish(None)
            return
        except Exception:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_tb)
            raise
        finally:
            tb = None
            command = self.redoStack.pop()
            if exc_type and exc_value and exc_tb:
                tb = traceback.format_exception(exc_type, exc_value, exc_tb)
            elif command.isUndoable:
                self.undoStack.append(command)
            command.stats.finish(tb)

        return result

    def flush(self):
        super(MayaExecutor, self).flush()
        cmds.flushUndo()

    def _callDoIt(self, command):
        if om2.MGlobal.isRedoing():
            self.redoStack.pop()
            result = super(MayaExecutor, self)._callDoIt(command)
            self.undoStack.append(command)
            return result
        return super(MayaExecutor, self)._callDoIt(command)
