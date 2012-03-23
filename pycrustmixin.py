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
        '''
        @nocreatemenu: if True, not create menu bar
        @menuBar: wx.Menu instance
        @kwargs: k1=v1, k2=v2, ...  set pycrust object
        '''
        if 'nocreatemenu' in kwargs: return
        self.kwargs = kwargs
        menuDebug = wx.Menu()
        itemCrust = menuDebug.Append(-1, "Show PyCrustFrame",
                    "Show PyCrustFrame window")
        self.Bind(wx.EVT_MENU, self.OnItemCrust, itemCrust)
        itemInspection = menuDebug.Append(-1, "Show Widget Inspection Tool",
                    "Show Widget Inspection Frame window")
        self.Bind(wx.EVT_MENU, self.OnItemInspection, itemInspection)
        if not isinstance(menuBar, wx.MenuBar):
            menuBar = self.GetMenuBar()
            if not menuBar:
                menuBar = wx.MenuBar()
                self.SetMenuBar(menuBar)
        menuBar.Append(menuDebug, "Debug")

    @classmethod
    def ShowCrustFrameNowx(cls, title=''):
        import threading
        def wxapp():
            global app
            app = wx.PySimpleApp(0)
            cls(nocreatemenu=1).OnItemCrust(None, None, title)
            app.MainLoop()
        t = threading.Thread(target=wxapp)
        t.daemon = True
        t.start()

    @classmethod
    def ShowCrustFrame(cls, title=''):
        cls(nocreatemenu=1).OnItemCrust(None, wx.GetApp().GetTopWindow(), title)

    def OnItemInspection(self, event):
        import wx.lib.inspection
        wx.lib.inspection.InspectionTool().Show()

    def OnItemCrust(self, event, mainwin='', title=''):
        import wx.py.crust
        if not isinstance(mainwin, wx.Window):
            if isinstance(self, wx.Window): mainwin = self
            else: mainwin = None
        if not hasattr(self, 'kwargs'): self.kwargs = {}
        if not title:
            if not hasattr(self, 'wcount'): self.wcount = 0
            self.wcount += 1
            title = 'PyCrust Debug Window :%d' % self.wcount
        frame = wx.py.crust.CrustFrame(parent=mainwin, title=title)
        frame.Show()

        frame.shell.interp.locals['app'] = wx.GetApp()
        frame.shell.interp.locals['self'] = mainwin
        frame.shell.interp.locals['crust'] = frame
        msg = []
        for k, v in self.kwargs.items():
            frame.shell.interp.locals[str(k)] = v
            msg.append(u'%s: %s' % (
                unicode(str(k), 'utf-8', errors='replace'),
                unicode(str(v), 'utf-8', errors='replace')
            ))

        notebook = frame.shell.interp.locals['notebook']
        notebook.SetSelection(2)
        calltip = notebook.GetPage(2)
        calltip.AppendText(
            "\n Globals() show in Namespace page\n"
            "\n---- Set Vars ----\n\n"
            "app:   wx.GetApp()\n"
            "self:  wx.GetApp().GetTopWindow()\n"
            "crust: PyCrustFrameWindow\n"
            "\n"
            + '\n'.join(msg) +
            "\n\n---- Howto Show Widget Inspection Tool ----\n\n"
            "import wx.lib.inspection\n"
            "wx.lib.inspection.InspectionTool().Show()\n"
        )
        calltip.SetInsertionPoint(0)


#from pycrustmixin import PycrustMixin
if __name__ == '__main__':
    if set(sys.argv).intersection(['--wx1', '--wx2', '--wx3']):
        class Demo1(wx.Frame, PycrustMixin):    ## demo 1 todo 1
            def __init__(self):
                wx.Frame.__init__(self, None, title='PycrustMixin Demo 1')
                PycrustMixin.__init__(self)     ## demo 1 todo 2
        class Demo2(wx.Frame):
            def __init__(self):
                wx.Frame.__init__(self, None, title='PycrustMixin Demo 2')
                self.__class__.__bases__ += (PycrustMixin,) ## demo 2 todo 1
                PycrustMixin.__init__(self)                 ## demo 2 todo 2
        class Demo3(wx.Frame):
            def __init__(self):
                wx.Frame.__init__(self, None, title='PycrustMixin Demo 2')
                PycrustMixin.ShowCrustFrame()   ## demo 3 todo
        if '--wx1' in sys.argv:     Demo = Demo1
        elif '--wx2' in sys.argv:   Demo = Demo2
        elif '--wx3' in sys.argv:   Demo = Demo3
        app = wx.PySimpleApp()
        mainwin = Demo()
        app.SetTopWindow(mainwin)
        mainwin.Show()
        app.MainLoop()
    elif '--nowx' in sys.argv:
        PycrustMixin.ShowCrustFrameNowx('Input G.exit=True exit')   ## demo 4 todo

        print 'Debug no wx program.  On PycrustFrame set G.exit=True exit\n'
        import time
        class G:
            exit = False
        t0 = time.time()
        while not G.exit:
            print '%s running: %d sec' % ('\b' * 80, time.time() - t0),
            time.sleep(1)
        print '\n\nExit on PycrustFrame set G.exit=True\n'
    else:
        print '''parameter:
        --wx1    add menu item to mainframe
        --wx2    add menu item to mainframe
        --wx3    show crustframe immediate
        --nowx   debug no wx program
        '''
