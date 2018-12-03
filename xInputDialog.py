# encoding: utf-8
import wx
import wx.lib.sized_controls as wxsc

#~ #set value for widgets( StaticText and TextCtrl) height
wh=30
#~ #set value for max width times
mwt=8
#~ #set value for  wh times
wht=3

class InputDialog(wxsc.SizedDialog):

    def __init__(self,title='Setting values:',values={'事项':'','起始':'','结束':""}):

        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.CENTRE
        wxsc.SizedDialog.__init__(self, parent=None, id=-1, title=title, style=style)

        self.originvalues=values.copy()
        self.modifiedvalues=values.copy()
        self.pane = self.GetContentsPane()
        self.pane.SetSizerType("form")


        maxlen1=mwt*max([len(str(key)) for key in values])
        if maxlen1<wh*wht:
            maxlen1=wh*wht

        maxlen2=mwt*max([len(str(values[key])) for key in values])
        if maxlen2<wh*wht:
            maxlen2=wh*wht

        font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, faceName='微软雅黑')
        for key in self.modifiedvalues:
            keyStr=str(key)
            label=keyStr+' :'
            StaticText = wx.StaticText(parent=self.pane,id=-1,label=label,style=wx.ALIGN_RIGHT)
            StaticText.SetInitialSize((maxlen1,wh))
            StaticText.SetFont(font)
            value=str(self.modifiedvalues[key])
            TextCtrl = wx.TextCtrl(parent=self.pane, id=-1,value=value)
            TextCtrl.SetInitialSize((maxlen2,wh))
            TextCtrl.SetSizerProps(expand=True)
            TextCtrl.Name='TC_'+str(keyStr)

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))

        self.Fit()
        self.Center()

    def GetOriginValue(self):

        return self.originvalues

    def GetValue(self):

        for key in self.modifiedvalues:
            keyStr=str(key)
            TextCtrlName='TC_'+str(keyStr)
            TextCtrl=self.FindWindowByName(TextCtrlName)
            ovk=self.modifiedvalues[key]
            if(type(ovk)==int):
                self.modifiedvalues[key]=int(TextCtrl.GetValue().strip())
            elif(type(ovk)==float):
                self.modifiedvalues[key]=float(TextCtrl.GetValue().strip())
            else:
                self.modifiedvalues[key]=str(TextCtrl.GetValue())

        return self.modifiedvalues

def InputBox(title='添加新事项(๑•̀ㅂ•́)و✧',values={'事项名称':'','起始时间':'','结束时间':""}):

    dialog = InputDialog(title=title,values=values)
    rvalues = []
    if dialog.ShowModal() == wx.ID_OK:
        values= dialog.GetValue()
        values["content"] = values.pop("事项名称")
        values["starttime"] = values.pop("起始时间").replace('：',':')
        values["endtime"] = values.pop("结束时间").replace('：',':')
        rvalues.append(values)
    else:
        values=dialog.GetOriginValue()
    dialog.Destroy()
    return rvalues

