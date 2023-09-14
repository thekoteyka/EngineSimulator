from tkinter import *

BG = 'gray60'

root = Tk()
root.geometry('400x250')
root.title('Симулятор двигателя?')
root['bg'] = BG

l = Label(root, text='s')
l.pack()


last_key = None

def pressed(e):
    global last_key

    print(e.char)
    l.configure(text='ddddddddddd')

    if e.char == last_key:
        return
    last_key = e.char

    

root.bind(f'<KeyRelease-z>', pressed)
root.bind(f'<KeyRelease-x>', pressed)

s = 0
while 1:
    l.configure(text=s)
    s += 1
    for i in range(20):
        root.after(20)
        root.update()



root.mainloop()