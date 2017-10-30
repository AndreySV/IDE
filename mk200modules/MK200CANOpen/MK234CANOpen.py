#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief вкладка GUI-я настройки CAN'а для MK234
@Author Vasilij
"""

import wx
import os
import CodeFileTreeNode
from editors.CodeFileEditor import CodeEditor
from PLCControler import LOCATION_CONFNODE, LOCATION_GROUP, LOCATION_VAR_MEMORY
from CANOpenIOEditors.CANOpenAI import CANOpenAinputEditor
from CANOpenIOEditors.CANOpenAO import CANOpenAoutputEditor
from MK200CANOpenBase import MK200CANOpenBase, MK200CANOpenFile

DIV_BEGIN = "/" + ("*"*82) + "\n\t\t\t"
DIV_END = "\n" + ("*"*82) + "/\n"
NODE_ID_DESCRIPTION = "Node ID"
AO_DESCRIPTION =  "On board AO"
AI_DESCRIPTION = "On board AI"

NUM_OF_AI = 8
NUM_OF_AO = 2
LOACTION_MODULE_NUM = '.1'

class MK234CANOpenEditor(CodeEditor):

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


class MK234CANOpenFileEditor(MK200CANOpenBase):

    CONFNODEEDITOR_TABS = [
        (_("C code"), "_create_CodePanel")]
    EditorType = MK234CANOpenEditor

    def _create_CodePanel(self, prnt):
        MK200CANOpenBase._create_CodePanel(self, prnt)
        self.DefaultNodID = []
        notebook = wx.Notebook(self.CodeEditorPanel)
        """AO tab"""
        self.aoEditor = CANOpenAoutputEditor(notebook, self.ParentWindow, self.Controler)
        notebook.AddPage(self.aoEditor, "AO Config")
        """AI tab"""
        self.aiEditor = CANOpenAinputEditor(notebook, self.ParentWindow, self.Controler, NUM_OF_AI)
        notebook.AddPage(self.aiEditor, "AI Config")

        self.mainSizer.Add(notebook, 1, wx.EXPAND)
        self.CodeEditorPanel.SetSizer(self.mainSizer)
        return self.CodeEditorPanel

    def RefreshView(self):
        MK200CANOpenBase.RefreshView(self)
        self.aoEditor.RefreshView()
        self.aiEditor.RefreshView()


class MK234CANOpenFile (MK200CANOpenFile):

    CODEFILE_NAME = "CANOpenConfig"
    SECTIONS_NAMES = [ "includes", "globals", "initFunction", "cleanUpFunction", "retrieveFunction", "publishFunction"]

    EditorType = MK234CANOpenFileEditor

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

    def GetDiagnosticVariableLocationTree(self, location):
        variableTree = {"name": "Diagnostic", "type": LOCATION_GROUP, "location": "0", "children": []}
        variableTree["children"].append({
                'children':[],
                'var_name': 'Connected',
                'IEC_type': u'BOOL',
                'name': 'Connected',
                'description': '',
                'type': LOCATION_VAR_MEMORY,
                'location': '%QX'+location+'.{}'.format(0),
                'size':  'X'})
        variableTree["children"].append({
                'children':[],
                'var_name': 'Error',
                'IEC_type': u'DINT',
                'name': 'Error',
                'description': '',
                'type': LOCATION_VAR_MEMORY,
                'location': '%QD'+location+'.{}'.format(1),
                'size':  'D'})
        return variableTree

    def GetVariableLocationTree(self):
        current_location = self.GetCurrentLocation()
        iecChannel = ".".join(map(str, current_location))
        # print "GetFullIEC_Channel", iecChannel
        analogInputsFloat = self.GetIoVariableLocationTree("Analog inputs (Float)", u'REAL', '%QD'+iecChannel+'.0', 'D', NUM_OF_AI)
        analogInputsU16 = self.GetIoVariableLocationTree("Analog inputs (U16)", u'DINT', '%QD'+iecChannel+'.1', 'D', NUM_OF_AI)
        analogOutputsFloat = self.GetIoVariableLocationTree("Analog outputs", u'REAL', '%QD'+iecChannel+'.2', 'D', NUM_OF_AO)
        diagnostic = self.GetDiagnosticVariableLocationTree(iecChannel+'.3')
        children = [analogInputsFloat, analogInputsU16, analogOutputsFloat, diagnostic]
        return {"name": self.BaseParams.getName(),
                "type": LOCATION_CONFNODE,
                "location": self.GetFullIEC_Channel(),
                "children": children}

    def GetConfNodeGlobalInstances(self):
        return []

    def GenerateDefaultVariables(self):
        defaultConfig = []
        cobeID = self.GetFullIEC_Channel()
        cobeID = cobeID[:-2].replace('.', '_')
        for i in range (0, NUM_OF_AI):
            defaultConfig.append({
                "Name" : "MK200_AI_{0}_{1}".format(cobeID, i),
                "Address" : "",
                "Len" : "",
                "Type" : u"REAL",
                "Initial": "",
                "Description": "On board AI",
                "OnChange":"",
                "Options":"4-20"})
        for i in range(0, NUM_OF_AO):
            defaultConfig.append({
                "Name" : "MK200_AO_{0}_{1}".format(cobeID, i),
                "Address" : "",
                "Len" : "",
                "Type" : u"REAL",
                "Initial": "",
                "Description": "On board AO",
                "OnChange":"",
                "Options":"4-20mA"})
        defaultConfig.append({
            "Name" : "Node_ID_{}".format(cobeID),
            "Address" : "127",
            "Len" : "",
            "Type" : u"INT",
            "Initial": "",
            "Description": "Node ID",
            "OnChange":"",
            "Value":"",
            "Options":""})
        return defaultConfig

    def GetVariables(self):
        datas = []
        codeFileVariables = self.CodeFileVariables(self.CodeFile)
        if len(codeFileVariables) == 0:
            datas = self.GenerateDefaultVariables()
            return datas
        for var in codeFileVariables:
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
        return "Cfile"

    def _CloseView(self, view):
        app_frame = self.GetCTRoot().AppFrame
        if app_frame is not None:
            app_frame.DeletePage(view)

    def CodeFileName(self):
        return os.path.join(self.CTNPath(), "MK234CANOpen.xml")

    def GenerateLocationVariables(self, location_str):
        """
        Generates Locations vairables that binds user app variables and runtime
        :param location_str: location of whole module in project three (e.g. 1,2,3...)
        :return: C-code of declaring binding variables
        """
        text = ""
        for i in range(NUM_OF_AI):
            text += "void *__QD{0}_0_{1} = &mk234_{2}.ai[{3}].fValue;\n".format(location_str,
                                                                                  i, location_str, i)
            text += "void *__QD{0}_1_{1} = &mk234_{2}.ai[{3}].u16Value;\n".format(location_str,
                                                                              i, location_str, i)
        for i in range(NUM_OF_AO):
            # text += "void *__QD{0}_2_{1} = &mk234_{2}.ao[{3}].fValue;\n".format(location_str,
            #                                                                       i, location_str, i)
            text += "void *__QD{0}_2_{1} = &mk234_{2}.ao[{3}].fValue;\n".format(location_str,
                                                                              i, location_str, i)
        text += "static u8 connectionStatus=0;\n"
        text += "void * __QX{}_3_0 = &connectionStatus;\n".format(location_str)
        text += "void * __QD{0}_3_1 = &mk234_{1}.connectionsStatus;\n".format(location_str, location_str)
        return text

    def GenerateInit(self, location_str):
        text = ""
        text += "extern \"C\" int __init_%s(int argc,char **argv)\n"%location_str
        text += "{\n"
        ao_config = [i for i in self.GetVariables() if i["Description"] == AO_DESCRIPTION]
        for config in ao_config:
            channel = config["Name"][-1]
            if config["Options"] == "Off":
                text += "    mk234_{0}.ao[{1}].enabled = 0;\n".format(location_str, channel)
            else:
                text += "    mk234_{0}.ao[{1}].enabled = 1;\n".format(location_str, channel)

        ai_config = [i for i in self.GetVariables() if i["Description"] == AI_DESCRIPTION]
        for config in ai_config:
            channel = config["Name"][-1]
            if config["Options"] == "Off":
                text += "    mk234_{0}.ai[{1}].enabled = 0;\n".format(location_str, channel)
            else:
                text += "    mk234_{0}.ai[{1}].enabled = 1;\n".format(location_str, channel)
        text += "    mk200CANOpenMaster.addNode(&mk234_{0});\n".format(location_str)
        text += "    return 0;\n"
        text += "}\n"
        return text

    def GenerateRetrive(self, location_str):
        """
        Generate __retrieve_%s function
        :param location_str: location of whole module in project three (e.g. 1,2,3...)
        :return: C-Function code
        """
        text = ""
        text += "extern \"C\" void __retrieve_%s(void)\n{\n"%location_str
        text += "    if (mk234_%s.connectionsStatus == ConnectedAndInited)\n"%location_str
        text += "    {\n"
        text += "        connectionStatus = 1;\n"
        text += "    }\n"
        text += "    else\n"
        text += "    {\n"
        text += "        connectionStatus = 0;\n"
        text += "    }\n"
        text += "\n}\n\n"
        return text

    def CTNGenerate_C(self, buildpath, locations):

        current_location = self.GetCurrentLocation()
        location_str = "_".join(map(str, current_location))
        # print 'location_str ', location_str
        text = ""
        text += "#include \"MK200CANOpenMasterProcess.h\"\r\n"

        node_id = [i["Address"] for i in self.GetVariables() if i["Description"] == NODE_ID_DESCRIPTION]
        # print node_id
        if len(node_id) > 0:
            node_id = node_id[0]
        else:
            node_id = 1

        text += "CANOpenMK234 mk234_{0}({1});\r\n".format(location_str, node_id)

        text += self.GenerateLocationVariables(location_str)

        text += DIV_BEGIN + "Publish and retrive" + DIV_END
        text += self.GenerateInit(location_str)

        text += "extern \"C\" void __cleanup_%s(void)\n{\n"%location_str
        text += "\n}\n\n"

        text += self.GenerateRetrive(location_str)

        text += "extern \"C\" void __publish_%s(void)\n{\n"%location_str
        text += "\n"
        text += "\n}\n\n"

        Gen_Cfile_path = os.path.join(buildpath, "MK234CANOpen_%s.cpp"%location_str)
        cfile = open(Gen_Cfile_path,'w')
        cfile.write(text)
        cfile.close()
        matiec_flags = '"-I%s"'%os.path.abspath(self.GetCTRoot().GetIECLibPath())
        return [(Gen_Cfile_path, str(matiec_flags))],str(""), True

