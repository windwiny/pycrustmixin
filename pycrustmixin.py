#!/usr/bin/env python
# coding: utf-8
#
# 2012 windwiny
# add a pycrustframe, debug program, usage:
#  MainFrame inherit PycrustMixin class and call __init__ create a menu or
#  call PycrustMixin.ShowCrustFrame() create pycrustframe immediate or
#  call PycrustMixin.ShowCrustFrameNowx() debug no base wx program
#

import sys
import wx

class PycrustMixin():
    def __init__(self, menuBar=None, **kwargs):
        if 'nocreatemenu' in kwargs: return
        self.kwargs = kwargs
        menuDebug = wx.Menu()
        itemCrust = menuDebug.Append(-1, "Show PyCrustFrame",
                    "Show PyCrustFrame window")
        self.Bind(wx.EVT_MENU, self.OnItemCrust, itemCrust)
        if not isinstance(menuBar, wx.MenuBar):
            menuBar = self.GetMenuBar()
            if not menuBar:
                menuBar = wx.MenuBar()
                self.SetMenuBar(menuBar)
        menuBar.Append(menuDebug, "Debug")

    @classmethod
    def ShowCrustFrameNowx(cls):
        import threading
        def wxapp():
            global app
            app = wx.PySimpleApp(0)
            cls(nocreatemenu=1).OnItemCrust(None, None)
            app.MainLoop()
        t = threading.Thread(target=wxapp)
        t.daemon = True
        t.start()

    @classmethod
    def ShowCrustFrame(cls):
        cls(nocreatemenu=1).OnItemCrust(None, wx.GetApp().GetTopWindow())

    def OnItemCrust(self, event, mainwin=''):
        from wx.py.crust import CrustFrame
        if not isinstance(mainwin, wx.Window):
            if isinstance(self, wx.Window): mainwin = self
            else: mainwin = None
        if not hasattr(self, 'wcount'): self.wcount = 0
        if not hasattr(self, 'kwargs'): self.kwargs = {}
        self.wcount += 1
        frame = CrustFrame(parent=mainwin,
                title='PyCrust Debug Window :%d' % self.wcount)
        frame.Show()

        frame.shell.interp.locals['app'] = wx.GetApp()
        frame.shell.interp.locals['self'] = mainwin
        frame.shell.interp.locals['crust'] = frame
        for k, v in self.kwargs.items():
            frame.shell.interp.locals[str(k)] = v

        notebook = frame.shell.interp.locals['notebook']
        notebook.SetSelection(2)
        notebook.GetPage(2).AppendText(
            "\n ---- Set Vars ----\n\n"
            "app:   wx.GetApp()\n"
            "self:  wx.GetApp().GetTopWindow()\n"
            "crust: PyCrustFrameWindow\n"
            "\n"
            + unicode(str(self.kwargs), errors='replace')
        )


#from pycrustmixin import PycrustMixin
if __name__ == '__main__':
    if '--wx1' in sys.argv or '--wx2' in sys.argv:
        class Demo1(wx.Frame, PycrustMixin):    # demo 1 todo 1
            def __init__(self):
                wx.Frame.__init__(self, None, title='PycrustMixin Demo 1')
                PycrustMixin.__init__(self)     # demo 1 todo 2
        class Demo2(wx.Frame):
            def __init__(self):
                wx.Frame.__init__(self, None, title='PycrustMixin Demo 2')
                PycrustMixin.ShowCrustFrame()   # demo 2 todo
        if '--wx2' in sys.argv:
            Demo1 = Demo2
        app = wx.PySimpleApp()
        mainwin = Demo1()
        app.SetTopWindow(mainwin)
        mainwin.Show()
        app.MainLoop()
    elif '--nowx' in sys.argv:
        PycrustMixin.ShowCrustFrameNowx()       # demo 3 todo

        print 'Debug no wx program.  On PycrustFrame set G.exit=True exit\n'
        import time
        class G2:
            exit = False
        global G
        G = G2
        t0 = time.time()
        while not G.exit:
            print '%s running: %d sec' % ('\b' * 80, time.time() - t0),
            time.sleep(1)
        print '\n\nExit on PycrustFrame set G.exit=True\n'
    else:
        print '''parameter:
        --wx1    add menu item to mainframe
        --wx2    show crustframe immediate
        --nowx   debug no wx program
        '''