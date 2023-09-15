from tkinter import *

BG = 'gray60'

all_progress_bars = []
class ProgressBar:
    def __init__(self, window, bg:str, x:int, y:int, lenght:int, max_value:int) -> None:
        all_progress_bars.append(self)

        max_value += 7

        self.window = window
        self.marker_value = 0
        self.value = 0
        self.max_value = max_value
        self.canvas = None

        # 300x200+52+52
        self.canvas = Canvas(window, bg='white', highlightthickness=0)
        self.canvas.place(x=x, y=y, height=20, width=lenght)

        canvas = self.canvas

        canvas.create_rectangle(0, 0, lenght, 20,
                                              fill=bg,
                                              outline='lightgray',
                                              width=4)
        
        self.value_in_pixel = (lenght) / max_value

        self.marker = canvas.create_rectangle(4, 4, 16, 16, fill='purple', width=0)

    def _true_position(self, val):
        return int(self.value_in_pixel * val)
        return val
    
    def _go(self):
        if self._true_position(self.value) < self.marker_value:
            if self._true_position(self.value) < self.marker_value:
                self._move(-1)
                self.marker_value = self.canvas.coords(self.marker)[0]

        elif self._true_position(self.value) > self.marker_value:
            if self._true_position(self.value) > self.marker_value:
                self._move(1)
                self.marker_value = self.canvas.coords(self.marker)[0]
    
    def _move(self, x:int):
        self.canvas.move(self.marker, x, 0)
        self.window.update()
        # self.window.after(5)
    
    def set_value(self, value:int):
        if value > self.max_value - 7:
            self.value = self.max_value - 7
            return
        else:
            self.value = value
            self._go()

    def update_all(self):
        if self.value > self.max_value - 7:
            self.value = self.max_value - 7
            return
        else:
            for progress_bar in all_progress_bars:
                progress_bar._go()

root = Tk()
root.geometry('400x250')
root.title('Симулятор двигателя?')
root['bg'] = BG

modes = 'davlenie', 'burn'
mode = 'davlenie'
last_key = None

def pressed(e=None):
    global last_key

    def increase_davlenie():
        davlenie = davlenie_progress.value
        davlenie_progress.set_value(davlenie + 2)

    def increase_burn():
        if davlenie_progress.value <= 2:
            return
        burn = burn_progress.value
        burn_progress.set_value(burn + 1)
        davlenie_progress.value -= 2

    if e.char == last_key:
        return
    last_key = e.char

    if mode == 'davlenie':
        increase_davlenie()
    elif mode == 'burn':
        increase_burn()
    

def switch_mode(e=None):
    global mode
    if mode == 'davlenie':
        mode = 'burn'
        davlenie_lbl.configure(fg=BG)
        burn_lbl.configure(fg='white')
        
    else:
        mode = 'davlenie'
        davlenie_lbl.configure(fg='white')
        burn_lbl.configure(fg=BG)
        

davlenie_lbl = Label(text='<', font='Arial 18', bg=BG, fg='white')
davlenie_lbl.place(x=330, y=38)

burn_lbl = Label(text='<', font='Arial 18', bg=BG, fg=BG)
burn_lbl.place(x=330, y=70)

Label(text="Скорость", font=10, bg=BG).place(x=0, y=7)
Label(text="Давление", font=10, bg=BG).place(x=0, y=40)
Label(text="Сгорание", font=10, bg=BG).place(x=0, y=73)


root.bind(f'<KeyRelease-z>', pressed)
root.bind(f'<KeyRelease-x>', pressed)
root.bind(f'<Shift-KeyRelease>', switch_mode)

root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())

speed_progress = ProgressBar(root, BG, 80, 10, 250, 100)
davlenie_progress = ProgressBar(root, BG, 80, 43, 250, 100)
burn_progress = ProgressBar(root, BG, 80, 75, 250, 100)


while root.winfo_exists():
    speed_progress.set_value(100)
    # davlenie_progress.set_value(65)
    # burn_progress.set_value(30)
    davlenie_progress.update_all()
    root.update()
    root.after(10)