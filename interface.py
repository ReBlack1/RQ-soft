# -*- coding: utf-8 -*-

import wx
import config
import soft_manager

class Setting_Frame(wx.Frame):
    def __init__(self, parent, title):
        super(Setting_Frame, self).__init__(parent, title=title, size=(400, 200), pos=(270, 150), style=wx.SYSTEM_MENU)
        if title=='Heal setting':
            print('Heal setting')
        self.sizer1 = wx.BoxSizer(wx.VERTICAL)

        self.exit_button = wx.BitmapButton(self, size=(30, 20), pos=(365, 0), bitmap=wx.Bitmap('icon_close.png'))
        self.sizer1.Add(self.exit_button)
        self.exit_button.Bind(wx.EVT_BUTTON, self.exit_click)

    def show(self):
        self.Show()
    def exit_click(self, e):
        self.Destroy()
        config.HEAL_SETTING_OPENED = False


class RoyalMain(wx.Frame):

    def __init__(self, parent, title):
        super(RoyalMain, self).__init__(parent, title=title, size=(120, 200),pos=(150,150) ,style=wx.SYSTEM_MENU)

        self.sizer1 = wx.BoxSizer(wx.VERTICAL)
        self.exit_button = wx.BitmapButton(self, size=(30, 20), pos=(85, 0), bitmap=wx.Bitmap('icon_close.png'))
        self.sizer1.Add(self.exit_button)
        self.exit_button.Bind(wx.EVT_BUTTON, self.exit_click)

        self.avto_heal = wx.BitmapButton(self, size=(80, 30), pos=(5, 40), bitmap=wx.Bitmap('BlackHP.png'))
        self.heal_setting = wx.BitmapButton(self, size=(24, 24), pos=(88, 43), bitmap=wx.Bitmap('setting.png'))
        self.avto_farm = wx.BitmapButton(self, size=(80, 30), pos=(5, 80), bitmap=wx.Bitmap('icon_close.png'))
        self.farm_setting = wx.BitmapButton(self, size=(24, 24), pos=(88, 83), bitmap=wx.Bitmap('setting.png'))
        self.zoom = wx.BitmapButton(self, size=(80, 30), pos=(5, 120), bitmap=wx.Bitmap('icon_close.png'))
        self.zoom_setting = wx.BitmapButton(self, size=(24, 24), pos=(88, 123), bitmap=wx.Bitmap('setting.png'))

        self.sizer1.Add(self.avto_heal)
        self.sizer1.Add(self.heal_setting)
        self.sizer1.Add(self.avto_farm)
        self.sizer1.Add(self.farm_setting)
        self.sizer1.Add(self.zoom)
        self.sizer1.Add(self.zoom_setting)


        self.avto_heal.Bind(wx.EVT_BUTTON, self.auto_heal_click)
        self.heal_setting.Bind(wx.EVT_BUTTON, self.heal_setting_click)


        self.Show()

    def exit_click(self, e):
        self.Destroy()

    def auto_heal_click(self, e):
        if not(config.HEAL_FLAG):
            self.avto_heal.Bitmap = wx.Bitmap('RedHP.png')
            config.HEAL_FLAG = True
            #Запуск потока на лечение
        else:
            self.avto_heal.Bitmap = wx.Bitmap('BlackHP.png')
            config.HEAL_FLAG = False

    def heal_setting_click(self, e):
        set_frame = Setting_Frame(self, title='Heal setting')
        if not(config.HEAL_SETTING_OPENED):
            set_frame.show()
            config.HEAL_SETTING_OPENED = True
        #else:
        #    set_frame.close()
         #   config.HEAL_SETTING_OPENED = False




if __name__ == '__main__':
    app = wx.App()
    RoyalMain(None, title='Royal Bot')
    app.MainLoop()
