#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@brief Вкладка AI для классов модулйей проткола CANOpen
@Author Yanikeev-AS
"""

__author__ = 'Yanikeev-as'

from mk200modules.MK200CANOpen.CANOpenIOEditors.CANOpenIOEditor import *


# CodeFileTreeNode.CODEFILE_XSD = CODEFILE_XSD
CodeFile = CodeFileTreeNode.CodeFile

DIV_BEGIN = "/" + ("*"*82) + "\n\t\t\t"
DIV_END = "\n" + ("*"*82) + "/\n"

AI_MODES = ("Off", "4-20mA", "0-20mA")
DESCRIPTION = "On board AI"

class CANOpenAiputChannelEditor(wx.Panel):

    def __init__(self, parent, channel):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.channelTxt = wx.StaticText(self, label="Input #{}".format(channel))
        newId = wx.NewId()
        self.modeCmbbx = wx.ComboBox(self, id=newId, value="SelectRange", choices=AI_MODES)
        self.modeCmbbx.SetStringSelection(AI_MODES[1])
        main_sizer.Add(self.channelTxt, flag=wx.ALIGN_CENTER_VERTICAL)
        main_sizer.Add(self.modeCmbbx, flag=wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(main_sizer)

class CANOpenAinputEditor(wx.Panel):
    def __init__(self, parent, window, controler, chanelNum):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)

        self.ParentWindow = window
        self.Controler = controler
        self.chanelNum = chanelNum

        self.AiDefaultConfig = []
        self.cobeID = self.Controler.GetFullIEC_Channel()
        self.cobeID = self.cobeID[:-2].replace('.', '_')
        for i in range (0, self.chanelNum):
            self.AiDefaultConfig.append({
                "Name" : "MK200_AI_{0}_{1}".format(self.cobeID, i),
                "Address" : "",
                "Len" : "",
                "Type" : u"REAL",
                "Initial": "",
                "Description": DESCRIPTION,
                "OnChange":"",
                "Options":"4-20"})

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.title = wx.StaticText(self, label="Analog input configuration")
        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        self.title.SetFont(font)
        main_sizer.Add(self.title, flag=wx.ALIGN_CENTER_VERTICAL)

        self.inputs = []
        for i in range(0, self.chanelNum):
            channel = CANOpenAiputChannelEditor(self, i)
            self.inputs.append(channel)
            main_sizer.Add(channel, flag=wx.ALIGN_CENTER_VERTICAL)
            wx.EVT_COMBOBOX(self, channel.modeCmbbx.GetId(), self.OnChange)
        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_SHOW, self.OnShow)
        self.firstCall = 1

    def OnChange(self, event):
        valuesOnFrame = self.GetData()
        valuesInController = [i for i in self.Controler.GetVariables()
                              if i["Description"] == DESCRIPTION]
        if valuesOnFrame != valuesInController:
            self.RefreshModel()
        event.Skip()

    def OnShow(self, event):
        if self.firstCall:
            self.RefreshView()
            self.firstCall = 0
        event.Skip()

    def GetData(self):
        """
        Считывает с GUI настроенные пользователем параметры и возвращает их в виде списка
        словарей
        """
        aiParams = self.AiDefaultConfig[:]
        for i in range (0, self.chanelNum):
            channelState = self.inputs[i].modeCmbbx.GetStringSelection()
            if channelState == "4-20mA":
                aiParams[i]["Options"] = channelState
            elif channelState == "0-20mA":
                aiParams[i]["Options"] = channelState
            else:
                aiParams[i]["Options"] = "Off"
        return aiParams

    def SetData(self, aiParams):
        """
        Выводит конфигурацию на GUI
        :param aiParams: спиоск с конфигурацией по каждому каналу
        :return: none
        """
        """ Если устанавливаемых параметров меньше чем надо, то уставливаются значения
         по умолчанию """
        if len(aiParams) < self.chanelNum:
            aiParams = self.AiDefaultConfig[:]
            self.RefreshModel()
        for aiInput, params in zip(self.inputs, aiParams):
            aiInput.modeCmbbx.SetStringSelection(params["Options"])

    def RefreshModel(self):
        controllerVariables = self.Controler.GetVariables()
        controllerVariables = [i for i in controllerVariables if i["Description"] != DESCRIPTION]
        controllerVariables += self.GetData()
        self.Controler.SetVariables(controllerVariables)
        self.RefreshBuffer()

    def RefreshBuffer(self):
        self.Controler.BufferCodeFile()
        self.ParentWindow.RefreshTitle()
        self.ParentWindow.RefreshFileMenu()
        self.ParentWindow.RefreshEditMenu()
        self.ParentWindow.RefreshPageTitles()

    def RefreshView(self):
        varForTable = self.Controler.GetVariables()
        varForTable = [i for i in varForTable if i["Description"] == DESCRIPTION]
        self.SetData(varForTable)
        self.Layout()

    def GetVariableTypeFunction(self, base_type):
        def VariableTypeFunction(event):
            self.RefreshModel()
            self.RefreshView()
            event.Skip()
        return VariableTypeFunction

