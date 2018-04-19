from __future__ import division
import sys,os,select,glob
sys.path.append(os.getcwd())
import socket
import wx
import wx.stc
from threading import Thread,Lock
import struct
import signal
import subprocess
import time
import gevent
import par as parser
import io
import keyword
from wx.lib.pubsub import pub
ON_POSIX = 'posix' in sys.builtin_module_names
msg = \
	'M-SEARCH * HTTP/1.1\r\n' \
	'HOST:239.255.255.250:1800\r\n' \
	'ST:upnp:rootdevice\r\n' \
	'MX:2\r\n' \
	'MAN:"ssdp:discover"\r\n'
if wx.Platform == '__WXMSW__':
# for windows
    faces = \
    {
    'comic': 'Times New Roman',
    'sizeCode': 10,
    'sizeLn': 10,
    }
else:
    faces = \
    {
    'mono': 'Courier',
    'sizeCode': 10,
    'sizeLn': 10,
    }
class open_file(wx.Frame):
    def __init__(self,*args,**kw):
         super(open_file, self).__init__(*args, **kw)
         self.filename=''
         self.Init()
    def Init(self):

        splitter1=wx.SplitterWindow(self,-1, style=wx.SP_3D)
        pan=wx.Panel(splitter1)
        pan1=wx.Panel(splitter1)
        txt = wx.TextCtrl(pan)
        xt=wx.TextCtrl(pan1)
        splitter1.SplitVertically(pan,pan1,50)
        self.Show()
class make_module(wx.Frame):
     def __init__(self,text,*args,**kw):
         super(make_module, self).__init__(*args, **kw)
         self.text=text
         self.pan=wx.Panel(self)
         self.pan.SetBackgroundColour((42,42,42))
         vbox=wx.BoxSizer(wx.VERTICAL)
         hbox=wx.BoxSizer(wx.HORIZONTAL)
         self.text_search=wx.TextCtrl(self.pan)
         str1=wx.StaticText(self.pan,label='Module',pos=(25,20))
         str1.SetForegroundColour((255,255,255))
         hbox.Add(str1,0,wx.ALL,border=5)
         hbox.Add(self.text_search,1,wx.RIGHT|wx.EXPAND,border=5)
         vbox1=wx.BoxSizer(wx.VERTICAL)
         self.output=wx.TextCtrl(self.pan,value ="",style =wx.TE_MULTILINE)
         str2=wx.StaticText(self.pan,label='Description',pos=(25,40))
         str2.SetForegroundColour((255,255,255))
         vbox1.Add(str2,0,wx.EXPAND,border=5)
         vbox1.Add(self.output,1,wx.EXPAND,border=5)
         vbox2=wx.BoxSizer(wx.VERTICAL)
         str3=wx.StaticText(self.pan,label='Syntax',pos=(25,40))
         str3.SetForegroundColour((255,255,255))
         self.output1=wx.TextCtrl(self.pan,value ="",style =wx.TE_MULTILINE)
         self.output1.write(self.text)
         vbox2.Add(str3,0,wx.EXPAND,border=5)
         vbox2.Add(self.output1,1,wx.EXPAND,border=5)
         hbox1=wx.BoxSizer(wx.HORIZONTAL)
         btn1=wx.Button(self.pan, label='Close')
         btn2=wx.Button(self.pan, label='Save')
         vbox.Add(hbox,0,wx.EXPAND,border=5)
         vbox.Add(vbox1,1,wx.EXPAND,border=5)
         vbox.Add(vbox2,1,wx.EXPAND,border=5)
         btn1.Bind(wx.EVT_BUTTON,self.close)
         hbox1.Add(btn2,0,wx.EXPAND,border=5)
         hbox1.Add(btn1,0,wx.EXPAND,border=5)
         vbox.Add(hbox1,0,wx.ALL,border=5)
         btn2.Bind(wx.EVT_BUTTON,self.save)
         self.Bind(wx.EVT_CLOSE,self.close)
         self.pan.SetSizer(vbox)
         self.Center()
     def save(self,e):
         if len(self.text_search.GetLineText(0)):
             if self.serach_file(self.text_search.GetLineText(0)):
                 message=wx.MessageDialog(None,'Do You want to Overwrite', 'Info', wx.YES_NO | wx.ICON_INFORMATION)
                 i=message.ShowModal()
                 message.Destroy()
                 if i == wx.ID_YES:
                    parser.make_mfile(self.text_search.GetLineText(0),self.output.GetValue(),self.output1.GetValue())
                    self.Close(False)

             else:
                 #print "save file"
                 parser.make_mfile(self.text_search.GetLineText(0),self.output.GetValue(),self.output1.GetValue())
                 self.Close(False)
         else:
              message=wx.MessageDialog(None,'Module name is missing', 'Info', wx.OK | wx.ICON_INFORMATION)
              message.ShowModal()
              message.Destroy()
     def close(self,e):
        self.Show(False)
        self.Destroy()

     def serach_file(self,filename):
         if "Modules/"+filename+".xml" in glob.glob("Modules/"+filename+".xml"):
             return True
         else:
             return False
class api_ref(wx.Frame):
    def __init__(self,ap_ref,*args,**kw):
         super(api_ref, self).__init__(*args, **kw)
         self.api=ap_ref

         text,para,syn=parser.get_all(str(self.api))
         self.pan=wx.Panel(self)
         self.pan.SetBackgroundColour((42,42,42))
         vbox=wx.BoxSizer(wx.VERTICAL)
         self.output1=wx.TextCtrl(self.pan,value ="",style = wx.TE_READONLY| wx.TE_MULTILINE)
         self.output1.write("Information:")
         self.output1.write("\n")
         self.output1.write(text)
         self.output1.write("\n")
         self.output1.write("\n")
         if para:
             self.output1.write("Parameters:")
             self.output1.write("\n")
             self.output1.write("\n")
         for key,value in para.iteritems():
             if key != 'return':
               self.output1.write('\t')
               self.output1.write(key)
               self.output1.write(':-')
               self.output1.write(value)
               self.output1.write("\n")
         if para.has_key('return'):
             self.output1.write('\t')
             self.output1.write("return")
             self.output1.write(":-")
             self.output1.write(para['return'])
         self.output1.write("\n")
         self.output1.write("\n")
         self.output1.write("Syntax:")
         self.output1.write("\n")
         self.output1.write(syn)
         btn1=wx.Button(self.pan, label='Close')
         vbox.Add(self.output1,1,wx.EXPAND,border=5)
         vbox.Add(btn1,0,wx.ALL,border=5)

         btn1.Bind(wx.EVT_BUTTON,self.close)
         self.Bind(wx.EVT_CLOSE,self.close)
         self.pan.SetSizer(vbox)
         self.Center()
    def close(self,e):
        self.Show(False)
        self.Destroy()

class msearch():
    def __init__(self,*args, **kw):
        self.devices=[]
        self.dev_dict={}
        self.connected=0
        self.message="M-SEARCH * HTTP/1.1"
        self.UDP_IP = "239.255.255.250"
        self.UDP_PORT=1800
        self.sock=0
        self.thread=0
        self.connect_sock()
        self.up=0
        print("in msearch")
    def update_cb(self):
        raise NotImplementedError()
    def parse_mpac(self):
        self.sock.setblocking(0)
        while(self.thread):
            try:
                time.sleep(.1)
                data,addr=self.sock.recvfrom(4096)
                data=data.decode()
            except:
                pass
            else:
                port_no=0
                devicename=''
                ptr=data.find('PORT:')
                for i in range(ptr,len(data)):
                    if data[i] == '\r':
                      port_no=data[ptr+5:i]
                      break
                ptr=data.find('DeviceName:')
                for i in range(ptr,len(data)):
                    if data[i] == '\r':
                      devicename=data[ptr+11:i]
                      break
                self.dev_dict[devicename]=(addr[0],port_no)
                for i in self.devices:
                    if i == devicename:
                        break
                else:
                    self.devices.append(devicename)
                    #print self.devices
                    #if self.up:
                     #   self.update_cb()
                    wx.CallAfter(self.update_cb)
                        
            gevent.sleep()
        print("out of thread")
    def refresh_pac(self):
        print("send udp packet")
        for i in range(5):
            self.sock.sendto(self.message.encode(),(self.UDP_IP, self.UDP_PORT))#msg.encode()


    def connect_sock(self):
        
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM,socket.IPPROTO_UDP)
        hostname = socket.gethostname()
        IP = socket.gethostbyname(hostname)
        self.sock.bind(('',5051))
        #self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mreq = struct.pack("4sl", socket.inet_aton(self.UDP_IP), socket.INADDR_ANY)#+socket.inet_aton(IP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,mreq)
        
        self.thread=1
        self.thread1=Thread(target=self.parse_mpac)
        self.thread1.deamon=True
        self.thread1.start()
        for i in range(5):
            self.sock.sendto(self.message.encode(),(self.UDP_IP, self.UDP_PORT))


    def close_sock(self):
        #print "in close"
        self.thread=0
        time.sleep(.2)
        self.sock.close()

class TextDropTarget(wx.TextDropTarget):
      """ This object implements Drop Target functionality for Text """
      def __init__(self, obj):
         """ Initialize the Drop Target, passing in the Object Reference to
             indicate what should receive the dropped text """
         # Initialize the wx.TextDropTarget Object
         wx.TextDropTarget.__init__(self)
         # Store the Object Reference for dropped text
         self.obj = obj

      def OnDropText(self, x, y, data):
        """ Implement Text Drop """
        indent=self.obj.GetLineIndentation(self.obj.GetCurrentLine())
        text,para,syn=parser.get_all(data)
        for i in syn.split("\n"):
                i.replace("\n","")
                self.obj.AddText(i)
                self.obj.NewLine()
                for j in range(indent):
                    self.obj.AddTextRaw(" ")
        return True

class MyPopupMenu(wx.Menu):

    def __init__(self, parent,text):
        super(MyPopupMenu, self).__init__()
        self.text=text
        self.parent = parent

        mmi = wx.MenuItem(self, wx.NewId(), 'Make module')
        self.Append(mmi)
        self.Bind(wx.EVT_MENU, self.makemodule, mmi)





    def makemodule(self,e):
        win=make_module(self.text,None)
        win.Show(True)
        del win


class myframe(wx.Frame,msearch):
    def __init__(self,*args,**kw):
        super(myframe, self).__init__(*args, **kw)
        msearch.__init__(self,*args, **kw)
        self.present_char=32
        self.api_total=20
###        self.api_list=[]
        self.sug_list=parser.list_def()
        #print self.sug_list
###        for i in range(self.api_total):
###         self.api_list.append(wx.ListItem())
###     for i in range(len(self.sug_list)):
###         self.api_list[i].SetText(self.sug_list[i])
        self.Init()
        self.filename=''
        self.select_dev=''
        self.W=0
        self.H=0
        self.thread1=0
        self.word=""
        self.str1=''
        self.show()
        self.sug_list.sort()
        self.sug_list_str="".join(i+" " for i in self.sug_list)
    def update_cb(self):
        #print "i am here"
        self.cb.Clear()
        for i in self.devices:
            self.cb.Append(i)
    def outputthread(self):
        filep=open("output.txt",'r')
        while(self.thread1):
                    time.sleep(.1)
                    i=filep.readline()
                    if len(i):
                        wx.CallAfter(self.updateDisplay,i)
                        gevent.sleep()
                    try:
                        nextline = self.p.stderr.readline()
                        if nextline == '' and self.p.poll() is not None:
                                pass
                        else:
                              wx.CallAfter(self.updateDisplay,nextline )
                    except:
                        pass
        filep.close()
        self.threadkilled=0
        print("out of thread1")

    def Init(self):
        menu=wx.MenuBar()
        fileit1=wx.Menu()
        new_it=fileit1.Append(wx.ID_NEW,'&New','New File')
        open_it=fileit1.Append(wx.ID_OPEN,'&Open','Open File')
        save_it=fileit1.Append(wx.ID_SAVE,'&Save','Save File')
        quit_it=fileit1.Append(wx.ID_EXIT, '&Quit', 'Quit application')
        Font = wx.Font(12, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        Face = Font.GetFaceName()
        Size = Font.GetPointSize()
        menu.Append(fileit1,'&File')
	
        self.Bind(wx.EVT_MENU,self.Quit,quit_it)
        self.Bind(wx.EVT_MENU,self.New,new_it)
        self.Bind(wx.EVT_MENU,self.Open,open_it)
        self.Bind(wx.EVT_MENU,self.Save,save_it)
        self.Bind(wx.EVT_CLOSE,self.close)

        self.splitter1=wx.SplitterWindow(self,-1,size = (width, height),style=wx.SP_3D|wx.SP_BORDER)

        self.pan=wx.Panel(self.splitter1)
        self.pan1=wx.Panel(self.splitter1)
        self.pan.SetBackgroundColour((42,42,42))
        self.pan1.SetBackgroundColour((163,35,48))
        ## Panel 1 inputs##
        vbox = wx.BoxSizer(wx.VERTICAL)
##        btn1 = wx.Button(self.pan, label='Connect', size=(70, 30))
##        vbox.Add(btn1,flag=wx.LEFT, border=5)
        btn2 = wx.Button(self.pan, label='Refresh', size=(70, 30))
        vbox.Add(btn2, flag=wx.LEFT|wx.BOTTOM, border=5)


##        btn1.Bind(wx.EVT_BUTTON,self.connect)
        btn2.Bind(wx.EVT_BUTTON,self.refresh)
	
        hbox= wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(vbox)
        self.cb = wx.ComboBox(self.pan, pos=(50, 30),choices=self.devices,style=wx.CB_READONLY)
        self.cb.Bind(wx.EVT_COMBOBOX, self.OnSelect)
        hbox.Add(self.cb)

        vbox1= wx.BoxSizer(wx.VERTICAL)
        vbox1.Add(hbox,0,wx.LEFT|wx.TOP|wx.RIGHT,5)
        vbox2= wx.BoxSizer(wx.VERTICAL)


        hbox3=wx.BoxSizer(wx.HORIZONTAL)
        self.text_search=wx.TextCtrl(self.pan)
        str1=wx.StaticText(self.pan,label='Search',pos=(25,20))
        str1.SetForegroundColour((255,255,255))
        hbox3.Add(str1,0,wx.ALL,border=5)
        hbox3.Add(self.text_search,1,wx.RIGHT|wx.EXPAND,border=5)
        self.text_search.Bind(wx.EVT_TEXT,self.search)
        self.list_view=wx.ListCtrl(self.pan,style=wx.LC_REPORT)
        self.list_view.InsertColumn(0, 'API Refference',width=130)
        self.list_view.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.list_click)
        self.list_view.Bind(wx.EVT_LIST_BEGIN_DRAG,self.ondrag)
        for i in range(len(self.sug_list)):
            self.list_view.InsertItem(i, self.sug_list[i])

	
        vbox2.Add(hbox3,0,wx.EXPAND,border=5)
        vbox2.Add(self.list_view,1,wx.EXPAND,border=5)
        vbox1.Add(vbox2,1,wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND,15)
        self.pan.SetSizer(vbox1)
        self.sb = self.CreateStatusBar()
        vbox3 = wx.BoxSizer(wx.HORIZONTAL)
        btn3 = wx.Button(self.pan1,label='Run', size=(70, 30))
        vbox3.Add(btn3,1,wx.ALL,border=5)
        btn4 = wx.Button(self.pan1,label='Stop', size=(70, 30))
        vbox3.Add(btn4,1,wx.ALL,border=5)

        btn3.Bind(wx.EVT_BUTTON,self.run)
        btn4.Bind(wx.EVT_BUTTON,self.stop)


	
        hbox2=wx.BoxSizer(wx.VERTICAL)
        image = wx.Image('sirena.jpg', wx.BITMAP_TYPE_ANY)

        hbox4=wx.BoxSizer(wx.HORIZONTAL)

        out_text1=wx.StaticText(self.pan1, label='Code Below:', pos=(25, 80))
        imageBitmap = wx.StaticBitmap(self.pan1, wx.ID_ANY, wx.Bitmap(image))
        hbox4.Add(out_text1,1,flag=wx.ALIGN_LEFT|wx.ALIGN_TOP,border=5)
        image_pos=width*(880/1366)
        hbox4.Add((image_pos,1),0)
        hbox4.Add(imageBitmap,1,flag=wx.ALIGN_RIGHT|wx.EXPAND,border=5)
        out_text1.SetForegroundColour((255,255,255))
        self.output_text=wx.stc.StyledTextCtrl(self.pan1,style = wx.TE_MULTILINE)

        self.output_text.SetStyleBits(5)
        self.output_text.SetIndentationGuides(1)
        self.output_text.SetLexer(wx.stc.STC_LEX_PYTHON)
        self.output_text.StyleSetForeground(wx.stc.STC_P_DEFNAME,wx.Colour(0,0,255))
        self.output_text.StyleSetForeground(wx.stc.STC_P_CLASSNAME,wx.Colour(0,0,255))
        self.output_text.StyleSetForeground(wx.stc.STC_P_WORD,wx.Colour(255,128,0))
        self.output_text.StyleSetForeground(wx.stc.STC_P_STRING,wx.Colour(0,255,0))
        self.output_text.StyleSetForeground(wx.stc.STC_P_IDENTIFIER,wx.Colour(0,0,0))
        self.output_text.StyleSetForeground(wx.stc.STC_P_OPERATOR,wx.Colour(125,125,200))
        self.output_text.StyleSetForeground(wx.stc.STC_P_COMMENTBLOCK,wx.Colour(255,0,0))
        self.output_text.StyleSetForeground(wx.stc.STC_P_COMMENTLINE,wx.Colour(255,0,0))
        self.output_text.StyleSetForeground(wx.stc.STC_P_TRIPLE,wx.Colour(0,255,0))
        kwlist="".join(i+" " for i in keyword.kwlist)
        self.output_text.SetKeyWords(0,kwlist)




	
        out_text=wx.StaticText(self.pan1, label='OUTPUT:', pos=(65, 80))
        out_text.SetForegroundColour((255,255,255))
        self.output1=wx.TextCtrl(self.pan1,value ="",style = wx.TE_READONLY| wx.TE_MULTILINE)
        self.output_text.AutoCompSetIgnoreCase(False)
        self.output_text.Bind(wx.EVT_KEY_DOWN,self.getchar)
        self.output_text.Bind(wx.EVT_RIGHT_DOWN,self.drag)
        self.list_view.Bind(wx.EVT_LIST_COL_CLICK,self.ondrag)

##        hbox2.Add(out_text1,border=5)
        hbox2.Add(hbox4,0,wx.EXPAND|wx.ALIGN_RIGHT,border=5)
        hbox2.Add(self.output_text,1,wx.ALL|wx.EXPAND,border=15)
        hbox2.Add(vbox3,0,wx.ALL,border=5)

        dt1 = TextDropTarget(self.output_text)
        self.output_text.SetDropTarget(dt1)


        hbox2.Add(out_text)
        hbox2.Add(self.output1,1,wx.ALL|wx.EXPAND,border=15)
        self.i=10

        self.pan1.SetSizer(hbox2)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_list, self.timer)
        self.timer.Start(1000)
        self.splitter1.SplitVertically(self.pan,self.pan1, width * (300/1366))
        self.SetMenuBar(menu)
        self.Maximize()
        self.Center()
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.up=1
	
    def update_list(self,e):
               search_text=self.text_search.GetValue()
               self.sug_list=parser.list_def()
               if len(search_text):
                    list_pre=[]
                    list_ab=[]
                    for i in self.sug_list:
                            if i.find(search_text) == 0:
                                    list_pre.append(i)
                            else:
                                    list_ab.append(i)
                    list_pre.extend(list_ab)
                    self.list_view.ClearAll()
                    self.list_view.InsertColumn(0, 'API Refference',width=130)
                    amt=len(self.sug_list)-1
            
                    for i in range(len(self.sug_list)):
                            self.list_view.InsertItem(i, list_pre[i])
               else:
                    
                    self.list_view.ClearAll()
                    self.list_view.InsertColumn(0, 'API Refference',width=130)
                    amt=len(self.sug_list)-1
                    for i in range(len(self.sug_list)):
                        self.list_view.InsertItem(i, self.sug_list[i])
    def drag(self,e):

        text=self.output_text.GetSelectedText()
        self.output_text.PopupMenu(MyPopupMenu(self,text), e.GetPosition())

    def ondrag(self,e):
        idx=self.list_view.GetFocusedItem()
        tdo = wx.TextDataObject(self.list_view.GetItem(idx).GetText())
        tds = wx.DropSource(self.output_text)
        tds.SetData(tdo)
        tds.DoDragDrop(True)

    def updateDisplay(self,e):
        self.output1.write(e)
    def list_click(self,e):
        print(e.GetText())
        win=api_ref(e.GetText(),None)
        win.Show(True)
        del win
    def search(self,e):
        search_text=self.text_search.GetValue()
        list_pre=[]
        list_ab=[]
        for i in self.sug_list:
            if i.find(search_text) == 0:
                list_pre.append(i)
            else:
                list_ab.append(i)
        list_pre.extend(list_ab)
        self.list_view.ClearAll()
        self.list_view.InsertColumn(0, 'API Refference',width=130)
        amt=len(self.sug_list)-1
	
        for i in range(len(self.sug_list)):
            self.list_view.InsertItem(i, list_pre[i])

    def getchar(self,e):
        self.present_char=e.GetUnicodeKey()
        if self.present_char<256:
            if  chr(self.present_char).isalnum():
                   line_content,cur_pos=self.output_text.GetCurLine()
                   line_len=len(line_content)
                   self.str1=chr(self.present_char)
                   self.pos1=cur_pos
                   if cur_pos!=line_len:
                       for i in range(cur_pos-1,-1,-1):
                           if not line_content[i].isalnum():
                               self.pos1=i
                               break
                       else:
                           self.pos1=-1
                       if self.pos1 != cur_pos:
                           self.str1=line_content[self.pos1+1:cur_pos]+self.str1
                       self.pos2=cur_pos
                       for i in range(cur_pos,line_len):
                           if not line_content[i].isalnum():
                               self.pos2=i
                               break
                       if self.pos2-1 != cur_pos:
                             self.str1+=line_content[cur_pos:self.pos2]

                   else:
                       for i in range(cur_pos-1,-1,-1):
                           if not line_content[i].isalnum():
                               self.pos1=i
                               break
                       else:
                           self.pos1=-1
                       if self.pos1 != cur_pos:
                           self.str1=line_content[self.pos1+1:cur_pos]+self.str1
                       self.pos2=cur_pos
            else:
                self.str1=''

        else:
            self.str1=''


        if len(self.str1):

            list_pre=[]
            for i in self.sug_list:
               if i.lower().find(self.str1.lower()) == 0:
                        list_pre.append(i)
               if list_pre:
                    list_pre.sort()
                    self.sug_list_str=""
                    self.sug_list_str="".join(i+" " for i in list_pre)
                    self.output_text.AutoCompShow(len(self.str1)-1,self.sug_list_str)

        e.Skip()
    def show(self):
        self.Show()
        self.W,self.H = self.GetSize()
        print(self.W,self.H)
    def OnSelect(self,e):

        self.select_dev=e.GetString()
        ip,port=self.dev_dict[self.select_dev]
        if ip:
            parser.set_para('IP',ip)
        if port:
            parser.set_para('Port',port)
    def close(self,e):
        self.timer.Stop()
        self.close_sock()
        self.thread1=0
        time.sleep(.2)
        self.Destroy()

    def OnSize(self,e):
        w,h=self.GetSize()

    def Open(self,e):
        with wx.FileDialog(self, "Open python file", wildcard="python files (*.py)|*.py",style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            try:
                self.output_text.LoadFile(pathname)
            except:
                print( "open error file")
##        self.output_text.LoadFile("tmp.py")
    def New(self,e):
        print("in new file")
        self.output_text.Clear()
        self.output_text.SetText("##...start your python code")
    def Save(self,e):
        with wx.FileDialog(self, "Save file", wildcard="python files (*.py)|*.py",style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            try:
                self.output_text.SaveFile(pathname+".py")
            except:
                print ("save error file")
    def refresh(self,e):


        print("in refresh")
        self.refresh_pac()
    def run(self,e):
        print("in run")
        self.log=open("output.txt",'a')
        self.log.seek(0)
        self.log.truncate()
        self.log.seek(0)
        #print "starting subprocess"
        cmd = 'python tmp.py'

        self.output_text.SaveFile("tmp.py")
        self.output1.Clear()
        try:
            self.p = subprocess.Popen(cmd.split(),stdout=self.log,stderr=subprocess.PIPE, universal_newlines=True,shell=False)
        except:
            print("unable to create proc")
        if self.p:
            self.thread1=1
            try:
                threadoutput=Thread(target=self.outputthread)
                threadoutput.daemon=True
                threadoutput.start()
                self.threadkilled=1
            except:
                print("thread not created")
                self.thread1=0
        else:
            self.thread1=0
    def stop(self,e):

        if self.p:
            self.thread1=0

            try:
                os.kill(self.p.pid, signal.SIGTERM)
            except:
                print("could not kill")
                pass

            try:

                output,err = self.p.communicate()

                if output:

                    self.output1.write(output)

                if err:

                    self.output1.write(err)

                exitCode = self.p.returncode


            except:
                print("in exception stop")
                pass

            self.log.close()
        else:
            print("i am here")
            pass


    def Quit(self,e):
        message=wx.MessageDialog(None,'Do You want to Quit', 'Info',
            wx.YES_NO | wx.ICON_INFORMATION)
        i=message.ShowModal()

        if i == wx.ID_YES:
            self.timer.Stop()
            self.close_sock()
            self.thread1=0
            time.sleep(.2)
            self.Close()

        message.Destroy()

app=wx.App()
width, height = wx.GetDisplaySize()
#print width
myframe(None,-1,"Sirena Gui",pos=wx.DefaultPosition,size=(width, height))
app.MainLoop()
