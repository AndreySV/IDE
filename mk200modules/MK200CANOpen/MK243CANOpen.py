#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief вкладка GUI-я настройки CAN'а для MK243
@Author Vasilij
"""

import wx
import os
import wx.lib.agw.customtreectrl as CT
import CodeFileTreeNode
from editors.CodeFileEditor import CodeEditor
from editors.CodeFileEditor import CodeFileEditor
from editors.ConfTreeNodeEditor import ConfTreeNodeEditor
from ConfigTreeNode import ConfigTreeNode
from PLCControler import LOCATION_CONFNODE, LOCATION_GROUP, LOCATION_VAR_MEMORY
from MK201CANOpen_XSD import CODEFILE_XSD
from CANOpenIOEditors.CANOpenDI import CANOpenDiEditor
from CANOpenIOEditors.CANOpenDO import CANOpenDoEditor
from MK200CANOpenBase import MK200CANOpenBase

CodeFileTreeNode.CODEFILE_XSD = CODEFILE_XSD
CodeFile = CodeFileTreeNode.CodeFile

DIV_BEGIN = "/" + ("*"*82) + "\n\t\t\t"
DIV_END = "\n" + ("*"*82) + "/\n"

NUM_OF_DI = 16
NUM_OF_DO = 24

LOACTION_MODULE_NUM = '.2'

class MK243CANOpenEditor(CodeEditor):

    def __init__(self, parent, window, controler):
        pass

    def SetCodeLexer(self):
        pass

    def RefreshBuffer(self):
        pass

    def ResetBuffer(self):
        pass

    def GetCodeText(self):
        pass

    def RefreshView(self, scroll_to_highlight=False):
        pass


class MK243CANOpenFileEditor(MK200CANOpenBase):

    CONFNODEEDITOR_TABS = [
        (_("C code"), "_create_CodePanel")]
    CODE_EDITOR = MK243CANOpenEditor

    def __init__(self, parent, controler, window):
        ConfTreeNodeEditor.__init__(self, parent, controler, window)

    def _create_CodePanel(self, prnt):
        MK200CANOpenBase._create_CodePanel(self, prnt)
        self.DefaultNodID = []
        notebook = wx.Notebook(self.CodeEditorPanel)
        """DO tab"""
        self.doEditor = CANOpenDoEditor(notebook, self.ParentWindow, self.Controler)
        notebook.AddPage(self.doEditor, "DO Config")
        """DI tab"""
        self.diEditor = CANOpenDiEditor(notebook, self.ParentWindow, self.Controler, NUM_OF_DI)
        notebook.AddPage(self.diEditor, "DI Config")

        self.mainSizer.Add(notebook, 1, wx.EXPAND)
        self.CodeEditorPanel.SetSizer(self.mainSizer)
        return self.CodeEditorPanel

    def RefreshView(self):
        MK200CANOpenBase.RefreshView(self)
        self.diEditor.RefreshView()
        self.doEditor.RefreshView()


class MK243CANOpenFile (CodeFile):

    CODEFILE_NAME = "CANOpenConfig"
    SECTIONS_NAMES = [ "includes", "globals", "initFunction", "cleanUpFunction", "retrieveFunction", "publishFunction"]

    EditorType = MK243CANOpenFileEditor

    def GetIoVariableLocationTree(self, name, type, location, size, numOfChannles):
        variableTree = {"name": name, "type": LOCATION_GROUP, "location": "0", "children": []}
        for i in range(0, numOfChannles):
            variableTree["children"].append({
                'children':[],
                'var_name': 'Channel #{}'.format(i),
                'IEC_type': type,
                'name': 'Channel #{}'.format(i),
                'description': '',
                'type': LOCATION_VAR_MEMORY,
                'location': location+'.{}'.format(i),
                'size':  size})
        return variableTree

    def GetVariableLocationTree(self):
        iecChannel = self.GetFullIEC_Channel()[:1]
        digitalInputs = self.GetIoVariableLocationTree("Digital inputs", u'BOOL', '%QD'+iecChannel+LOACTION_MODULE_NUM+'.0', 'D', NUM_OF_DI)
        digitalOutputs = self.GetIoVariableLocationTree("Digital outputs", u'BOOL', '%QX'+iecChannel+LOACTION_MODULE_NUM+'.1', 'X', NUM_OF_DO)
        children = [digitalInputs, digitalOutputs]
        return {"name": self.BaseParams.getName(),
                "type": LOCATION_CONFNODE,
                "location": self.GetFullIEC_Channel(),
                "children": children}

    def GetConfNodeGlobalInstances(self):
        return []

    def GetVariables(self):
        datas = []
        for var in self.CodeFileVariables(self.CodeFile):
            datas.append({"Name" : var.getname(),
                          "Type" : var.gettype(),
                          "Initial" : var.getinitial(),
                          "Description": var.getdesc(),
                          "OnChange": var.getonchange(),
                          "Options": var.getopts(),
                          "Address" : var.getaddress(),
                          "Len" : var.getlen(),
                          })
        return datas

    def SetVariables(self, variables):
        self.CodeFile.variables.setvariable([])
        for var in variables:
            variable = self.CodeFileParser.CreateElement("variable", "variables")
            variable.setname(var["Name"])
            variable.settype(var["Type"])
            variable.setinitial(var["Initial"])
            variable.setdesc(var["Description"])
            variable.setonchange(var["OnChange"])
            variable.setopts(var["Options"])
            variable.setaddress(var["Address"])
            variable.setlen(var["Len"])
            self.CodeFile.variables.appendvariable(variable)

    def GetIconName(self):
        return "CFile"

    def _CloseView(self, view):
        app_frame = self.GetCTRoot().AppFrame
        if app_frame is not None:
            app_frame.DeletePage(view)

    def CodeFileName(self):
        return os.path.join(self.CTNPath(), "MK243CANOpen.xml")

    def CTNGenerate_C(self, buildpath, locations):

        current_location = self.GetCurrentLocation()
        location_str = "_".join(map(str, current_location))
        text = ""

        text += DIV_BEGIN + "Publish and retrive" + DIV_END
        text += "extern \"C\" int __init_%s(int argc,char **argv)\n{\n"%location_str
        text += "  return 0;\n}\n\n"

        text += "extern \"C\" void __cleanup_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += "extern \"C\" void __retrieve_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += "extern \"C\" void __publish_%s(void)\n{\n"%location_str
        text += "\n"
        text += "\n}\n\n"

        Gen_Cfile_path = os.path.join(buildpath, "MK243CANOpen_%s.cpp"%location_str)
        cfile = open(Gen_Cfile_path,'w')
        cfile.write(text)
        cfile.close()
        matiec_flags = '"-I%s"'%os.path.abspath(self.GetCTRoot().GetIECLibPath())
        return [(Gen_Cfile_path, str(matiec_flags))],str(""), True

