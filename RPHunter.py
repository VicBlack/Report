# encoding: utf-8
import wx
import wx.grid as grid
import requests
import re
import time
import os
from sys import exit
import configparser
import pickle
from xDialog import LoginFrame
from Report import DecodeReport
from Report import DecodeCatchedReport
from DecodeYZM import decodeyzm
from threading import Thread
from xGridTable import ReportInfoGridTable
from xDateFilter import DateFilter
from pubsub import pub

validation_pattern = re.compile('id=\"__EVENTVALIDATION\".*value=\"(.*)" />')
VIEWSTATE_pattern = re.compile('id=\"__VIEWSTATE\".*value=\"(.*)" />')
rethink_pattern = re.compile('id=\"txtxd\" style=\"width:602px;\">(.*)</textarea>', re.DOTALL)
target_pattern = re.compile('href=\"javascript:__doPostBack\(&#39;(dg.*3)&#39;,&#39;')
cancel_pattern = re.compile('href=\"javascript:__doPostBack\(&#39;(dg.*1)&#39;,&#39;')
rethinking_pattern = re.compile('href=\"javascript:__doPostBack\(&#39;(dg.*2)&#39;,&#39;')
js_pattern = re.compile('<script language=javascript>alert\(\'(.*)\'\)</script>')
sorry_pattern = re.compile('(<div class=\"sorry-box\">)')
# url_home = "http://202.4.157.73/pyxx/login.aspx"
# image_url = "http://202.4.157.73/pyxx/PageTemplate/NsoftPage/yzm/IdentifyingCode.aspx"
url_home = "http://202.4.152.190:8080/pyxx/login.aspx"
image_url = "http://202.4.152.190:8080/pyxx/PageTemplate/NsoftPage/yzm/IdentifyingCode.aspx"
url_rethink = "http://202.4.152.190:8080/pyxx/txhdgl/hdxxdetail.aspx"


def IsTimeOK(stime, etime, times):
    stimestamp = time.mktime(time.strptime(stime,"%Y/%m/%d %H:%M:%S"))
    etimestamp = time.mktime(time.strptime(etime,"%Y/%m/%d %H:%M:%S"))
    starttime = time.localtime(stimestamp)
    weekinfo = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day = weekinfo[starttime.tm_wday]
    daytimeslist = times[day]
    for i in range(len(daytimeslist)):
        task = daytimeslist[i]
        taskstimestamp = time.mktime(time.strptime(time.strftime("%Y/%m/%d ", starttime)+task['starttime'],"%Y/%m/%d %H:%M"))
        tasketimestamp = time.mktime(time.strptime(time.strftime("%Y/%m/%d ", starttime)+task['endtime'],"%Y/%m/%d %H:%M"))
        if etimestamp < taskstimestamp or tasketimestamp < stimestamp:
            continue
        else:
            return False
    return True


def IsNameOK(name, list):
    for i in range(list.GetCount()):
        if name == list.GetString(i):
            return False
    return True


def IsTypeOK(type, conf):
    if conf.getboolean("Settings", "SelectActivities") is False and type == "活动报名":
        return False
    return True


class ReportHunter(wx.App):

    def __init__(self):
        wx.App.__init__(self)
        self.conf = configparser.ConfigParser()
        self.times = {
            'Monday': [
                {'content': '有课', 'starttime':'9:50', 'endtime':'12:20'},
                {'content': '组会', 'starttime': '14:30', 'endtime': '16:30'}
            ],
            'Tuesday':[
                {'content': '有课', 'starttime': '18:00', 'endtime': '20:00'}
            ],
            'Wednesday': [],
            'Thursday': [],
            'Friday':[
                {'content': '有课', 'starttime':'9:50', 'endtime':'12:20'}
            ],
            'Saturday': [
                {'content': '逛街', 'starttime': '18:00', 'endtime': '20:00'}
            ],
            'Sunday': [
                {'content': '游戏', 'starttime': '14:00', 'endtime': '17:00'}
            ]
        }
        self.LoadConfig()
        self.s = requests.session()
        self.s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'})
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        leftsizer = wx.BoxSizer(wx.VERTICAL)
        rightsizer = wx.BoxSizer(wx.VERTICAL)
        self.confsizer = wx.BoxSizer(wx.VERTICAL)
        righttopsizer = wx.BoxSizer()
        ReadyBox = wx.StaticBox(self.leftpanel, -1, '待抢报告：')
        ReadyBoxsizer = wx.StaticBoxSizer(ReadyBox, wx.VERTICAL)
        self.ReadyTable = grid.Grid(self.leftpanel, -1, style=wx.WANTS_CHARS)
        self.ReadyTable.SetRowLabelSize(0)
        self.ReadyTable.SetDefaultCellOverflow(False)
        self.ReadyTable.EnableEditing(False)
        self.ReadyTable.EnableDragRowSize(False)
        self.ReadyTable.EnableDragColSize(False)
        ReadyBoxsizer.Add(self.ReadyTable, 1, wx.EXPAND)
        self.ReadyTable.Bind(grid.EVT_GRID_CELL_LEFT_DCLICK, self.ReadyTableDClik)

        CatchedBox = wx.StaticBox(self.leftpanel, -1, '已选报告：')
        CatchedBoxsizer = wx.StaticBoxSizer(CatchedBox, wx.VERTICAL)
        self.CatchedTable = grid.Grid(self.leftpanel, -1, style=wx.WANTS_CHARS)
        self.CatchedTable.SetRowLabelSize(0)
        self.CatchedTable.SetDefaultCellOverflow(False)
        self.CatchedTable.EnableEditing(False)
        self.CatchedTable.EnableDragRowSize(False)
        self.CatchedTable.EnableDragColSize(False)
        CatchedBoxsizer.Add(self.CatchedTable, 1, wx.EXPAND)
        self.CatchedTable.Bind(grid.EVT_GRID_CELL_LEFT_DCLICK, self.CatchedTableDClik)

        LogBox = wx.StaticBox(self.leftpanel, -1, '日志：')
        LogBoxsizer = wx.StaticBoxSizer(LogBox, wx.VERTICAL)
        self.log = wx.TextCtrl(self.leftpanel, style=wx.TE_MULTILINE| wx.TE_READONLY)
        LogBoxsizer.Add(self.log, 1, wx.EXPAND)

        self.SelectActivitiesCB = wx.CheckBox(self.rightpanel, -1, "活动报名", size=wx.DefaultSize)
        self.SelectActivitiesCB.SetValue(self.conf.getboolean("Settings", "SelectActivities"))
        self.EndlessTryConnectingCB = wx.CheckBox(self.rightpanel, -1, "无限重连", size=wx.DefaultSize)
        self.EndlessTryConnectingCB.SetValue(self.conf.getboolean("Settings", "EndlessTryConnecting"))
        self.AutoHuntingCB = wx.CheckBox(self.rightpanel, -1, "自动开抢", size=wx.DefaultSize)
        self.AutoHuntingCB.SetValue(self.conf.getboolean("Settings", "AutoHunting"))
        self.TimeSpanLabel = wx.StaticText(self.rightpanel, -1, '抢报告间隔：')
        self.TimeSpanTC = wx.TextCtrl(self.rightpanel, -1, self.conf.get("Settings", "TimeSpan"), size=(70, -1))
        TimeSpanSizer = wx.BoxSizer()
        TimeSpanSizer.Add(self.TimeSpanLabel, 0, wx.ALIGN_CENTER_VERTICAL)
        TimeSpanSizer.Add(self.TimeSpanTC, 1, wx.EXPAND | wx.ALL)
        self.StartBTN = wx.ToggleButton(self.rightpanel, -1, '抢', size=(100, 100))
        self.StartBTN.SetFont(wx.Font(50, wx.DEFAULT, wx.NORMAL, wx.BOLD, faceName='华文行楷'))
        self.StartBTN.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggle)

        self.DateFilter = DateFilter(self.rightpanel, -1, pos=(0, 0), size=(240, 380),  conf=self.conf, times=self.times)
        DateFilterbox = wx.StaticBox(self.rightpanel, -1, '非选时段：')
        DateFilterboxsizer = wx.StaticBoxSizer(DateFilterbox, wx.VERTICAL)
        DateFilterboxsizer.Add(self.DateFilter.panel, 1, wx.EXPAND)

        self.textFont = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        self.listDatas = []
        self.UnSelectlist = wx.ListBox(self.rightpanel, -1, size=(300, 120), choices=self.listDatas, style=wx.LB_SINGLE | wx.LB_HSCROLL)
        self.UnSelectlist.SetFont(self.textFont)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.listCtrlSelectFunc, self.UnSelectlist)
        UnSelectListbox = wx.StaticBox(self.rightpanel, -1, '非选报告：')
        UnSelectListboxsizer = wx.StaticBoxSizer(UnSelectListbox, wx.VERTICAL)
        UnSelectListboxsizer.Add(self.UnSelectlist, 1, wx.EXPAND)

        leftsizer.Add(ReadyBoxsizer, 1, wx.EXPAND | wx.BOTTOM, 5)
        leftsizer.Add(CatchedBoxsizer, 1, wx.EXPAND | wx.BOTTOM, 5)
        leftsizer.Add(LogBoxsizer, 1, wx.EXPAND | wx.RIGHT, 5)

        self.confsizer.AddMany([(self.SelectActivitiesCB, 0, wx.ALL, 3), (self.EndlessTryConnectingCB, 0, wx.ALL, 3), (self.AutoHuntingCB, 0, wx.ALL, 3), (TimeSpanSizer, 0, wx.ALL, 3)])
        righttopsizer.Add(self.confsizer, 1, wx.LEFT | wx.ALL, 5)
        righttopsizer.Add(self.StartBTN, 1, wx.RIGHT | wx.ALL, 5)
        rightsizer.Add(righttopsizer, 0, wx.ALL, 2)
        rightsizer.Add(DateFilterboxsizer, 1, wx.EXPAND | wx.ALL, 2)
        rightsizer.Add(UnSelectListboxsizer, 1, wx.EXPAND | wx.ALL, 2)

        self.rightpanel.SetSizer(rightsizer)
        self.leftpanel.SetSizer(leftsizer)
        sizer.Add(self.leftpanel, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.rightpanel, 0, wx.EXPAND | wx.ALL, 5)
        self.panelsizer = wx.BoxSizer()
        self.panelsizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(self.panelsizer)

        self.LoginFrame = LoginFrame(title='Reports Hunter |･ω･｀)', func_callBack=self.ReadyToHunt, session=self.s, conf=self.conf)
        self.LoginFrame.InitConnect()
        wx.CallAfter(pub.sendMessage, "Log", msg="初始化完成 <(￣︶￣)>")

    def OnInit(self):
        self.frame = wx.Frame(None, title="Reports Hunter (๑•̀ㅂ•́)و✧", size=(1400, 700))
        self.frame.Centre()
        self.frame.SetIcon(wx.Icon(name=".\\icon.ico",  type=wx.BITMAP_TYPE_ICO))
        self.frame.Bind(wx.EVT_CLOSE, self.cancleEvent)
        self.panel = wx.Panel(self.frame)
        self.leftpanel = wx.Panel(self.panel, -1, pos=(0, 0), size=(1150, 700))
        self.rightpanel = wx.Panel(self.panel, -1, pos=(1150, 0), size=(270, 700))
        pub.subscribe(self.LogMessage, "Log")
        pub.subscribe(self.RefreshData, "RefreshData")
        return True

    def LoadConfig(self):
        wx.CallAfter(pub.sendMessage, "Log", msg="加载配置文件中（。・＿・。）")
        if not os.path.isfile(".\\ReportHunter.conf"):
            fw = open('.\\ReportHunter.conf', 'wb')
            self.conf.add_section("Account")
            self.conf.set("Account", "ID", "")
            self.conf.set("Account", "PWD", "")
            self.conf.set("Account", "SavePassword", "False")
            self.conf.add_section("Settings")
            self.conf.set("Settings", "EndlessTryConnecting", "False")
            self.conf.set("Settings", "AutoHunting", "False")
            self.conf.set("Settings", "SelectActivities", "False")
            self.conf.set("Settings", "TimeSpan", "3.5")
            pickle.dump(self.conf, fw)
            fw.close()
        else:
            try:
                fw = open('.\\ReportHunter.conf', 'rb')
                self.conf = pickle.load(fw)
            except Exception as e:
                os.chdir(os.getcwd())
                os.remove('.\\ReportHunter.conf')
                fw = open('.\\ReportHunter.conf', 'wb')
                self.conf.add_section("Account")
                self.conf.set("Account", "ID", "")
                self.conf.set("Account", "PWD", "")
                self.conf.set("Account", "SavePassword", "False")
                self.conf.add_section("Settings")
                self.conf.set("Settings", "EndlessTryConnecting", "False")
                self.conf.set("Settings", "AutoHunting", "False")
                self.conf.set("Settings", "SelectActivities", "False")
                self.conf.set("Settings", "TimeSpan", "3.5")
                pickle.dump(self.conf, fw)
                fw.close()
                wx.CallAfter(pub.sendMessage, "Log", msg=str(e)+'配置恢复默认值（＞人＜；）')

        if not os.path.isfile(".\\DateUnavailable.pkl"):
            fwp = open('.\\DateUnavailable.pkl', 'wb')
            pickle.dump(self.times, fwp)
            fwp.close()
        else:
            try:
                fwp = open('.\\DateUnavailable.pkl', 'rb')
                self.times = pickle.load(fwp)
            except Exception as e:
                os.chdir(os.getcwd())
                os.remove('.\\DateUnavailable.pkl')
                fwp = open('.\\DateUnavailable.pkl', 'wb')
                pickle.dump(self.times, fwp)
                fwp.close()
                wx.CallAfter(pub.sendMessage, "Log", msg=str(e)+'时间配置恢复默认值（＞人＜；）')

    def ReadyToHunt(self, id):
        self.id = id
        self.url_choice = "http://202.4.152.190:8080/pyxx/txhdgl/hdlist.aspx?xh={username}".format(username=self.id)
        wx.CallAfter(pub.sendMessage, "Log", msg="登录成功 (￣▽￣)～■干杯□～(￣▽￣)")
        self.LoadConfig()
        self.RefreshData()
        self.frame.GetEffectiveMinSize()
        self.frame.Show()
        if self.AutoHuntingCB.GetValue():
            self.StartHunting()

    def OnToggle(self, event):
        state = event.GetEventObject().GetValue()
        if state == True:
            self.leftpanel.Disable()
            self.SelectActivitiesCB.Disable()
            self.EndlessTryConnectingCB.Disable()
            self.AutoHuntingCB.Disable()
            self.TimeSpanTC.Disable()
            self.DateFilter.panel.Disable()
            self.UnSelectlist.Disable()
            event.GetEventObject().SetLabel("停")
            wx.CallAfter(pub.sendMessage, "Log", msg="开始抢报告 ～(￣▽￣～)(～￣▽￣)～")
            Hunter(self)
        else:
            self.leftpanel.Enable()
            self.SelectActivitiesCB.Enable()
            self.EndlessTryConnectingCB.Enable()
            self.AutoHuntingCB.Enable()
            self.TimeSpanTC.Enable()
            self.DateFilter.panel.Enable()
            self.UnSelectlist.Enable()
            event.GetEventObject().SetLabel("抢")
            wx.CallAfter(pub.sendMessage, "Log", msg="暂停抢报告 (｡･∀･)ﾉﾞ")
            wx.CallAfter(pub.sendMessage, "StopHunt")

    def StartHunting(self):
        self.StartBTN.SetValue(True)
        self.leftpanel.Disable()
        self.SelectActivitiesCB.Disable()
        self.EndlessTryConnectingCB.Disable()
        self.AutoHuntingCB.Disable()
        self.TimeSpanTC.Disable()
        self.DateFilter.panel.Disable()
        self.UnSelectlist.Disable()
        self.StartBTN.SetLabel("停")
        wx.CallAfter(pub.sendMessage, "Log", msg="开始抢报告 ～(￣▽￣～)(～￣▽￣)～")
        Hunter(self)

    def cancleEvent(self, event):
        self.SaveConf()
        exit(0)

    def SaveConf(self):
        wx.CallAfter(pub.sendMessage, "Log", msg="保存配置文件中（。・＿・。）")
        self.conf.set("Settings", "SelectActivities", str(self.SelectActivitiesCB.GetValue()))
        self.conf.set("Settings", "EndlessTryConnecting", str(self.EndlessTryConnectingCB.GetValue()))
        self.conf.set("Settings", "AutoHunting", str(self.AutoHuntingCB.GetValue()))
        self.conf.set("Settings", "TimeSpan", self.TimeSpanTC.GetValue())
        fw = open('ReportHunter.conf', 'wb')
        pickle.dump(self.conf, fw)
        fw.close()
        fwp = open('DateUnavailable.pkl', 'wb')
        pickle.dump(self.times, fwp)
        fwp.close()

    def listCtrlSelectFunc(self, event):
        indexSelected = event.GetEventObject().GetSelection()
        wx.CallAfter(pub.sendMessage, "Log", msg="将报告"+self.UnSelectlist.GetString(indexSelected)+"移出非选队列 (＠￣ー￣＠)")
        self.UnSelectlist.Delete(indexSelected)
        self.RefreshData()

    def ReadyTableDClik(self, event):
        rowindex = event.GetRow()
        table = self.ReadyTable.GetTable()
        rowdata = table.PopData(rowindex)
        reportname = []
        reportname.append(rowdata[1])
        self.UnSelectlist.Append(reportname)
        wx.CallAfter(pub.sendMessage, "Log", msg="将报告"+rowdata[1]+"移入非选队列 (￣0￣)/")
        self.RefreshData()

    def CatchedTableDClik(self, event):
        rowindex = event.GetRow()
        table = self.CatchedTable.GetTable()
        rowdata = table.GetValue(rowindex, 1)
        jionway = table.GetValue(rowindex, 6)
        endjointime = table.GetValue(rowindex, 7)
        if not jionway == "人工安排":
            ejtimestamp = time.mktime(time.strptime(endjointime, "%Y/%m/%d %H:%M:%S"))
            if time.time() < ejtimestamp:
                the_form = {
                    '__EVENTTARGET': self.cancel[rowindex],
                    '__EVENTARGUMENT': '',
                    '__VIEWSTATE': self.viewstate,
                    '__EVENTVALIDATION': self.validation,
                    'txtyzm': '',
                }
                dlg = wx.MessageDialog(self.panel, "确定要退掉"+rowdata+"吗？", "警告 (＞﹏＜)", wx.YES_NO | wx.ICON_QUESTION | wx.NO_DEFAULT  | wx.CENTRE)
                if dlg.ShowModal() == wx.ID_YES:
                    try:
                        respon = self.s.post(self.url_choice, the_form).text
                        js = re.findall(js_pattern, respon)
                        if js[0] == '已成功取消！':
                            wx.CallAfter(pub.sendMessage, "Log", msg="成功退选报告"+rowdata+" (￣0￣)/")
                            self.RefreshData()
                        else:
                            wx.CallAfter(pub.sendMessage, "Log", msg=js[0]+" (￣0￣)/")
                            self.RefreshData()
                    except Exception as e:
                        wx.CallAfter(pub.sendMessage, "Log", msg=str(e)+'（＞人＜；）')
                        return None
                return None
        the_form = {
            '__EVENTTARGET': self.rethinking[rowindex],
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': self.viewstate,
            '__EVENTVALIDATION': self.validation,
            'txtyzm': '',
        }
        try:
            respon = self.s.post(self.url_choice, the_form).text
            validation = re.findall(validation_pattern, respon)[0]
            viewstate = re.findall(VIEWSTATE_pattern, respon)[0]
            rethink = re.findall(rethink_pattern, respon)[0][2:]
            dlg = wx.TextEntryDialog(self.panel, message="心得：", caption="提交心得", value=rethink, style=wx.TE_MULTILINE | wx.OK | wx.CANCEL | wx.CENTRE )
            if dlg.ShowModal() == wx.ID_OK:
                rethink = dlg.GetValue()
                rethinking_form = {
                    '__EVENTTARGET': 'lbsq1',
                    '__EVENTARGUMENT': '',
                    '__VIEWSTATE': viewstate,
                    '__EVENTVALIDATION': validation,
                    'myscrollheight': '0',
                    'txtxd': rethink,
                }
                try:
                    res = self.s.post(url_rethink, rethinking_form).text
                    js = re.findall(js_pattern, res)
                    wx.CallAfter(pub.sendMessage, "Log", msg=js[0]+" (￣0￣)/")
                    self.RefreshData()
                except Exception as e:
                    wx.CallAfter(pub.sendMessage, "Log", msg=str(e)+'（＞人＜；）')
                    return None
        except Exception as e:
            wx.CallAfter(pub.sendMessage, "Log", msg=str(e)+'（＞人＜；）')
            return None

    def RefreshData(self):
        self.gridDatas = []
        self.catchedgridDatas = []
        self.target = []
        self.cancel = []
        self.rethinking = []
        self.times = self.DateFilter.times
        activity_page = self.s.get(self.url_choice).text
        self.validation = re.findall(validation_pattern, activity_page)[0]
        self.viewstate = re.findall(VIEWSTATE_pattern, activity_page)[0]
        table_pattern = re.compile('id=\"dgData00\"(.*?)</table>', re.DOTALL)
        table = re.findall(table_pattern, activity_page)[0]
        catched_pattern = re.compile('id=\"dgData\"(.*?)</table>', re.DOTALL)
        catchedtable = re.findall(catched_pattern, activity_page)[0]
        Reports = DecodeReport(table)
        Catched_Reports = DecodeCatchedReport(catchedtable)
        for i in range(len(Reports)):
            areport = []
            areport.append(Reports[i].type)
            areport.append(Reports[i].name)
            areport.append(Reports[i].starttime)
            areport.append(Reports[i].endtime)
            areport.append(Reports[i].location)
            areport.append(Reports[i].maxnum)
            areport.append(Reports[i].availablenum)
            areport.append(Reports[i].endjiontime)
            self.target.append(Reports[i].target)
            if IsNameOK(areport[1], self.UnSelectlist):
                self.gridDatas.append(areport)
        colLabels = ['类别', '名称', '开始时间', '结束时间', '地点', '总量', '已报', '报名截止时间']
        self.infoTable = ReportInfoGridTable(self.gridDatas, colLabels)
        for i in range(len(Catched_Reports)):
            areport = []
            areport.append(Catched_Reports[i].type)
            areport.append(Catched_Reports[i].name)
            areport.append(Catched_Reports[i].starttime)
            areport.append(Catched_Reports[i].endtime)
            areport.append(Catched_Reports[i].location)
            areport.append(Catched_Reports[i].maxnum)
            areport.append(Catched_Reports[i].joinway)
            areport.append(Catched_Reports[i].endjiontime)
            self.cancel.append(Catched_Reports[i].cancel)
            self.rethinking.append(Catched_Reports[i].rethinking)
            self.catchedgridDatas.append(areport)
        catchedcolLabels = ['类别', '名称', '开始时间', '结束时间', '地点', '总量', '报名方式', '报名截止时间']
        self.catchedinfoTable = ReportInfoGridTable(self.catchedgridDatas, catchedcolLabels)
        self.ReadyTable.SetTable(self.infoTable, True)
        self.ReadyTable.AutoSize()
        self.CatchedTable.SetTable(self.catchedinfoTable, True)
        self.CatchedTable.AutoSize()

    def LogMessage(self, msg):
        self.log.AppendText(msg+'\n')


class Hunter(Thread):
    def __init__(self, RP):
        Thread.__init__(self)
        self.RP = RP
        self.ifdo = True
        pub.subscribe(self.stop, "StopHunt")
        self.start()

    def run(self):
        record = 1
        while True:
            if self.ifdo:
                try:
                    wx.CallAfter(pub.sendMessage, "RefreshData")
                    wx.CallAfter(pub.sendMessage, "Log", msg='正在尝试第'+str(record)+'次抢报告 ε=ε=ε=(~￣▽￣)~')
                    record += 1
                    activity_page = self.RP.s.get(self.RP.url_choice).text
                    target_pattern = re.compile('href=\"javascript:__doPostBack\(&#39;(dg.*3)&#39;,&#39;')
                    target = re.findall(target_pattern, activity_page)
                    validation = re.findall(validation_pattern, activity_page)[0]
                    viewstate = re.findall(VIEWSTATE_pattern, activity_page)[0]
                    table_pattern = re.compile('id=\"dgData00\"(.*?)</table>', re.DOTALL)
                    table = re.findall(table_pattern, activity_page)[0]
                    Reports = DecodeReport(table)
                    for i in range(len(Reports)):
                        if Reports[i].maxnum > Reports[i].availablenum and IsTypeOK(Reports[i].type, self.RP.conf) and IsTimeOK(Reports[i].starttime, Reports[i].endtime, self.RP.times) and IsNameOK(Reports[i].name, self.RP.UnSelectlist):
                            while True:
                                picture = self.RP.s.get(image_url)
                                with open('.\\yzmcode.jpg', 'wb') as local:
                                    local.write(picture.content)
                                code = decodeyzm('.\\yzmcode.jpg')
                                the_form = {
                                    '__EVENTTARGET': target[i],
                                    '__EVENTARGUMENT': '',
                                    '__VIEWSTATE': viewstate,
                                    '__EVENTVALIDATION': validation,
                                    'txtyzm': code,
                                }
                                try:
                                    respon = self.RP.s.post(self.RP.url_choice, the_form).text
                                    js = re.findall(js_pattern, respon)
                                    if len(js) > 0:
                                        wx.CallAfter(pub.sendMessage, "Log", msg=js[0]+' (｡･∀･)ﾉﾞ')
                                        wx.CallAfter(pub.sendMessage, "RefreshData")
                                        break
                                except Exception as e:
                                    wx.CallAfter(pub.sendMessage, "Log", msg=str(e)+'（＞人＜；）')
                        else:
                            pass
                    time.sleep(float(self.RP.conf.get("Settings", "TimeSpan")))
                except Exception as e:
                    wx.CallAfter(pub.sendMessage, "Log", msg=str(e)+'（＞人＜；）')
            else:
                break

    def stop(self):
        self.ifdo = False


if __name__ == '__main__':
    RP = ReportHunter()
    RP.MainLoop()

