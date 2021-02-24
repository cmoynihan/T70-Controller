import u6 
import tkinter as tk
from tkinter import ttk

def ToggleOn(relay):
    if relay['key'].startswith('E'):
        IONumber = int(relay['key'][3:])+8
    elif relay['key'].startswith('C'):
        IONumber = int(relay['key'][3:])+16
    else:
        IONumber = int(relay['key'][3:])
    LJ.getFeedback(u6.BitDirWrite(int(IONumber), 1))
    LJ.getFeedback(u6.BitStateWrite(int(IONumber), 0))

def ToggleOff(relay):
    if relay['key'].startswith('E'):
        IONumber = int(relay['key'][3:])+8
    elif relay['key'].startswith('C'):
        IONumber = int(relay['key'][3:])+16
    else:
        IONumber = int(relay['key'][3:])
    LJ.getFeedback(u6.BitDirWrite(int(IONumber), 0))

def Power():
    if powerbtn['text'] == 'Start Pump':
        ToggleOn({'key':'FIO0'})
        powerbtn['text'] = 'Stop Pump'

    elif powerbtn['text'] == 'Stop Pump':
        ToggleOff({'key':'FIO0'})
        powerbtn['text'] = 'Start Pump'

if __name__ == '__main__':

    try:
        LJ = u6.U6()
        LJ.getCalibrationData()
        for i in range(20):
            LJ.getFeedback(u6.BitDirWrite(i, 0)) # output
    except:
        pass

    root = tk.Tk()
    root.grid_rowconfigure(0, w=1)
    root.grid_columnconfigure(0, w=1)
    root.geometry('300x300')

    powerbtn = ttk.Button(root, text='Start Pump', command=Power)
    powerbtn.grid(row=0, column=0, sticky='news')
    root.mainloop()
