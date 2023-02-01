import time
from flask import Flask, request
from datetime import datetime
import wx
import threading

app = Flask(__name__)

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
        super(MainFrame, self).__init__(parent, title=title, style=no_resize, size=(220, 100))
        self.InitUI()
        self.fone_thread()
        self.Center()

    def InitUI(self):
        self.count = 0
        pnl = wx.Panel(self)
        pnl.SetBackgroundColour("#45f542")
        self.login = wx.StaticText(pnl, label='Привет! Я сервер~ \nКак закончишь работу жми \nна "Х" чтобы закрыть меня'
                                   , size=(180, 50))
        #self.login.SetLabel('Привет! Я сервер~')
        hbox = wx.BoxSizer(wx.VERTICAL)
        hbox.Add(self.login, flag=wx.ALIGN_CENTRE | wx.RIGHT | wx.LEFT, border=20)
        pnl.SetSizer(hbox)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(pnl, 1, flag=wx.ALL)
        self.SetSizer(sizer)
        self.Show(True)

    def fone_thread(self):
        self.create_thread(self.run_ser)

    def create_thread(self, target):
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()

    def run_ser(self):
        servak()
        app.run()


def servak():

    messages = [
        {'username': 'Jack', 'time': time.time(), 'text': 'Hello'},
        {'username': 'Mary', 'time': time.time(), 'text': 'Hi, Jack'},
    ]
    users = {
        # username : password
        'Jack': 'Black',
        'Mary': '12345',
    }

    # Набор возможных смайлов
    smile = {
        # name : smile
        'oldjoke': '[:]|||[:]',
        'dunno': '¯\_(ツ)_/¯',
        'wow': '(о_О)',
        'nice': '(⌒‿⌒)',
        'happy': '╰(▔∀▔)╯',
        'fuck': '凸(￣ヘ￣)',
        'cry': '(ಥ﹏ಥ)',
        'panic': '..・ヾ(。＞＜)シ',
        '?': '(・・ ) ?',
        'dntknow': '┐(￣ヘ￣)┌',
        'scare': '( : ౦ ‸ ౦ : )',
        'hello': '( ° ∀ ° )ﾉﾞ',
        'hi': '(￣▽￣)ノ',
        'hugs': '(づ ◕‿◕ )づ',
        'wink': '(^_~)',
        'regards': '(シ_ _)シ',
        'sleep': '(￣ρ￣)..zzZZ',
        'wall': '┬┴┬┴┤(･_├┬┴┬┴',
        'writing': '__φ(．．;)',
        'bear': 'ʕ ᵔᴥᵔ ʔ',
        'pig': '(￣(00)￣)',
        'spider': r'╱╲//\\╭(ರರ⌓ರರ)╮//\\╱╲',
    }

    # Набор возможных тэгов для смайлов
    smile_tags = 'oldjoke, dunno, wow, nice, happy, fuck, cry, panic, ?, dntknow, scare, hello,' \
                 ' hi, hugs, wink, regards, sleep, wall, writing, bear, pig, spider'


    @app.route("/")
    def hello_view():
        return "Hello python messenger!"


    @app.route("/status")
    def status_view():
        return {
            'status': True,
            'number users': len(users),
            'number messages': len(messages),
            'time': datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        }


    @app.route("/messages")
    def messages_view():
        after = float(request.args['after'])

        filtered_messages = []
        for message in messages:
            if message['time'] > after:
                filtered_messages.append(message)

        return {'messages': filtered_messages}


    @app.route("/send", methods=['POST'])
    def send_view():
        """
        Send message to all users
        input: {"username": str, "password" : str, "text": str}
        :return: {"ok": bool}
        """
        print(request.json)
        username = request.json["username"]
        password = request.json["password"]
        text = request.json["text"]

        if username not in users or users[username] != password:
            return {"ok": False}

        if text[:2] == '--':
            # Если пользователь введет '--' то дальнейший текст будет принят как команда
            if text[2:] == 'help':
                # Если слово будет 'help', то он получит список возможных тэгов
                text = smile_tags
            elif text[2:] in smile:
                # Если слово это тэг, то текст будет заменен смайлом
                text = smile[text[2:]]
            messages.append({'username': username, 'time': time.time(), 'text': text})
        else:
            messages.append({'username': username, 'time': time.time(), 'text': text})

        return {'ok': True}


    @app.route("/login", methods=['POST'])
    def login_view():
        """
        Login to send message
        input: {"username": str, "password" : str}
        :return: {"ok": bool}
        """
        username = request.json["username"]
        password = request.json["password"]

        if username not in users:
            users[username] = password
            return {'ok': True}
        elif users[username] == password:
            return {'ok': True}
        else:
            return {'ok': False}


def main():
    onAp = wx.App()
    MainFrame(None, 'server')
    onAp.MainLoop()


if __name__ == '__main__':
    main()
    #app.run()

