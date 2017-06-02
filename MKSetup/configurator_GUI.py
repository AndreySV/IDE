# -*- coding: UTF-8 -*-
__author__ = 'Yanikeev-as'
import wx
import wx.lib.masked
import copy
import os.path
import sys
import time
from threading import Thread
from wx.lib.pubsub import pub
from wx.lib.masked.ipaddrctrl import IpAddrCtrl
from wx.lib.masked import TimeCtrl
import wx.lib.intctrl

# импорт моих модулей
from serialWork import SerialPort
from mk201_proto import mk201_proto

VERISON = '0.0.1'

# wx ID
GRID_BORDER = 5


ID_MAINWXFRAME = wx.NewId()
ID_MAINWXDIALOGFRAME = wx.NewId()

BTN_SIZE = (75, 23)

TEXT_WIDGET_SIZE = (30, 13)
PARITY_WIDGET_SIZE = (54, 21)
BAUD_WIDGET_SIZE = (66, 21)
DATA_WIDGET_SIZE = (40, 21)
MBCOMBOX_WIDGET_SIZE = (155, 21)
MBADDRESS_WIDGET_SIZE = (100, 21)

NETWORK_WIDGET_SIZE = (50, 13)
NETWORKADDRESS_WIDGET_SIZE = (120, 22)

DATETIME_WIDGET_SIZE = (32, 21)

class comLabels(wx.Panel):
    def __init__(self, parent, *args, **kwds):
        wx.Panel.__init__(self, parent, *args, **kwds)
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.portLbl = wx.StaticText(self, label = u"Порт", size = TEXT_WIDGET_SIZE)
        self.parityLbl = wx.StaticText(self, label = u"Четность", size = PARITY_WIDGET_SIZE)
        self.baudLbl = wx.StaticText(self, label = u"Скорость", size = BAUD_WIDGET_SIZE)
        self.databutsLbl = wx.StaticText(self, label = u"Data bytes", size = (40, 30))
        self.mbCombobox = wx.StaticText(self, label = u"Настройка modbus", size = MBCOMBOX_WIDGET_SIZE)
        self.mbAddress = wx.StaticText(self, label = u"Адрес modbus", size = MBADDRESS_WIDGET_SIZE)
        self.btn = wx.StaticText(self, label = u"", size = BTN_SIZE)

        mainSizer.Add(self.portLbl, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.parityLbl, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.baudLbl, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.databutsLbl, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.mbCombobox, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.mbAddress, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.btn, 0.5, wx.ALL, GRID_BORDER)

        self.SetSizer(mainSizer)
        self.Layout()


class initComWidget(wx.Panel):
    def __init__(self, parent, comNum, *args, **kwds):
        wx.Panel.__init__(self, parent, *args, **kwds)

        self.comNum = comNum
        parity_list = ["none", "even","odd"]
        baudrate_list = "300 600 900 1200 2400 4800 9600 14400 19200 38400 56000 57600 115200 128000 256000".split()
        modbusSetting_list = [u"Режим Modbus Master 0", u"Режим Modbus Master 1", u"Режим Modbus Master 2",
                              u"Режим Modbus slave", u"Выключен"]
        stopbytes_list = ["1", "1.5", "2"]

        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.portLabel = wx.StaticText(self, label = u"COM" + str(comNum), size = TEXT_WIDGET_SIZE)
        self.parityCombobox = wx.ComboBox(self, choices = parity_list, size = PARITY_WIDGET_SIZE)
        self.baudrateCombobox = wx.ComboBox(self, choices = baudrate_list, size = BAUD_WIDGET_SIZE)
        self.databytesCombobox = wx.ComboBox(self, choices = stopbytes_list, size = DATA_WIDGET_SIZE)
        self.modbusCombobox = wx.ComboBox(self, choices = modbusSetting_list, size = MBCOMBOX_WIDGET_SIZE)
        self.modbusAddress = wx.lib.intctrl.IntCtrl(self, min = 0, max = 255, limited = True, size = MBADDRESS_WIDGET_SIZE)
        self.writePortSettingBtn = wx.Button(self, wx.ID_ANY, u"Записать", name = 'writeBtnCOM1', size = BTN_SIZE)

        self.parityCombobox.SetSelection(1)
        self.baudrateCombobox.SetSelection(12)
        self.databytesCombobox.SetSelection(0)
        self.modbusCombobox.SetSelection(0)

        mainSizer.Add(self.portLabel, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.parityCombobox, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.baudrateCombobox, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.databytesCombobox, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.modbusCombobox, 1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.modbusAddress, 0.3, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.writePortSettingBtn, 0.5, wx.ALL, GRID_BORDER)

        self.SetSizer(mainSizer)
        self.Layout()

class networkLabels(wx.Panel):
    def __init__(self, parent, *args, **kwds):
        wx.Panel.__init__(self, parent, *args, **kwds)
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.addresType = wx.StaticText(self, label = u"Тип", size = NETWORK_WIDGET_SIZE)
        self.adderss = wx.StaticText(self, label = u"Адрес", style = wx.ALIGN_LEFT, size = NETWORKADDRESS_WIDGET_SIZE)
        self.btn = wx.StaticText(self, label = u"", style = wx.ALIGN_LEFT, size = BTN_SIZE)

        mainSizer.Add(self.addresType, 1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.adderss, 1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.btn, 1, wx.ALL, GRID_BORDER)

        self.SetSizer(mainSizer)
        self.Layout()

class initNetworkWidget(wx.Panel):
    def __init__(self, parent, strName, defValue = '100.100.100.100',*args, **kwds):
        self.addressType = strName
        wx.Panel.__init__(self, parent, *args, **kwds)
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.ipLabel = wx.StaticText(self, label = strName, size = NETWORK_WIDGET_SIZE)
        self.addressTextCtl = IpAddrCtrl(self, size = NETWORKADDRESS_WIDGET_SIZE)
        self.addressTextCtl.SetValue(defValue)
        self.writeAddressBtn = wx.Button(self, label = u"Записать", size = BTN_SIZE)

        mainSizer.Add(self.ipLabel, 1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.addressTextCtl, 1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.writeAddressBtn, 1, wx.ALL, GRID_BORDER)

        self.SetSizer(mainSizer)
        self.Layout()

class modbusWidget(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self,  *args, **kwds)
        GRID_BORDER = 10
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.modbusSettingsLabel = wx.StaticText(self, label = u"Порт")
        self.modbusSettingsTextCtl = wx.lib.intctrl.IntCtrl(self, pos = (5,65), size = (50, 20),
                                                            min = 0, max = 65535, limited = True)
        self.modbusSettingsWriteBtn = wx.Button(self, label = u"Записать")

        mainSizer.Add(self.modbusSettingsLabel, 1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.modbusSettingsTextCtl, 1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.modbusSettingsWriteBtn, 1, wx.ALL, GRID_BORDER)

        self.SetSizer(mainSizer)
        self.Layout()

class dateLabels(wx.Panel):
    def __init__(self, parent, *args, **kwds):
        wx.Panel.__init__(self, parent, *args, **kwds)
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        slash_label = u'/'

        self.typeLabel = wx.StaticText(self, label = u"", style = wx.ALIGN_CENTRE_HORIZONTAL, size = DATETIME_WIDGET_SIZE)
        self.day = wx.StaticText(self, label = u"День", style = wx.ALIGN_CENTRE_HORIZONTAL, size = DATETIME_WIDGET_SIZE)
        self.month = wx.StaticText(self, label = u"Месяц", style = wx.ALIGN_CENTRE_HORIZONTAL, size = DATETIME_WIDGET_SIZE)
        self.year = wx.StaticText(self, label = u"Год", style = wx.ALIGN_CENTRE_HORIZONTAL, size = DATETIME_WIDGET_SIZE)
        self.btn = wx.StaticText(self, label = u"", size = BTN_SIZE)

        mainSizer.Add(self.typeLabel, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.day, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(wx.StaticText(self, label = slash_label), 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.month, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(wx.StaticText(self, label = slash_label), 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.year, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.btn, 0.5, wx.ALL, GRID_BORDER)


        self.SetSizer(mainSizer)
        self.Layout()

class dateWidget(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self,  *args, **kwds)
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        slash_label = u'/'

        self.dateSettingsLabel = wx.StaticText(self, label = u"Дата", size = DATETIME_WIDGET_SIZE)
        self.dayTextCtl = wx.lib.intctrl.IntCtrl(self, size = DATETIME_WIDGET_SIZE ,min = 0, max = 31, limited = True)
        self.monthTextCtl = wx.lib.intctrl.IntCtrl(self, size = DATETIME_WIDGET_SIZE, min = 0, max = 12, limited = True)
        self.yearTextCtl = wx.lib.intctrl.IntCtrl(self, size = DATETIME_WIDGET_SIZE, min = 0, max = 64, limited = True)
        self.dateWriteBtn = wx.Button(self, label = u"Записать")

        mainSizer.Add(self.dateSettingsLabel, 1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.dayTextCtl, 0.1, wx.ALL, GRID_BORDER)
        mainSizer.Add(wx.StaticText(self, label = slash_label), 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.monthTextCtl, 0.1, wx.ALL, GRID_BORDER)
        mainSizer.Add(wx.StaticText(self, label = slash_label), 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.yearTextCtl, 0.1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.dateWriteBtn, 0.7, wx.ALL, GRID_BORDER)


        self.SetSizer(mainSizer)
        self.Layout()


class modbusWidget(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self,  *args, **kwds)
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.modbusSettingsLabel = wx.StaticText(self, label = u"Порт")
        self.modbusSettingsTextCtl = wx.lib.intctrl.IntCtrl(self, pos = (5,65), size = (50, 20),
                                                            min = 0, max = 65535, limited = True)
        self.modbusSettingsWriteBtn = wx.Button(self, label = u"Записать")

        mainSizer.Add(self.modbusSettingsLabel, 1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.modbusSettingsTextCtl, 1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.modbusSettingsWriteBtn, 1, wx.ALL, GRID_BORDER)

        self.SetSizer(mainSizer)
        self.Layout()

class timdLabels(wx.Panel):
    def __init__(self, parent, *args, **kwds):
        wx.Panel.__init__(self, parent, *args, **kwds)
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        label_size = (45,26)

        self.typeLabel = wx.StaticText(self, label = u"", size = TEXT_WIDGET_SIZE)
        self.hour = wx.StaticText(self, label = u"Часы", style = wx.ALIGN_CENTRE_HORIZONTAL, size = label_size)
        self.min = wx.StaticText(self, label = u"Мин", style = wx.ALIGN_CENTRE_HORIZONTAL, size = label_size)
        self.sec = wx.StaticText(self, label = u"Сек", style = wx.ALIGN_CENTRE_HORIZONTAL, size = label_size)
        self.btn = wx.StaticText(self, label = u"", size = BTN_SIZE)

        mainSizer.Add(self.typeLabel, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.hour, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.min, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.sec, 0.5, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.btn, 0.5, wx.ALL, GRID_BORDER)


        self.SetSizer(mainSizer)
        self.Layout()

class timeWidget(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self,  *args, **kwds)
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        colone_label = u":"

        self.modbusSettingsLabel = wx.StaticText(self, label = u"Время", size = TEXT_WIDGET_SIZE)
        self.hourTextCtl = wx.lib.intctrl.IntCtrl(self, size = DATETIME_WIDGET_SIZE, min = 0, max = 23, limited = True)
        self.minuteTextCtl = wx.lib.intctrl.IntCtrl(self, size = DATETIME_WIDGET_SIZE, min = 0, max = 59, limited = True)
        self.secondTextCtl = wx.lib.intctrl.IntCtrl(self, size = DATETIME_WIDGET_SIZE, min = 0, max = 59, limited = True)

        self.timeWriteBtn = wx.Button(self, label = u"Записать")

        mainSizer.Add(self.modbusSettingsLabel, 1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.hourTextCtl, 0.1, wx.ALL, GRID_BORDER)
        mainSizer.Add(wx.StaticText(self, label = colone_label), 0.1, wx.ALL, 5)
        mainSizer.Add(self.minuteTextCtl, 0.1, wx.ALL, GRID_BORDER)
        mainSizer.Add(wx.StaticText(self, label = colone_label), 0.1, wx.ALL, 5)
        mainSizer.Add(self.secondTextCtl, 0.1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.timeWriteBtn, 0.7, wx.ALL, GRID_BORDER)


        self.SetSizer(mainSizer)
        self.Layout()

class connectWidget(wx.Panel):
    def __init__(self, *args, **kwds):
        wx.Panel.__init__(self,  *args, **kwds)
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.portsListCombobox = wx.ComboBox(self)
        self.connectnBtn = wx.Button(self, label = u"Подключить")

        mainSizer.Add(self.portsListCombobox, 1, wx.ALL, GRID_BORDER)
        mainSizer.Add(self.connectnBtn, 0.3, wx.ALL, GRID_BORDER)

        self.SetSizer(mainSizer)
        self.Layout()


class ConfiguratorGUI(wx.Frame, wx.Dialog):
    heigthFrame = 690
    widthFrame = 540
    def __init__(self, parent = None, modulObject = None, hexFilePath = None):
        self.connectStatus = None # отображет сообщение от действий объекта SerialWork
        self.connection = False # отображает состояние соединения
        if parent is None:
            self.modulObj = mk201_proto()
            self.comPorts = self.modulObj.getPorts()[1]
            self.initWxFrame()
        else:
            self.parent = parent
            self.modulObj = modulObject
            self.hexFilePath = hexFilePath
            self.comPorts = self.modulObj.getPorts()[1]
            self.initWxDialogFrame()
        self.initWidgets()

    def initWxFrame(self):
        wx.Frame.__init__(self, None, id = ID_MAINWXFRAME, title = "MKSetup " + VERISON, name = 'mainWxFrame',
                          pos=(150,150), size = (self.heigthFrame, self.widthFrame))
        self.frameParent = wx.Panel(self)

        self.mainsizer = wx.BoxSizer(wx.VERTICAL)

        self.connectWidget = connectWidget(self)
        connectSettingsBox = wx.StaticBoxSizer(wx.StaticBox(self, label = u'Подключение'))

        connectSettingsBox.Add(self.connectWidget, 1, wx.EXPAND)
        self.mainsizer.Add(connectSettingsBox)


    def initWxDialogFrame(self):
        wx.Dialog.__init__(self, parent = self.parent, id = ID_MAINWXDIALOGFRAME, title = "MKSetup " + VERISON, name = 'mainWxFrame',
                          pos=(150,150), size = (self.heigthFrame, self.widthFrame))
        self.frameParent = self
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)


    def initWidgets(self):
        # self.panel = wx.Panel(self)

        '''Настройка TCP'''
        netwrokSettingsBox = wx.StaticBoxSizer(wx.StaticBox(self, label = u'Настройка TCP'),
                                                    wx.VERTICAL)

        self.labelWidget = networkLabels(self)
        netwrokSettingsBox.Add(self.labelWidget, 1, wx.EXPAND)
        self.ipWidget = initNetworkWidget(self, u'IP-адресс')
        netwrokSettingsBox.Add(self.ipWidget, 1, wx.EXPAND)
        self.gatewayWidget = initNetworkWidget(self, u'Шлюз')
        netwrokSettingsBox.Add(self.gatewayWidget, 1, wx.EXPAND)
        self.maskWidget = initNetworkWidget(self, u'Маска')
        netwrokSettingsBox.Add(self.maskWidget, 1, wx.EXPAND)

        self.mainsizer.Add(netwrokSettingsBox)

        '''Настройка COM-портов'''
        portSettingsBox = wx.StaticBoxSizer(wx.StaticBox(self, label = u'Настройка COM-портов'),
                                                    wx.VERTICAL)
        self.comLabel = comLabels(self)
        portSettingsBox.Add(self.comLabel, 1, wx.EXPAND)
        self.comWidget_1 = initComWidget(self, comNum = 1)
        portSettingsBox.Add(self.comWidget_1, 1, wx.EXPAND)
        self.comWidget_2 = initComWidget(self, comNum = 2)
        portSettingsBox.Add(self.comWidget_2, 1, wx.EXPAND)
        self.comWidget_3 = initComWidget(self, comNum = 3)
        portSettingsBox.Add(self.comWidget_3, 1, wx.EXPAND)

        self.mainsizer.Add(portSettingsBox)

        '''Настройка времени и даты'''

        grid_bord = 1

        dateSettingsBox = wx.StaticBoxSizer(wx.StaticBox(self, label = u'Настройка времени и даты'),
                                                    wx.VERTICAL)
        self.dateSettingsLabel = dateLabels(self)
        dateSettingsBox.Add(self.dateSettingsLabel, 1, wx.EXPAND, grid_bord)
        self.dateWidget = dateWidget(self)
        dateSettingsBox.Add(self.dateWidget, 1, wx.EXPAND, grid_bord)
        self.timeSettingsLabels = timdLabels(self)
        dateSettingsBox.Add(self.timeSettingsLabels, 1, wx.EXPAND, grid_bord)
        self.timeSettigsWidget = timeWidget(self)
        dateSettingsBox.Add(self.timeSettigsWidget, 1, wx.EXPAND, grid_bord)

        self.mainsizer.Add(dateSettingsBox)

        '''Вывод времени '''
        curTimeSettingsBox = wx.StaticBoxSizer(wx.StaticBox(self, label = u'Дата'),
                                                    wx.VERTICAL)
        self.timeLabels = timdLabels(self)
        curTimeSettingsBox.Add(self.timeLabels, 1, wx.EXPAND, 1)
        self.curTimeWidget = timeWidget(self)
        curTimeSettingsBox.Add(self.curTimeWidget, 1, wx.EXPAND, 1)

        self.mainsizer.Add(curTimeSettingsBox)

        '''Настройка MODBUS'''
        modbusSettingsBox = wx.StaticBoxSizer(wx.StaticBox(self, label = u'Настройка Modbus'),
                                                    wx.VERTICAL)
        self.modbusWidget = modbusWidget(self)
        modbusSettingsBox.Add(self.modbusWidget, 1, wx.EXPAND)

        self.mainsizer.Add(modbusSettingsBox)

        self.SetSizer(self.mainsizer)
        self.mainsizer.Fit(self)
        self.Layout()
        # self.statusBar = wx.StatusBar(self, id = wx.ID_ANY)

if __name__ == '__main__':
    app = wx.App(False)
    top = ConfiguratorGUI()
    top.Show()
    app.MainLoop()