# encoding: utf-8
import wx
from xTreeCtrl import TimeTreeListCtrl
from xInputDialog import InputBox
from pubsub import pub

class DateFilter():
    def __init__(self, parent=None, id=-1, pos=(0, 0), size=(240, 400), conf=None, times=None):
        self.panel = wx.Panel(parent, id)
        self.conf = conf
        self.times = times
        self.boxsizer = wx.BoxSizer(wx.VERTICAL)
        self.treeListCtrl = TimeTreeListCtrl(self.panel, pos=pos, size=size, datas=self.times)
        self.boxsizer.Add(self.treeListCtrl, 1, wx.EXPAND)
        self.panel.SetSizer(self.boxsizer)
        self.treeListCtrl.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnTreeListCtrlDoubleClick)
        pass

    def OnTreeListCtrlDoubleClick(self, event):
        currentTreeItemId = event.GetItem()
        if self.treeListCtrl.GetItemPyData(currentTreeItemId) != None:
            datName, timespanIndex = str(self.treeListCtrl.GetItemPyData(currentTreeItemId)).split("|")
            TimeSpanObj = self.times.get(datName, [])[int(timespanIndex)]
            dlg = wx.MessageDialog(self.panel, "确定要删除"+self.treeListCtrl.GetDayChinexeName(datName) +'的'+TimeSpanObj.get('starttime', '')+"到"+TimeSpanObj.get('endtime', '')+TimeSpanObj.get('content', '')+"吗？", "注意(＞﹏＜)", wx.YES_NO | wx.ICON_QUESTION | wx.NO_DEFAULT | wx.CENTRE)
            if dlg.ShowModal() == wx.ID_YES:
                wx.CallAfter(pub.sendMessage, "Log", msg="删除事项"+self.treeListCtrl.GetDayChinexeName(datName) +'的'+TimeSpanObj.get('starttime', '')+"到"+TimeSpanObj.get('endtime', '')+TimeSpanObj.get('content', '') + "o(￣▽￣)ｄ")
                self.treeListCtrl.DeleteSubjectItem(currentTreeItemId)
                self.times = self.treeListCtrl.datas
        elif self.treeListCtrl.GetItemParent(currentTreeItemId) == self.treeListCtrl.root:
            values = InputBox()
            if len(values) > 0:
                wx.CallAfter(pub.sendMessage, "Log", msg="添加事项"+self.treeListCtrl.GetItemText(currentTreeItemId)[0:2] + '的' + values[0].get('starttime', '')+"到"+values[0].get('endtime', '')+values[0].get('content', '') + "o(￣▽￣)ｄ")
                self.treeListCtrl.AddSubjectItem(currentTreeItemId, values)
                self.times = self.treeListCtrl.datas
        pass
