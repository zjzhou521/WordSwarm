import tkinter as tk
import re
import datetime

    
# action functions
reg = "^[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]/[0-9][0-9]:[0-9][0-9]$"

def pop(te):
    popup = tk.Toplevel()
    popup.title('Warnign')
    pCanvas = tk.Canvas(popup, width=300, height=100)
    pCanvas.pack()
    t = tk.Label(popup, text = te)
    pCanvas.create_window(150, 50, window=t)   
    # t.grid(row = 0, column = 0)

def checkdate(d):
    print(d)
    if(re.search(reg, d)):
        spl = d.split("/")
        time = spl[-1].split(":")
        print(spl)
        print(time)
        try:
            datetime.datetime(year = int(spl[2]), month = int(spl[0]), day = int(spl[1]), hour = int(time[0]), minute = int(time[1]))
        except:
            return False
        return True
    else:
        return False

def getDate ():  
    x = date1.get()
    y = date2.get()
    z = date0.get()
    erroMes = ''
    if checkdate(x) == False:
        erroMes += 'Invalid start date'
        print("failed x!!!")
    if checkdate(y) == False:
        if erroMes == '':
            erroMes += 'Invalid end date'
        else:
            erroMes += ' and end date'
        print("failed y!!!")
    if erroMes != '':
        pop(erroMes)
    else:
        # Draw graph
        congrad = tk.Label(root, text= "Successful")
        canvas.create_window(200, 230, window=congrad)    
    date1.delete(0, 'end')
    date2.delete(0, 'end')

def click(event):
    event.delete(0, 'end')

def leave(event):
    event.delete(0, 'end')
    event.insert(0, 'mm/dd/yyyy/00:00')
    root.focus()


root = tk.Tk()
root.title("word cloud")
canvas = tk.Canvas(root, width = 400, height = 300)
canvas.pack()

ins1 = tk.Label(root, text= 'Enter a name')
canvas.create_window(200, 50, window=ins1)
date0 = tk.Entry (root) 
date0.insert(0, 'Name')
date0.bind('<Button-1>', lambda ev:click(date0))
canvas.create_window(200, 80, window=date0)

ins1 = tk.Label(root, text= 'Enter the start time')
canvas.create_window(200, 110, window=ins1)
date1 = tk.Entry (root) 
date1.insert(0, 'mm/dd/yyyy/00:00')
date1.bind('<Button-1>', lambda ev:click(date1))
canvas.create_window(200, 140, window=date1)
    
ins1 = tk.Label(root, text= 'Enter the end time')
canvas.create_window(200, 170, window=ins1)
date2 = tk.Entry (root) 
date2.insert(0, 'mm/dd/yyyy/00:00')
date2.bind('<Button-1>', lambda ev:click(date2))
canvas.create_window(200, 200, window=date2)

button = tk.Button(text='Search', command=getDate)
canvas.create_window(200, 260, window=button)


root.mainloop()
