import sys,os,select
import socket
import wx
import wx.stc 
from threading import Thread,Lock
import struct
import signal
import subprocess
import time
import gevent
import parser
import io
import re
from wx.lib.pubsub import Publisher
ON_POSIX = 'posix' in sys.builtin_module_names
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

class api_ref(wx.Frame):
    def __init__(self,ap_ref,*args,**kw):
         super(api_ref, self).__init__(*args, **kw)
         self.api=ap_ref
         text,para=parser.get_all(self.api)
         self.pan=wx.Panel(self)
         pos_w=80
         wx.StaticText(self.pan,label=text,pos=(25,pos_w))
         for key,value in para.iteritems():
             if key != 'return':
                 pos_w+=20
                 wx.StaticText(self.pan,label=key,pos=(25,pos_w))
                 wx.StaticText(self.pan, label=value,pos=(140,pos_w))
         if para.has_key('return'):
            pos_w+=20
            wx.StaticText(self.pan,label='return',pos=(25,pos_w))
            wx.StaticText(self.pan, label=para['return'],pos=(140,pos_w))
         btn1=wx.Button(self.pan, label='Close', pos=(140, pos_w+30))
         btn1.Bind(wx.EVT_BUTTON,self.close)
         self.Bind(wx.EVT_CLOSE,self.close)
         self.Center()
    def close(self,e):
        self.Show(False)
         
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
                gevent.sleep(.1)
                data,addr=self.sock.recvfrom(256)
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
                    if self.up:
                        self.update_cb()
            gevent.sleep()
        print("out of thread")
    def refresh_pac(self):
        print("send udp packet")
        for i in range(5):
            self.sock.sendto(self.message,(self.UDP_IP, self.UDP_PORT))
        
        
    def connect_sock(self):
        self.sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('',5051))
        mreq = struct.pack("4sl", socket.inet_aton(self.UDP_IP), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.thread=1
        self.thread1=Thread(target=self.parse_mpac)
        self.thread1.deamon=False
        self.thread1.start()
        for i in range(5):
            self.sock.sendto(self.message,(self.UDP_IP, self.UDP_PORT))
        
        
    def close_sock(self):
        self.thread=0
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
        text,para=parser.get_all(data)
        for i in text.split("\n"):
                i.replace("\n","")
                self.obj.AddText(i)
                self.obj.NewLine()
                for j in range(indent):
                    self.obj.AddTextRaw(" ")
                

class myframe(wx.Frame,msearch):
    def __init__(self,*args,**kw):
        super(myframe, self).__init__(*args, **kw)
        msearch.__init__(self,*args, **kw)
        self.dot=46
        self.sug_start=0
        self.back_dot=0
        self.prev_char=0
        self.present_char=32
        self.api_total=20
        self.api_list=[]
        self.sug_list=parser.list_def()
        for i in range(self.api_total):
            self.api_list.append(wx.ListItem())
        for i in range(len(self.sug_list)):
            self.api_list[i].SetText(self.sug_list[i])
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

        menu.Append(fileit1,'&File')
        
        self.Bind(wx.EVT_MENU,self.Quit,quit_it)
        self.Bind(wx.EVT_MENU,self.New,new_it)
        self.Bind(wx.EVT_MENU,self.Open,open_it)
        self.Bind(wx.EVT_MENU,self.Save,save_it)
        self.Bind(wx.EVT_CLOSE,self.close)

        self.splitter1=wx.SplitterWindow(self,-1,style=wx.SP_3D|wx.SP_BORDER)
        
        self.pan=wx.Panel(self.splitter1)
        self.pan1=wx.Panel(self.splitter1)
        self.pan.SetBackgroundColour((255,0,0))
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
        self.text_search=wx.TextCtrl(self.pan,size=(-1,1))
        str1=wx.StaticText(self.pan,label='Search',pos=(25,20))
        hbox3.Add(str1,0,wx.ALL,border=5)
        hbox3.Add(self.text_search,1,wx.RIGHT|wx.EXPAND,border=5)
        self.text_search.Bind(wx.EVT_TEXT,self.search)
        self.list_view=wx.ListCtrl(self.pan,size=(-1,1),style=wx.LC_REPORT)
        self.list_view.InsertColumn(0, 'API Refference',width=130)
        self.list_view.Bind(wx.EVT_LIST_ITEM_ACTIVATED,self.list_click)
        self.list_view.Bind(wx.EVT_LIST_BEGIN_DRAG,self.ondrag)
        for i in range(len(self.sug_list)):
            self.list_view.InsertItem(self.api_list[i])

       
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
        
        out_text1=wx.StaticText(self.pan1, label='Code Below:', pos=(25, 80))
        self.output_text=wx.stc.StyledTextCtrl(self.pan1,size=(-1,1),style = wx.TE_MULTILINE)
        self.output_text.SetIndentationGuides(1)
        out_text=wx.StaticText(self.pan1, label='OUTPUT:', pos=(65, 80))
        self.output1=wx.TextCtrl(self.pan1,value ="",size=(-1,1),style = wx.TE_READONLY| wx.TE_MULTILINE)
        self.output_text.AutoCompSetIgnoreCase(False)
        self.output_text.Bind(wx.EVT_KEY_DOWN,self.getchar)

        self.list_view.Bind(wx.EVT_LIST_COL_CLICK,self.ondrag)

        hbox2.Add(out_text1,border=5)
        hbox2.Add(self.output_text,1,wx.ALL|wx.EXPAND,border=15)
        hbox2.Add(vbox3,0,wx.ALL,border=5)

        dt1 = TextDropTarget(self.output_text)
        self.output_text.SetDropTarget(dt1)
        
        
        hbox2.Add(out_text)
        hbox2.Add(self.output1,1,wx.ALL|wx.EXPAND,border=15)
        
        
        self.pan1.SetSizer(hbox2)
        
        
        self.splitter1.SplitVertically(self.pan,self.pan1,300)
        self.SetMenuBar(menu)
        self.Maximize()
        self.Center()
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.up=1
 
        
    def ondrag(self,e):
        idx=self.list_view.GetFocusedItem()
        tdo = wx.PyTextDataObject(self.list_view.GetItem(idx).GetText())
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
            self.api_list[i].SetText(list_pre[amt-i])
            self.list_view.InsertItem(self.api_list[i])
        
    def getchar(self,e):
        
        self.prev_char=self.present_char
        self.present_char=e.GetUnicodeKey()
        
        if self.present_char<256:
            if  chr(self.present_char).isalnum():
                   line_content,cur_pos=self.output_text.GetCurLine()
                   line_len=len(line_content)
                   self.str1=chr(self.present_char)
                   pos1=cur_pos
                   if cur_pos!=line_len:
                       for i in range(cur_pos-1,-1,-1):
                           if not line_content[i].isalnum():
                               pos1=i
                               break
                       else:
                           pos1=-1
                       if pos1 != cur_pos:     
                           self.str1=line_content[pos1+1:cur_pos]+self.str1
                       pos2=cur_pos
                       for i in range(cur_pos,line_len):
                           if not line_content[i].isalnum():
                               pos2=i
                               break
                       if pos2-1 != cur_pos:
                             self.str1+=line_content[cur_pos:pos2]
                        
                   else:
                       for i in range(cur_pos-1,-1,-1):
                           if not line_content[i].isalnum():
                               pos1=i
                               break
                       else:
                           pos1=-1
                       if pos1 != cur_pos:     
                           self.str1=line_content[pos1+1:cur_pos]+self.str1
                       self.pos2=cur_pos
            else:
                self.str1=''
            
        else:
            self.str1=''
        if self.pos2:    
            self.output_text.SetSelection(self.pos1+1,self.pos2)    
        if len(self.str1):
            list_pre=[]
            for i in self.sug_list:
                 if i.lower().find(self.str1.lower()) == 0:
                        list_pre.append(i)
            list_pre.sort()
            self.sug_list_str=""
            self.sug_list_str="".join(i+" " for i in list_pre)
            print self.sug_list_str
            self.output_text.AutoCompShow(len(self.str1)-1,self.sug_list_str)
##        if self.sug_start==1 and self.present_char==self.dot and chr(self.present_char).isalnum():
##            self.word=""
##            self.sug_start=0
##        if self.sug_start==1:
##           if self.present_char<256: 
##            if chr(self.present_char).isalnum():
##                self.word+=chr(self.present_char)
##                print(self.word)
##                list_pre=[]
##                for i in self.sug_list:
##                    if i.lower().find(self.word.lower()) == 0:
##                        list_pre.append(i)
##                list_pre.sort()
##                print(list_pre)
##                self.sug_list_str=""
##                self.sug_list_str="".join(i+" " for i in list_pre)
##                self.output_text.AutoCompShow(len(self.word)-1,self.sug_list_str)
##        if self.present_char==self.dot:
##            self.sug_start=1
##        
##        
##        if self.present_char==8 and self.prev_char==self.dot:
##            self.word=""
##        elif self.present_char==8:
##            self.word=self.word[:-1]        
##        if self.present_char==8 and self.output_text.GetCharAt(self.output_text.GetCurrentPos()-1)==self.dot:
##            self.sug_start=0
        
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
        self.close_sock()
        self.thread1=0
        self.Destroy()
        
    def OnSize(self,e):
        w,h=self.GetSize()
        
    def Open(self,e):
        
        self.output_text.LoadFile("tmp.py")
    def New(self,e):
        print("in new file")
        self.output_text.Clear()
        self.output_text.write("##...start your python code")
    def Save(self,e):
        print("in save file")
    def refresh(self,e):
        print("in refresh")
        self.refresh_pac()
    def run(self,e):
        print("in run")
        self.log=open("output.txt",'a')
        self.log.seek(0)
        self.log.truncate()
        self.log.seek(0)
        print "starting subprocess"
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
                threadoutput.daemon=False
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
            self.close_sock()
            self.thread1=0
            self.Close()
            
        message.Destroy()
            
app=wx.App()
width, height = wx.GetDisplaySize()
myframe(None,-1,"Sirena Gui",pos=wx.DefaultPosition,size=(width, height))
app.MainLoop()
