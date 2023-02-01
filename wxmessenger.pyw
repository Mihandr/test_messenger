

# ==================<Имортирование необходимых модулей>=================
import wx
from wx import html
from pubsub import pub
import requests
import threading
from datetime import datetime
from time import sleep
# ==================</Имортирование необходимых модулей>=================

DIR_TO_SAVE = "Pictures"
NAME_FILE = "Test"
FLAG_PASS = False


class TransparentText(wx.StaticText):
    def __init__(self, parent, id=wx.ID_ANY, label='', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.TRANSPARENT_WINDOW, name='transparenttext'):
        wx.StaticText.__init__(self, parent, id, label, pos, size, style, name)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda event: None)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_paint(self, event):
        bdc = wx.PaintDC(self)
        dc = wx.GCDC(bdc)

        font_face = self.GetFont()
        font_color = self.GetForegroundColour()

        dc.SetFont(font_face)
        dc.SetTextForeground(font_color)
        dc.DrawText(self.GetLabel(), 0, 0)

    def on_size(self, event):
        self.Refresh()
        event.Skip()

class MainFrame(wx.Frame):

    def __init__(self, parent, title):
        no_resize = wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        super(MainFrame, self).__init__(parent, title=title, style=no_resize, size=(500, 850))
        self.InitUI()
        self.Center()
        self.fone_thread()

    def InitUI(self):
        self.count = 0
        pnl = wx.Panel(self)
        pnl.SetBackgroundColour("#8C86AA")

        self.login = wx.TextCtrl(pnl, size=(200, 22))
        self.login.SetLabel('Логин')
        self.parol = wx.TextCtrl(pnl, size=(200, 22))
        self.parol.SetLabel('Пароль')
        self.btn1 = wx.Button(pnl, label="Зарегестрироваться")
        self.Bind(wx.EVT_BUTTON, self.registration, self.btn1)
        self.messText = wx.TextCtrl(pnl, size=(470, 470),
                                    style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.TE_RICH)
        self.inputText = wx.TextCtrl(pnl, size=(470, 150), style=wx.TE_MULTILINE | wx.HSCROLL | wx.TE_RICH)

        self.btn2 = wx.Button(pnl, label="Отправить")
        self.Bind(wx.EVT_BUTTON, self.send, self.btn2)

        vbox = self.layout()

        pnl.SetSizer(vbox)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(pnl, 1, flag=wx.ALL)
        self.SetSizer(sizer)
        self.Show(True)

    def layout(self):
        # Создание коробок для разметки
        staticbox1 = wx.StaticBox(self, -1, label="Регистрация")
        staticbox1.SetBackgroundColour("#8C86AA")

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.VERTICAL)

        hbox1_static = wx.StaticBoxSizer(staticbox1, wx.HORIZONTAL)

        hbox2 = wx.BoxSizer(wx.VERTICAL)
        hbox3 = wx.BoxSizer(wx.VERTICAL)

        # Создание самой разметки
        hbox2.Add(self.login, flag=wx.ALIGN_CENTRE | wx.BOTTOM, border=5)
        hbox2.Add(self.parol, flag=wx.ALIGN_CENTRE)
        hbox1_static.Add(hbox2, flag=wx.ALIGN_CENTRE | wx.RIGHT, border=10)
        hbox1_static.Add(self.btn1, flag=wx.ALIGN_CENTRE)

        hbox3.Add(hbox1_static, flag=wx.ALIGN_CENTRE | wx.BOTTOM, border=10)
        hbox3.Add(self.messText, flag=wx.RIGHT | wx.LEFT | wx.CENTRE, border=10)
        hbox3.Add((0, 10))
        hbox3.Add(self.inputText, flag=wx.RIGHT | wx.LEFT | wx.CENTRE, border=10)
        hbox3.Add(self.btn2, flag=wx.ALIGN_CENTRE | wx.UP, border=10)

        hbox.Add(hbox3, proportion=1, flag=wx.ALIGN_CENTRE)

        vbox.Add((0, 30))
        vbox.Add(hbox, flag=wx.ALIGN_CENTRE)

        return vbox

    def registration(self, e):
        username = self.login.GetValue()
        password = self.parol.GetValue()
        response = requests.post('http://127.0.0.1:5000/login', json={
            'username': username,
            'password': password
        })
        print(response.text)

    def send(self, e):
        text = self.inputText.GetValue()
        username = self.login.GetValue()
        password = self.parol.GetValue()
        print(username, text, password)
        response = requests.post('http://127.0.0.1:5000/send', json={
            'username': username,
            'password': password,
            'text': text
        })

    def fone_thread(self):
        self.create_thread(self.refresh)

    def create_thread(self, target):
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()

    def refresh(self):
        last_time = 0

        while True:
            try:
                response = requests.get('http://127.0.0.1:5000/messages', params={'after': last_time})
            except:
                print('ERROR')
                sleep(1)
                continue

            for message in response.json()['messages']:
                time_formated = datetime.fromtimestamp(message['time'])
                time_formated = time_formated.strftime('%d-%m-%Y %H:%M:%S')
                header = message['username'] + ' в ' + time_formated
                self.messText.AppendText(header + "\n")
                self.messText.AppendText(">> " + message['text'] + "\n")

                last_time = message['time']

            sleep(1)


def main():
    onAp = wx.App()
    MainFrame(None, 'messenger')
    onAp.MainLoop()


if __name__ == "__main__":
    main()
"""

# coding: utf-8
import wx
import random


class MyPanel(wx.Panel):

   def __init__(self, parent):
       wx.Panel.__init__(self, parent)
        # десь мы будем хранить все сообщения
       self.cache_msg = list()
       self.logText = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL | wx.TE_RICH)

       btn = wx.Button(self, label="Press Me")
       btn.Bind(wx.EVT_BUTTON, self.onPress)
       # чебокс
       self.check_box_invert = wx.CheckBox(self, wx.ID_ANY, 'Invert log', wx.DefaultPosition, wx.DefaultSize, 0)

       sizer = wx.BoxSizer(wx.VERTICAL)
       # горизонтальный сайзер в который мы поместим кнопку и чекбокс, что бы они были рядом
       hor_sizer = wx.BoxSizer(wx.HORIZONTAL)
       sizer.Add(self.logText, 1, wx.EXPAND | wx.ALL, 5)
       hor_sizer.Add(btn, 0, wx.ALL, 5)
       hor_sizer.Add(self.check_box_invert, 0, wx.ALL, 5)
       sizer.Add(hor_sizer, 0, wx.ALL, 5)
       self.SetSizer(sizer)

   def onPress(self, event):

       random_list = ['ERROR: this is error\n', 'INFO: start program\n', 'DEBUG: debug info for developer\n']
       self.outputPrint(random.choice(random_list))

   def outputPrint(self, message):
       # сохраним наше сообщение в списке
        self.cache_msg.append(message)
       # очистим окно от старых сообщений
        self.logText.Clear()
       # в зависимости от состояния флажка обном сообщения в окне
        # если флажок устновлен, то инвертируме лог (последнее сообщение будет вверху)
        if self.check_box_invert.IsChecked():
           for msg in reversed(self.cache_msg):
               # определим цвет сообщения
                color = self.outputColored(str(msg))
               # добавим его в окно
                self.logText.AppendText(msg)
               # окрасим вывод
                self.logText.SetForegroundColour(color)
           # перемещаем курсор в верхнее положение, иначе пользователь будет видеть нижнее сообщение
            # используем только если инвертировать лог включено
           self.logText.SetInsertionPoint(0)
        else:
            for msg in self.cache_msg:
               color = self.outputColored(str(msg))
               self.logText.AppendText(msg)
               self.logText.SetForegroundColour(color)

   @staticmethod
   # метод определяет цвет вывод
   def outputColored(message):
       return wx.RED if message.split()[0] == 'ERROR:' else wx.BLACK


class MyFrame(wx.Frame):
   def __init__(self):

       wx.Frame.__init__(self, None, title="Logging test")
       panel = MyPanel(self)
       self.Show()


def main():
   app = wx.App(False)
   frame = MyFrame()
   app.MainLoop()


if __name__ == "__main__":
   main()
"""