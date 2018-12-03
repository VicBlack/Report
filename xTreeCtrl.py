#coding=utf-8

import wx
import wx.lib.gizmos as gizmos



class TimeTreeListCtrl(gizmos.TreeListCtrl):
    def __init__(self, parent=None, id=-1, pos=(0,0), size=wx.DefaultSize, style=wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT, datas=None):
        gizmos.TreeListCtrl.__init__(self, parent, id, pos, size, style)
        self.root = None
        self.datas = datas
        self.dayNames = {
            "Monday": "周一",
            "Tuesday": "周二",
            "Wednesday": "周三",
            "Thursday": "周四",
            "Friday": "周五",
            "Saturday": "周六",
            "Sunday": "周日",
        }
        self.InitUI()
        pass
    def InitUI(self):
        self.il = wx.ImageList(16, 16, True)
        self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16, 16)))
        self.il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))
        self.SetImageList(self.il)

        self.AddColumn('事项')
        self.AddColumn('起始')
        self.AddColumn('结束')

        self.Show()

        pass
    def Show(self):
        self.SetColumnWidth(0, 150)
        self.SetColumnWidth(1, 40)
        self.SetColumnWidth(2, 47)
        self.root = self.AddRoot('排除时间表')
        self.SetItemText(self.root, "", 1)
        self.SetItemText(self.root, "", 2)

        # 填充整个树
        dayIDs = self.datas.keys()
        for dayID in dayIDs:
            child = self.AppendItem(self.root, dayID)
            lastList = self.datas.get(dayID, [])
            childTitle = self.GetDayChinexeName(dayID)+" (共"+str(len(lastList))+"个时段)"
            self.SetItemText(child, childTitle, 0)
            self.SetItemText(child, "", 1)
            self.SetItemText(child, "", 2)
            self.SetItemImage(child, 0, which=wx.TreeItemIcon_Normal)
            self.SetItemImage(child, 1, which=wx.TreeItemIcon_Expanded)
            for index in range(len(lastList)):
                timespans = lastList[index]
                data = (dayID+"|"+str(index))
                last = self.AppendItem(child, str(index), data=data)
                self.SetItemText(last, timespans.get('content', ''), 0)
                self.SetItemText(last, timespans.get('starttime', ''), 1)
                self.SetItemText(last, timespans.get('endtime', ''), 2)
                self.SetItemImage(last, 0, which=wx.TreeItemIcon_Normal)
                self.SetItemImage(last, 1, which=wx.TreeItemIcon_Expanded)
        self.ExpandAll()
        pass
    def refreshDataShow(self, newDatas):
        if self.root != None:
            self.DeleteAllItems()
        if newDatas != None:
            self.datas = newDatas
            self.Show()
    def DeleteSubjectItem(self, treeItemId):
        itemData = self.GetItemPyData(treeItemId)
        datName, timespanIndex = str(itemData).split("|")
        self.datas[datName].pop(int(timespanIndex))
        self.refreshDataShow(self.datas)
        self.Refresh()
        pass
    def AddSubjectItem(self, treeItemId, values):
        itemData = self.GetItemText(treeItemId)[0:2]
        itemData = list (self.dayNames.keys()) [list (self.dayNames.values()).index (itemData)]
        childrens = self.GetChildrenCount(treeItemId)
        timespans = values[0]
        data = (itemData+"|"+str(childrens))
        last = self.AppendItem(treeItemId, childrens, data=data)
        self.SetItemText(last, timespans.get('content', ''), 0)
        self.SetItemText(last, timespans.get('starttime', ''), 1)
        self.SetItemText(last, timespans.get('endtime', ''), 2)
        self.SetItemImage(last, 0, which=wx.TreeItemIcon_Normal)
        self.SetItemImage(last, 1, which=wx.TreeItemIcon_Expanded)
        self.datas[itemData].append(timespans)
        self.refreshDataShow(self.datas)
        self.Refresh()

    def GetDayChinexeName(self, id):
        return self.dayNames.get(id, '')