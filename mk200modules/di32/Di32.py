
import os

from CodeFileTreeNode import CodeFile
from PLCControler import LOCATION_VAR_INPUT
from ConfigTreeNode import LOCATION_CONFNODE

class Di32ModuleFile(CodeFile):

    CODEFILE_NAME = "CFile"
    SECTIONS_NAMES = [
        "includes",
        "globals",
        "initFunction",
        "cleanUpFunction",
        "retrieveFunction",
        "publishFunction"]

    #EditorType = DoFileEditor

    def GetVariables(self):
        datas = []
        for var in self.CFile.variables.getvariable():
            datas.append({"Name" : "__IW0_1_1", "Type" : LOCATION_VAR_INPUT, "Class" : var.getclass()})
        return datas

    def GetVariableLocationTree(self):
        """
        This function is meant to be overridden by confnodes.

        It should returns an list of dictionaries

        - IEC_type is an IEC type like BOOL/BYTE/SINT/...
        - location is a string of this variable's location, like "%IX0.0.0"
        """
        children = [{'children':[], 'var_name': u'input', 'IEC_type': u'INT', 'name': u'input', 'description': '', 'type': 3, 'location': '%QW' + self.GetFullIEC_Channel()[:1] + '.0', 'size': 'W'}]
        return {"name": self.BaseParams.getName(),
                "type": LOCATION_CONFNODE,
                "location": self.GetFullIEC_Channel(),
                "children": children}

    def GetConfNodeGlobalInstances(self):
        return []

    def GetIconName(self):
        return "CFile"

    def CodeFileName(self):
        return os.path.join(self.CTNPath(), "cfile.xml")

    def CTNGenerate_C(self, buildpath, locations):
        """
        Generate C code
        @param current_location: Tupple containing confnode IEC location : %I0.0.4.5 => (0,0,4,5)
        @param locations: List of complete variables locations \
            [{"IEC_TYPE" : the IEC type (i.e. "INT", "STRING", ...)
            "NAME" : name of the variable (generally "__IW0_1_2" style)
            "DIR" : direction "Q","I" or "M"
            "SIZE" : size "X", "B", "W", "D", "L"
            "LOC" : tuple of interger for IEC location (0,1,2,...)
            }, ...]
        @return: [(C_file_name, CFLAGS),...] , LDFLAGS_TO_APPEND
        """
        print locations

        current_location = self.GetCurrentLocation()
        print current_location
        # define a unique name for the generated C file
        location_str = "_".join(map(str, current_location))
        iecChannel = self.GetFullIEC_Channel()[:1];

        text = "/* Code generated by Beremiz c_ext confnode */\n\n"
        text += "#include <stdio.h>\n\n"

        text += '#include "iec_types_all.h"\n\n'
        text += '#include "CANOpenNodeType.h"\n\n'

        text += "static INT di32Value;\n"

        text += 'static void pdoHandler (unsigned char pdoNum, unsigned char *data)\n\n'
        text += "{\n"
        text += "   if (pdoNum == 0)\n"
        text += "   {\n"
        text += "       di32Value = (data[0])|(data[1]<<8)|(data[2]<<16)|(data[3]<<24);\n"
        text += "   }\n"
        text += "}\n"

        text += 'static CANOpenNodeType mkLogic500_DI32 ={' + iecChannel + ', pdoHandler };\n'

        text += "INT *" + "__QW" + iecChannel + "_0 = &di32Value;\n"
        text += "unsigned char di32ModuleNodeId;\n"

        # Adding user global variables and routines
        text += "/* User internal user variables and routines */\n"
        text += self.CodeFile.globals.getanyText().strip()
        text += "\n"

        # Adding Beremiz confnode functions
        text += "/* Beremiz confnode functions */\n"
        text += "int __init_%s(int argc,char **argv)\n{\n"%location_str
        text += "   di32ModuleNodeId =" + iecChannel + ";\n"
        text += "   addCANOpenNode(&mkLogic500_DI32);\n"
        text += "  return 0;\n}\n\n"

        text += "void __cleanup_%s(void)\n{\n"%location_str
        text += self.CodeFile.cleanUpFunction.getanyText().strip()
        text += "\n}\n\n"

        text += "void __retrieve_%s(void)\n{\n"%location_str
        text += "   ;\n"
        text += "\n}\n\n"

        text += "void __publish_%s(void)\n{\n"%location_str
        text += "\n"
        text += "\n}\n\n"

        Gen_Cfile_path = os.path.join(buildpath, "CFile_%s.c"%location_str)
        cfile = open(Gen_Cfile_path,'w')
        cfile.write(text)
        cfile.close()

        matiec_flags = '"-I%s"'%os.path.abspath(self.GetCTRoot().GetIECLibPath())

        return [(Gen_Cfile_path, str(matiec_flags))],str(""),True
