import wx

def ask(message):
    dlg = wx.TextEntryDialog(None, message, "")
    dlg.ShowModal()
    result = dlg.GetValue()
    dlg.Destroy()
    return result

class Dialog(wx.Dialog):
    def __init__(self, parent, id, title, btn_list):
        self.result = btn_list[0]
        wx.Dialog.__init__(self, parent, id, title)
        panel = wx.Panel(self, wx.ID_ANY)
        v_layout = wx.BoxSizer(wx.VERTICAL)
        staticText = wx.StaticText(panel, wx.ID_ANY, "画像サイズを選択して[閉じる]ボタンを押してください")
        v_layout.Add(staticText)
        button = []
        for i, btn_name in enumerate(btn_list):
           button.append(wx.Button(panel,wx.ID_ANY, btn_name))
           button[i].myname = btn_list[i]
           v_layout.Add(button[i])
           button[i].Bind(wx.EVT_BUTTON, self.OnButtonClick)
        panel.SetSizer(v_layout)

    def OnButtonClick(self, event):
        self.result = event.GetEventObject().myname
        print("ボタンが押されました" + str(self.result))
        self.Destroy()

def get_image_style():
    style_list = ["full", "real_size", "width=300px", "width=100px", "height=300px", "height=500px"]
    dialog = Dialog(None, wx.ID_ANY, "Select Image Display Type" ,style_list)
    dialog.ShowModal()
    result = dialog.result
    return result
