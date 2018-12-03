#coding=utf-8
import wx
import re
import time
import pickle
from sys import exit

# url_home = "http://202.4.157.73/pyxx/login.aspx"
# image_url = "http://202.4.157.73/pyxx/PageTemplate/NsoftPage/yzm/IdentifyingCode.aspx"
url_home = "http://202.4.152.190:8080/pyxx/login.aspx"
image_url = "http://202.4.152.190:8080/pyxx/PageTemplate/NsoftPage/yzm/IdentifyingCode.aspx"
validation_pattern = re.compile('id=\"__EVENTVALIDATION\".*value=\"(.*)" />')
VIEWSTATE_pattern = re.compile('id=\"__VIEWSTATE\".*value=\"(.*)" />')
js_pattern = re.compile('<script language=javascript>alert\(\'(.*)\'\)</script>')
sorry_pattern = re.compile('(<div class=\"sorry-box\">)')

class LoginFrame(wx.Frame):
    def __init__(self, title, func_callBack, session, conf):
        wx.Frame.__init__(self, None, -1, title, size=(320, 300), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        self.func_callBack = func_callBack
        self.s = session
        self.conf = conf
        self.themeColor = '#0a74f7'
        self.the_form = {
            '__VIEWSTATE': '',
            '__EVENTVALIDATION': '',
            '_ctl0:txtyzm': '',
            "_ctl0:txtusername": '',
            "_ctl0:txtpassword": '',
            "_ctl0:ImageButton1.x": "0",
            "_ctl0:ImageButton1.y": "0",
        }
        self.StatusBar = self.CreateStatusBar()
        self.panel = wx.Panel(self, -1, size=(310, 290))
        font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD, faceName='微软雅黑')
        icon = wx.Icon(name=".\\icon.ico",  type=wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        accountLabel = wx.StaticText(self.panel, -1, '学号', pos=(20, 24))
        accountLabel.SetForegroundColour(self.themeColor)
        accountLabel.SetFont(font)
        self.accountInput = wx.TextCtrl(self.panel, -1, '', pos=(90, 25), size=(180, -1))
        self.accountInput.SetForegroundColour('gray')
        self.accountInput.SetFont(font)

        passwordLabel = wx.StaticText(self.panel, -1, '密码', pos=(20, 69))
        passwordLabel.SetFont(font)
        passwordLabel.SetForegroundColour(self.themeColor)
        self.passwordInput = wx.TextCtrl(self.panel, -1, '', pos=(90, 70), size=(180, -1), style=wx.TE_PASSWORD)
        self.passwordInput.SetForegroundColour(self.themeColor)
        self.passwordInput.SetFont(font)

        yzmcodeLabel = wx.StaticText(self.panel, -1, '验证码', pos=(20, 114))
        yzmcodeLabel.SetForegroundColour(self.themeColor)
        yzmcodeLabel.SetFont(font)
        self.yzmcodeInput = wx.TextCtrl(self.panel, -1, '', pos=(90, 115), size=(70, -1), style=wx.TE_PROCESS_ENTER)
        self.yzmcodeInput.SetForegroundColour('gray')
        self.yzmcodeInput.SetFont(font)

        picture = b'GIF89a@\x00\x1c\x00\xf7\x00\x00\x00\x00\x00\x00\x003\x00\x00f\x00\x00\x99\x00\x00\xcc\x00\x00\xff\x00+\x00\x00+3\x00+f\x00+\x99\x00+\xcc\x00+\xff\x00U\x00\x00U3\x00Uf\x00U\x99\x00U\xcc\x00U\xff\x00\x80\x00\x00\x803\x00\x80f\x00\x80\x99\x00\x80\xcc\x00\x80\xff\x00\xaa\x00\x00\xaa3\x00\xaaf\x00\xaa\x99\x00\xaa\xcc\x00\xaa\xff\x00\xd5\x00\x00\xd53\x00\xd5f\x00\xd5\x99\x00\xd5\xcc\x00\xd5\xff\x00\xff\x00\x00\xff3\x00\xfff\x00\xff\x99\x00\xff\xcc\x00\xff\xff3\x00\x003\x0033\x00f3\x00\x993\x00\xcc3\x00\xff3+\x003+33+f3+\x993+\xcc3+\xff3U\x003U33Uf3U\x993U\xcc3U\xff3\x80\x003\x8033\x80f3\x80\x993\x80\xcc3\x80\xff3\xaa\x003\xaa33\xaaf3\xaa\x993\xaa\xcc3\xaa\xff3\xd5\x003\xd533\xd5f3\xd5\x993\xd5\xcc3\xd5\xff3\xff\x003\xff33\xfff3\xff\x993\xff\xcc3\xff\xfff\x00\x00f\x003f\x00ff\x00\x99f\x00\xccf\x00\xfff+\x00f+3f+ff+\x99f+\xccf+\xfffU\x00fU3fUffU\x99fU\xccfU\xfff\x80\x00f\x803f\x80ff\x80\x99f\x80\xccf\x80\xfff\xaa\x00f\xaa3f\xaaff\xaa\x99f\xaa\xccf\xaa\xfff\xd5\x00f\xd53f\xd5ff\xd5\x99f\xd5\xccf\xd5\xfff\xff\x00f\xff3f\xffff\xff\x99f\xff\xccf\xff\xff\x99\x00\x00\x99\x003\x99\x00f\x99\x00\x99\x99\x00\xcc\x99\x00\xff\x99+\x00\x99+3\x99+f\x99+\x99\x99+\xcc\x99+\xff\x99U\x00\x99U3\x99Uf\x99U\x99\x99U\xcc\x99U\xff\x99\x80\x00\x99\x803\x99\x80f\x99\x80\x99\x99\x80\xcc\x99\x80\xff\x99\xaa\x00\x99\xaa3\x99\xaaf\x99\xaa\x99\x99\xaa\xcc\x99\xaa\xff\x99\xd5\x00\x99\xd53\x99\xd5f\x99\xd5\x99\x99\xd5\xcc\x99\xd5\xff\x99\xff\x00\x99\xff3\x99\xfff\x99\xff\x99\x99\xff\xcc\x99\xff\xff\xcc\x00\x00\xcc\x003\xcc\x00f\xcc\x00\x99\xcc\x00\xcc\xcc\x00\xff\xcc+\x00\xcc+3\xcc+f\xcc+\x99\xcc+\xcc\xcc+\xff\xccU\x00\xccU3\xccUf\xccU\x99\xccU\xcc\xccU\xff\xcc\x80\x00\xcc\x803\xcc\x80f\xcc\x80\x99\xcc\x80\xcc\xcc\x80\xff\xcc\xaa\x00\xcc\xaa3\xcc\xaaf\xcc\xaa\x99\xcc\xaa\xcc\xcc\xaa\xff\xcc\xd5\x00\xcc\xd53\xcc\xd5f\xcc\xd5\x99\xcc\xd5\xcc\xcc\xd5\xff\xcc\xff\x00\xcc\xff3\xcc\xfff\xcc\xff\x99\xcc\xff\xcc\xcc\xff\xff\xff\x00\x00\xff\x003\xff\x00f\xff\x00\x99\xff\x00\xcc\xff\x00\xff\xff+\x00\xff+3\xff+f\xff+\x99\xff+\xcc\xff+\xff\xffU\x00\xffU3\xffUf\xffU\x99\xffU\xcc\xffU\xff\xff\x80\x00\xff\x803\xff\x80f\xff\x80\x99\xff\x80\xcc\xff\x80\xff\xff\xaa\x00\xff\xaa3\xff\xaaf\xff\xaa\x99\xff\xaa\xcc\xff\xaa\xff\xff\xd5\x00\xff\xd53\xff\xd5f\xff\xd5\x99\xff\xd5\xcc\xff\xd5\xff\xff\xff\x00\xff\xff3\xff\xfff\xff\xff\x99\xff\xff\xcc\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00!\xf9\x04\x01\x00\x00\xfc\x00,\x00\x00\x00\x00@\x00\x1c\x00\x00\x08\xff\x00\x01\x08\x1cH\xb0\xa0\xc1\x83\x06\x95)#\xa8\x10\xa1C\x83\xfb"J\x9cH\xb1\xa2E\x8a\n#*\xccx\xb1\xa3D\x81\xfb\xa2\x85\x1c)\xb2\xa4\xc2\x92$I\x9e<9r\xdfFe\x12Q\xcaL9\x13\xe4\xbee\x11\xeb\x89\xac\x17\xb2^F\x9d\xfb\x80\xf2\x8c\xe6\x13&1\x98<C\x12\xc3\x19\x91\xa9\xd0\x9d=\x9b\xe6\x14\xb9O \xd5\x91\xca\x88\xb5\x8cH\xb5\xebV\x8a(%\x02my\xd5\xab\xd7}Gm2ui\x14&\xce\xa1<\x93\x02\xc5)\xd2)\xd7\xadL\xf36\xcd:\x95kC\x00^\xe9\xb2\xbd[\xb6\xe5\xcf\xc0.\xb5\xde\xbc\x1b\xd4+=ea\xd7\xaa\xadX7gO\x91\xde\xa4m\x1bL\x95\xa9\xc8\x8c\x9d\x19\x8f\x85\xba\xf8.H\xb3G\xd9I[\xbd\xb9l\xe6\xd5\xb0\xa5Qc,\x8f\x81\x04\tF\xca\x0e\xd5\xa7\x8e\\;\xb6\x88\xab\x02\x08\x1a\xd5%\xad\xd8\xab\xd1E\xfd<\x0c\xb9\xb4i\xf5\xf4\x99\xb9M\xdd\xc1)\xe2"\xd7\xa9\xdb\xbe\xbd\x1c\xbd\xc61\x85\x87\xff\r\xa9Zs\xc8u\xab\xdfm\xe5\x18\xad\xbc8\xaa\x96\xa8K\xc0`\x9d*2\xee\xeb\xf6\xc9\xdb\xee\xaekR\x9bs\xed\xf3\x9az\xfb@\xb3Z8\x8d\x8d\xb6\x8f>\xabM\xe3\xceH\xfah\x12Q0\xb7q\xc0\x15=\xfb\xb5CT4\xfb\xa9\xf3\x9dg\xc2\x91\xb5\xe0j\xb3\x89\xa4Of%ND\xd5q\xd2\xa0\x03\x19x\xf0I@\xc1)I\x8d\x07\xcdv\xbf16YD\xc2$\'\xd5q\xd0]6Ty\xb3i\x04\x13Z\xca\xe8\x03\x86\x8c\xd1PUcD\xf3l\xc7\xceb@\tt\xd4T\xe8I#NK\xe4\xa4W\xd8>\xae\xa4\x87\x95V\x1b\xc5\'A\x05D\x85\xa4\x10O8\x19C\x8e:9^%\x10h\x11\x95\xb3Z\x7fW\x0e8\x12Sv\xb6(\xd2<<\xc8\'h\x13w]\x99\x1dwO\x85t\x9aT=J\x93\x0epz&\xb5O2\xaba#\xe8\xa5\x1526R\x87\xfc\xa5)\xe7p\xe0\t(fD\xfa`\xf3\x9c`\xd1\x94*\r-\x98\n:A(R\xe9\xfc\x14\x0fw\xdc=xWQV\x91\x95e\x7f!\xe9\x83\x8al\xe1\x11\xc9\x0eu\x16v$\x12\xa7on\xa7^X\x9f-\x04*\\\xe5=z\xd4<\x07B\xc6\x93\x81\xab\x1d%\x0fuhn8\xd2Q\xbc\xd1\xaa\x0ePW\xe9\xf4\xe4\xa2TQ*\r\x82\n\r\x08S\xbb\xacI\xb4\xedmhJ\xa5P2\xbd\xf1\xd7\xd2P"2\x05 V,\xaa\xd7\xe86G*\xd3(t(\x01J\xefU\xd3\xd2\xfa\x1b\xb9\xc4\xad\x15\x13\xba\x1a\xa9\x1b[\x8a"\x99*\xcd;\x85\xe5\x13\xa8\x04\xd6\xd1\xb4O0\xf8\x11GV\x80!\xde\xc4\x17W\xd4\x02;\x12\xbf\xfbz\x1a\x9d\x19\x14\x8c\xc7\x18\xbe\xf9\xf2\x8a$c\xd1\xe4\xcaYxX\xbd\xd8\xd2\x95"\xaaI&1\xd1\xf0U\x16w9\xb2T\x9aM1\xc1\xcc\xf0\x91\xcbd\xc4\x12\xcc8Y\xfd.\xd5\xe1\xc93VDD\xf7\x0c\x00\xca2_\xc6\x98\xd2@\x13\xad)\xcf\xa5!\xe6\xf4Cp\x0f\xf4\x17C\xce2DLBu\xc7\x1d\x10\x00;\r\n\r\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\r\n\r\n<html xmlns="http://www.w3.org/1999/xhtml">\r\n<head><title>\r\n\r\n</title></head>\r\n<body>\r\n    <form name="form1" method="post" action="IdentifyingCode.aspx" id="form1">\r\n<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwULLTE2MTY2ODcyMjlkZFfiPYjN3OgKVvDZbVcHWf6DAu0K0ActbKlAdWPUjHKM" />\r\n\r\n    <div>\r\n    \r\n    </div>\r\n    </form>\r\n</body>\r\n</html>\r\n'
        with open('.\\yzmcode.jpg', 'wb') as local:
            local.write(picture)
        self.image = wx.Image('.\\yzmcode.jpg', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.yzmButton = wx.BitmapButton(self.panel, -1, self.image, pos=(180, 114), size=(self.image.GetWidth(), self.image.GetHeight()))

        self.SavePasswordCkeckBox = wx.CheckBox(self.panel, -1, "保存密码", pos=(90, 155), size=wx.DefaultSize, name="IsSavePassword")
        self.SavePasswordCkeckBox.SetValue(self.conf.getboolean("Account", "SavePassword"))

        if self.conf.getboolean("Account", "SavePassword"):
            self.accountInput.SetValue(self.conf.get("Account", "ID"))
            self.passwordInput.SetValue(self.conf.get("Account", "PWD"))
            self.yzmcodeInput.SetFocus()

        sureButton = wx.Button(self.panel, -1, '登录', pos=(20, 185), size=(120, 40))
        sureButton.SetForegroundColour('white')
        sureButton.SetBackgroundColour(self.themeColor)

        cancleButton = wx.Button(self.panel, -1, '取消', pos=(160, 185), size=(120, 40))
        cancleButton.SetBackgroundColour('black')
        cancleButton.SetForegroundColour('#ffffff')

        self.Bind(wx.EVT_BUTTON, self.sureEvent, sureButton)
        self.Bind(wx.EVT_BUTTON, self.cancleEvent, cancleButton)
        self.Bind(wx.EVT_BUTTON, self.changeYZM, self.yzmButton)
        self.Bind(wx.EVT_TEXT_ENTER, self.sureEvent, self.yzmcodeInput)
        self.Bind(wx.EVT_CLOSE, self.cancleEvent)
        self.Centre()
        self.Show()

    def InitConnect(self):
        self.StatusBar.SetStatusText("正在尝试连接服务器(๑•̀ㅂ•́)و✧，请稍候...")
        trytime = 1
        while True:
            try:
                response = self.s.get(url_home)
                viewstate = re.findall(VIEWSTATE_pattern, response.text)[0]
                validation = re.findall(validation_pattern, response.text)[0]
                self.the_form['__VIEWSTATE'] = viewstate
                self.the_form['__EVENTVALIDATION'] = validation
                picture = self.s.get(image_url)
                with open('.\\yzmcode.jpg', 'wb') as local:
                    local.write(picture.content)
                newimage = wx.Image('.\\yzmcode.jpg', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
                self.yzmButton.SetBitmap(newimage)
                self.StatusBar.SetStatusText("连接服务器成功o(*￣▽￣*)ブ请登录！")
                self.Enable()
                break
            except Exception as e:
                if trytime > 3 and not self.conf.getboolean("Settings", "EndlessTryConnecting"):
                    self.StatusBar.SetStatusText("根本连不上啊，稍后再试吧(￣ε(#￣)☆╰╮o(￣皿￣///)")
                    time.sleep(1.5)
                    exit(0)
                self.StatusBar.SetStatusText("连接服务器失败┌(。Д。)┐，第{trytime}次努力重试中...".format(trytime=trytime))
                trytime += 1
                time.sleep(3.5)


    def sureEvent(self, event):
        self.the_form['_ctl0:txtusername'] = self.accountInput.GetValue()
        self.the_form['_ctl0:txtpassword'] = self.passwordInput.GetValue()
        self.the_form['_ctl0:txtyzm'] = self.yzmcodeInput.GetValue().upper()
        result = self.s.post(url_home, self.the_form)
        js = re.findall(js_pattern, result.text)
        sorry = re.findall(sorry_pattern, result.text)
        if len(js) > 0:
            wx.MessageDialog(self, js[0], "登录失败w(ﾟДﾟ)w", wx.OK).ShowModal()
            if js[0] == "你输入的验证码错误！":
                self.changeYZM(self)
        elif len(sorry) > 0:
            wx.MessageDialog(self, '教务网崩了(￣ε(#￣)☆╰╮o(￣皿￣///)，稍后再试吧', "登录失败w(ﾟДﾟ)w", wx.OK).ShowModal()
        else:
            wx.MessageDialog(self, "登录成功！", "登录成功o(￣▽￣)ｄ", wx.OK).ShowModal()
            self.saveConf()
            self.func_callBack(self.the_form['_ctl0:txtusername'])
            self.Destroy()

    def cancleEvent(self, event):
        self.saveConf()
        exit(0)

    def changeYZM(self, event):
        picture = self.s.get(image_url)
        with open('.\\yzmcode.jpg', 'wb') as local:
            local.write(picture.content)
        newimage = wx.Image('.\\yzmcode.jpg', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.yzmButton.SetBitmap(newimage)
        self.yzmcodeInput.SetValue("")

    def saveConf(self):
        self.conf.set("Account", "SavePassword", str(self.SavePasswordCkeckBox.GetValue()))
        if self.conf.getboolean("Account", "SavePassword"):
            self.conf.set("Account", "ID", self.accountInput.GetValue())
            self.conf.set("Account", "PWD", self.passwordInput.GetValue())
        fw = open('ReportHunter.conf', 'wb')
        pickle.dump(self.conf, fw)
        fw.close()
