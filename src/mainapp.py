import tkinter as tk
from tkinter import ttk
import threading
import queue
import time
import numpy as np

class TurboController(ttk.Frame):

    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.info = {}
        for key,value in self.master.Dict.items():
            if value in ['Failure','Low Speed','Frequency','Supply Current','Driving Frequency','Error Reset','On/Off','Low Speed Activate']:
                self.info[value] = {'name':value, 'key':key, 'status':'Off'}
        
        self.eqnmap = {
                'Supply Current' : self.SupplyCurrent,
                'Driving Frequency' : self.Frequency,
                'Failure' : self.HighVoltage,
                'Low Speed' : self.HighVoltage,
                'Frequency' : self.HighVoltage,
                }

        ttk.Label(self, text='Failure:').grid(row=0, column=0, sticky='ew')
        LED(self, 25, self.info['Failure'], colors=('gray', 'red')).grid(row=0, column=1)

        ttk.Label(self, text='Low Speed:').grid(row=1, column=0, sticky='ew')
        LED(self, 25, self.info['Low Speed'], colors=('gray', 'green')).grid(row=1, column=1)

        ttk.Label(self, text='Low Output Frequency:').grid(row=2, column=0, sticky='ew')
        LED(self, 25, self.info['Frequency'], colors=('gray', 'red')).grid(row=2, column=1)

        ttk.Label(self, text='Supply Current (A)').grid(row=3, column=0, sticky='ew')
        Monitor(self,self.info['Supply Current']).grid(row=3, column=1)

        ttk.Label(self, text='Driving Frequency (Hz)').grid(row=4, column=0, sticky='ew')
        Monitor(self,self.info['Driving Frequency']).grid(row=4, column=1)

        ttk.Label(self, text='Error Reset').grid(row=5, column=0, sticky='ew')
        LED(self, 25, self.info['Error Reset'], colors=('gray', 'green')).grid(row=5, column=1)

        ttk.Label(self, text='Pump On/Off').grid(row=6, column=0, sticky='ew')
        LED(self, 25, self.info['On/Off'], colors=('gray', 'green')).grid(row=6, column=1)

        ttk.Label(self, text='Low Speed Activate').grid(row=7, column=0, sticky='ew')
        LED(self, 25, self.info['Low Speed Activate'], colors=('gray', 'green')).grid(row=7, column=1)

        self.startbtn = ttk.Button(self, text='Start Pump', command=self.StartPump)
        self.startbtn.grid(row=8, column=0, columnspan=2, sticky='ew')

        self.lowspeedbtn = ttk.Button(self, text='Start Low Speed', command=self.StartLowSpeed)
        self.lowspeedbtn.grid(row=9, column=0, columnspan=2, sticky='ew')

        self.resetbtn = ttk.Button(self, text='Pump Reset', command=lambda: ThreadedTask(self,self.PumpReset))
        self.resetbtn.grid(row=10, column=0, columnspan=2, sticky='ew')

    
    def StartPump(self):
        if self.startbtn['text'] == 'Start Pump':
            self.master.ToggleOn(self.info['On/Off'], 'Start')
            self.startbtn['text'] = 'Stop Pump' 
        elif self.startbtn['text'] == 'Stop Pump':
            self.master.ToggleOff(self.info['On/Off'], 'Start')
            self.startbtn['text'] = 'Start Pump' 

    def StartLowSpeed(self):
        if self.lowspeedbtn['text'] == 'Start Low Speed':
            self.master.ToggleOn(self.info['Low Speed Activate'], 'Low Speed')
            self.lowspeedbtn['text'] = 'Stop Low Speed' 
        elif self.lowspeedbtn['text'] == 'Stop Low Speed':
            self.master.ToggleOff(self.info['Low Speed Activate'], 'Low Speed')
            self.lowspeedbtn['text'] = 'Start Low Speed' 

    def PumpReset(self):
        self.resetbtn['state'] = tk.DISABLED
        self.lowspeedbtn['state'] = tk.DISABLED
        self.startbtn['state'] = tk.DISABLED
        if self.startbtn['text'] == 'Stop Pump':
            self.StartPump()
        if self.lowspeedbtn['text'] == 'Stop Low Speed':
            self.StartLowSpeed()
        self.master.ToggleOn(self.info['Error Reset'], 'Reset')
        time.sleep(3)
        self.master.ToggleOff(self.info['Error Reset'], 'Reset')
        self.resetbtn['state'] = tk.ACTIVE
        self.lowspeedbtn['state'] = tk.ACTIVE
        self.startbtn['state'] = tk.ACTIVE

    def SupplyCurrent(self, info):
        if self.master.DevFlag:
            info['status'] = np.random.random(1)[0]
        else:
            V = self.master.LJ.getAIN(int(key[3:]), resolutionIndex = 8)
            info['status'] = V/4.

    def Frequency(self, info):
        if self.master.DevFlag:
            info['status'] = np.random.random(1)[0]
        else:
            V = self.master.LJ.getAIN(int(key[3:]), resolutionIndex = 8)
            info['status'] = V*125.

    def HighVoltage(self, info):
        if self.master.DevFlag:
            V = np.random.random(1)[0]
        else:
            V = self.master.LJ.getAIN(int(key[3:]), resolutionIndex = 8)
        if V > 3.:
            info['status'] = 'On'
        else:
            info['status'] = 'Off'


    
class Monitor(ttk.Label):
    
    def __init__(self, master, info):
        self.master = master
        self.info = info
        self.var = tk.StringVar()
        self.var.set(info['status'])
        super().__init__(master, textvariable=self.var)
        self.info = info
        ThreadedTask(self, self.monitor)
    
    def monitor(self):
        while True:
            self.master.eqnmap[self.info['name']](self.info)
            if isinstance(self.info['status'], type('')):
                text = self.info['status']
            elif isinstance(self.info['status'], type(1.)):
                text = '{:.1f}'.format(self.info['status'])
            else: 
                text='Error' 
            self.var.set(text)
            time.sleep(1)


class LED(tk.Canvas):
    def __init__(self, master, width, relay, colors=('gray', 'green')):
        super().__init__(master = master, width = width, height = width)
        self.master = master
        self.colors=colors
        self.light = self.create_rectangle(0, 0, width, width, fill=self.colors[0])

        self.relay = relay
        ThreadedTask(self, self.toggleColor)

    def toggleColor(self):
        while True:
            try:
                self.master.eqnmap[self.relay['name']](self.relay)
            except:
                pass
            if self.relay:
                try:
                    if self.relay['status'] == 'On':
                        self.itemconfig(self.light, fill=self.colors[1])
                    elif self.relay['status'] == 'Off':
                        self.itemconfig(self.light, fill=self.colors[0])
                    else: print('Error in toggling LED Color')
                except KeyError:
                    pass
            time.sleep(.1) 

class ThreadedTask():
    def __init__(self,master,func, *args, **kwargs):
        self.master = master
        self.thread_queue = queue.Queue()
        self.new_thread = threading.Thread(target=func, *args, **kwargs)
        self.new_thread.setDaemon(1)
        self.new_thread.start()
        self.master.after(100, self.listen_for_result)

    def listen_for_result(self):
        try:
            self.res = self.thread_queue.get(0)
        except queue.Empty:
            self.master.after(100, self.listen_for_result)

class MainApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.grid_rowconfigure(0, w=1) 
        self.grid_columnconfigure(0, w=1) 

        self.Dict = {
                'AIN0' : 'Failure',
                'AIN1' : 'Low Speed',
                'AIN2' : 'Frequency',
                'AIN3' : 'Supply Current',
                'AIN4' : 'Driving Frequency',
                'FIO3' : 'Error Reset',
                'FIO4' : 'On/Off',
                'FIO5' : 'Low Speed Activate',
                'FIO6' : 'Enable Override',
                }

        self.DevFlag = False
        try:
            self.LJ = u6.U6()
            self.LJ.getCalibrationData()
            for i in range(20):
                self.LJ.getFeedback(u6.BitDirWrite(i, 0)) # output
            #self.LJ.configTimerClock(TimerClockBase=3, TimerClockDivisor=4)
            #self.LJ.configIO(NumberTimersEnabled=4, EnableCounter1=True)
        except:
            self.DevFlag = True

        self.turbo = TurboController(self)
        self.turbo.grid(row=0, column=0, sticky='news')

    def ToggleOn(self, relay, name):
        if relay['key'].startswith('E'):
            IONumber = int(relay['key'][3:])+8
        elif relay['key'].startswith('C'):
            IONumber = int(relay['key'][3:])+16
        else:
            IONumber = int(relay['key'][3:])
        if not self.DevFlag:
            self.LJ.getFeedback(u6.BitDirWrite(int(IONumber), 1))
            self.LJ.getFeedback(u6.BitStateWrite(int(IONumber), 0))
        relay['status'] = 'On'

    def ToggleOff(self, relay, name):
        if relay['key'].startswith('E'):
            IONumber = int(relay['key'][3:])+8
        elif relay['key'].startswith('C'):
            IONumber = int(relay['key'][3:])+16
        else:
            IONumber = int(relay['key'][3:])
        if not self.DevFlag:
            self.LJ.getFeedback(u6.BitDirWrite(int(IONumber), 0))
        relay['status'] = 'Off'


if __name__ == '__main__':

    root = MainApp()
    root.mainloop()
