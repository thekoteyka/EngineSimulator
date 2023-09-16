from tkinter import *
from tkinter.messagebox import showerror
from pygame import mixer
from random import uniform
from colorama import init, Fore

BG = 'gray60'

all_progress_bars = []  # Все прогресс бары
class ProgressBar:
    def __init__(self, window, bg:str, x:int, y:int, lenght:int, max_value:int) -> None:
        all_progress_bars.append(self)

        max_value += 7  # Корректировка (аэ ну)

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

    def reset(self):
        self.marker_value = 0
        self.set_value(0)
        self.canvas.coords(self.marker, 4, 4, 16, 16)

def centerwindow(win):
    """
    💀💀💀💀💀💀💀💀💀💀💀 чт
    центрирует окно ткинтер
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

root = Tk()
root.geometry('400x110')
root.title('Симулятор двигателя?')
root['bg'] = BG
root.resizable(False, False)
centerwindow(root)

PLAY_SOUNDS = True

modes = 'davlenie', 'burn'  # Режимы игры (только для справки)
mode = 'davlenie'  # Текущий режим
last_key = None  # Номер последней нажатой клавиши управления
started = False  # Запущен ли двигатель (скорость поднималась)
running = True   # Запущена ли игра
distance = 0  # Пройденное расстояние
help_actiavted = False  # Была ли активирована помощь (при бездействии)
ticks_showed = False

davlenie_blocked = False  # Заблокирована ли подкачка давления
burn_reduce_lock = False  # Заблокирована ли верояность пробития клапана сгорания
speed_invisible_lock = False
ready_to_visible_speed = False

mixer.init()  # Инициализация для звуков

def playsound(sound):  # Играет звуки
    if not PLAY_SOUNDS:
        return
    
    if sound == 'stop':
        mixer.music.fadeout(5000)
        return
    
    mixer.music.load(f"{sound}.mp3")
    mixer.music.play(loops=0, fade_ms=200)
 
# 2 давления = 1 сгорание
# 2 сгорания = 1 скорость -> 4 давления = 1 скорость
def increase_davlenie():  # Увеличить давление (если возможно)
    if not davlenie_blocked:
        davlenie = davlenie_progress.value
        davlenie_progress.set_value(davlenie + 2)  # Накачиваем по 2 давления за раз

def increase_burn():  # Увеличить сгорание (если возможно)
    if davlenie_progress.value <= 2:
        return
    
    if burn_progress.max_value-7 <= burn_progress.value:  # Чтобы нельзя было накачать выше прогресс бара
        return
    burn = burn_progress.value
    burn_progress.set_value(burn + 1)
    davlenie_progress.value -= 2

def increase_speed():  # Увеличить скорость (если возможно)
    burn = burn_progress.value
    if burn > 2:  # Если есть сгорание
        speed = speed_progress.value
        if speed_progress.max_value <= speed:
            return
        speed_progress.value += 1
        burn_progress.value -= 2

def reduce_speed():  # Стабильное уменьшение скорости
    speed = speed_progress.value
    if speed <= 0:
        lose('Машина заглохла')  # Проигрываем
        return
    speed_progress.set_value(speed-1)

def lose(reason):
    global running, started, last_key, distance
    playsound('death')  # Играем звук смерти из дорс
    running = False  # Временно останавливаем игру
    showerror('Ты проиграл ахахахахаха', f'Причина: {reason}\nДистанция: {distance} амогусов')
    speed_progress.reset()  # Сбрасываем прогресс бары
    burn_progress.reset()
    davlenie_progress.reset()
    last_key = 'None'  # Чтобы не вызывалась помощь
    started = False  # Глушим двигатель
    distance = 0  # Сбрасываем дистанцию
    distance_lbl.configure(text=0)
    root.bind(f'<Shift-KeyRelease>', switch_mode)  # Биндим шифт

    davlenie_progress.update_all()  # Обновляем новую позицию прогресс баров
    playsound('stop')  # Останавливаем звук смерти (с затуханием 10 секунд)
    running = True  # Снова запускаем игру


def probability(percent):  # Расчёт вероятности в процентах
    return uniform(0, 1) < percent/100
    

def pressed(e=None):  # При нажатии
    global last_key
    if not (e.keycode == 90 or e.keycode == 88 or e.keycode == 67):  # Проверяем, что мы нажали z, x или c
        return
    
    if help_actiavted:  # Если была активирована помощь, то закрываем её
        help1_lbl.destroy()

    if e.keycode == last_key:  # Если нажали ту же клавишу что и в прошлый раз, то ничего не делаем
        return

    last_key = e.keycode

    if mode == 'davlenie':  # Если в режиме давления, то увеличиваем его
        increase_davlenie()
    elif mode == 'burn':  # Если в режиме сгорания, то увеличиваем его
        increase_burn()

def safe_sleep(ms):  # Безопасный таймер без зависания программы
    for i in range(ms // ticks_delay):
        run()

def switch_mode(e=None):  # Меняет режим игры (Давление и Сжигание)
    global mode
    root.unbind(f'<Shift-KeyRelease>')  # Отключаем шифт
    if mode == 'davlenie':  # Если было давление, значит ставим сжигание
        mode = 'changing'
        davlenie_lbl.configure(fg=BG)
        burn_lbl.configure(fg='red')  # Делаем задержу при переключении, чтобы он начал работать через секунду
        safe_sleep(1000)
        mode = 'burn'
        burn_lbl.configure(fg='white')
        root.bind(f'<Shift-KeyRelease>', switch_mode)  # Снова включаем шифт
        
    else:  # И наоборот
        mode = 'changing'
        davlenie_lbl.configure(fg='red')  # Так же как и сверху
        burn_lbl.configure(fg=BG)
        safe_sleep(1000)
        mode = 'davlenie'
        davlenie_lbl.configure(fg='white')
        root.bind(f'<Shift-KeyRelease>', switch_mode)
    
def every_n_tick(n):  # Проверяет, наступил ли n-ный тик (ну типо каждый 500-ый и тд)
    return ticks % n == 0

def every_n_sec(seconds):  # Проверяет, прошло ли нужное время, но уже в секундах
    return ticks % (seconds*1000 / ticks_delay) == 0

def logic():  # Динамическая логика
    global started, distance
    speed = speed_progress.value
    davlenie = davlenie_progress.value
    burn = burn_progress.value

    if speed > 2:
        started = True  # Если поехали, то считаем двигатель заведённым
    
    if every_n_tick(30):  # Каждые 30 тиков пробуем увеличить скорость
        increase_speed()

    if every_n_tick(60):  # Каждые 60 тиков пробуем уменьшить скорость
        if started:
            reduce_speed()
    
    if every_n_tick(300):  # Каждые 300 тиков считаем пройденное расстояние с учётом скорости
        distance += 0.1 * speed

        distance *= 10  # Округляем до десятых
        distance = int(distance)
        distance /= 10
        if distance >0:
            distance_lbl.configure(font='Arial 15')
            distance_lbl.configure(text=distance)
    
    if every_n_sec(1):  # Каждую секунду с шансом 5% или 12% если скорость меньше 10
        global speed_invisible_lock, ready_to_visible_speed
        if probability(5) or (speed < 10 and probability(12)):  # Прячем маркер скорости
            if speed_invisible_lock or ready_to_visible_speed:
                return
            speed_invisible_lock = True
            speed_progress.canvas.itemconfig(speed_progress.marker, fill=BG)
            safe_sleep(700)
            speed_progress.canvas.itemconfig(speed_progress.marker, fill='purple')
            safe_sleep(700)
            speed_progress.canvas.itemconfig(speed_progress.marker, fill=BG)
            ready_to_visible_speed = True

    if every_n_sec(10):  # Каждые 10 секунд возвращаем маркер скорости, если его не было
        if speed_invisible_lock and ready_to_visible_speed:
            ready_to_visible_speed = False
            speed_progress.canvas.itemconfig(speed_progress.marker, fill='purple')
            safe_sleep(300)
            speed_progress.canvas.itemconfig(speed_progress.marker, fill=BG)
            safe_sleep(300)
            speed_progress.canvas.itemconfig(speed_progress.marker, fill='purple')
            safe_sleep(300)
            speed_invisible_lock = False
            

    if every_n_sec(1):  # Каждую секунду с шансом 5% или 12% если скорость выше 10
        if probability(5) or (speed > 10 and probability(12)):
            global davlenie_blocked
            if davlenie_blocked:  # Если давление уже заблокировано, то ничего не делаем
                return
            davlenie_progress.set_value(2)  # Ставим давление всего на 2 единицы
            davlenie_progress.canvas.itemconfig(davlenie_progress.marker, fill='red')
            davlenie_blocked = True  # Блокируем давление
            for i in range(8):  # Мигание маркера
                safe_sleep(250)
                davlenie_progress.canvas.itemconfig(davlenie_progress.marker, fill='purple')
                safe_sleep(250)
                davlenie_progress.canvas.itemconfig(davlenie_progress.marker, fill='red')
            davlenie_blocked = False  # Возвращаем накачку давления
            davlenie_progress.canvas.itemconfig(davlenie_progress.marker, fill='purple')  # Возвращаем фиол цвет
    
    if every_n_sec(1):  # Каждую секунду с шансом 5% или 12% если скорость выше 15
        if probability(5) or (speed > 15 and probability(12)):
            global burn_reduce_lock
            if burn_reduce_lock:  # Если уже спускается
                return
            
            burn_reduce_lock = True  # Блокируем повторный запуск этой функции
            burn = burn_progress.value
            if burn_progress.value <= 10:  # Понижаем сгорание на 10
                burn_progress.set_value(0)
            else:
                burn_progress.set_value(burn-10)

            burn_progress.canvas.itemconfig(burn_progress.marker, fill='red')
            for i in range(2):  # Мигание маркера
                safe_sleep(250)
                burn_progress.canvas.itemconfig(burn_progress.marker, fill='purple')
                safe_sleep(250)
                burn_progress.canvas.itemconfig(burn_progress.marker, fill='red')
            burn_progress.canvas.itemconfig(burn_progress.marker, fill='purple')
            burn_reduce_lock = False  # Разблокируем повторный запуск функции



    if ticks == 700 and last_key is None:  # Если прошло уже 700 тиков и не было нажато клавиш управления, то вызываем помощь
        global help_actiavted, help1_lbl
        help_actiavted = True
        help1_lbl = Label(text="Управление осуществляется кнопками\nz, x, c, Shift на клавиатуре. Если ничего\nне происходит, переключи раскладку.\nНачни играть чтобы убрать это сообщение\n                       ", justify='left', font='Arial 15', bg=BG)
        help1_lbl.place(x=1, y=5)


davlenie_lbl = Label(text='<', font='Arial 18', bg=BG, fg='white')
davlenie_lbl.place(x=330, y=38)

burn_lbl = Label(text='<', font='Arial 18', bg=BG, fg=BG)  # Делаем цвет стрелки такой-же как и у фона, чтобы её не было видно
burn_lbl.place(x=330, y=70)

Label(text="Скорость", font=10, bg=BG).place(x=0, y=7)
Label(text="Давление", font=10, bg=BG).place(x=0, y=40)
Label(text="Сгорание", font=10, bg=BG).place(x=0, y=73)

distance_lbl = Label(text='Расстояние', bg=BG, font="Arial 8")  # Потом заменим на число пройденных амогусов
distance_lbl.place(x=330, y=7)


root.bind(f'<KeyRelease>', pressed)  # Биндим кнопки для управления на отпускание клавиш
root.bind(f'<Shift-KeyRelease>', switch_mode)

root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())  # При закрытии окна уничтожаем окно (важно, так как у нас while True)

speed_progress = ProgressBar(root, BG, 80, 10, 250, 30)  # Делаем прогресс бары
davlenie_progress = ProgressBar(root, BG, 80, 43, 250, 100)
burn_progress = ProgressBar(root, BG, 80, 75, 250, 100)

# Тики - основная еденица времени. 1 тик = <ticks_delay> милисекунд
ticks = 0  # Общее количиство тиков
ticks_delay = 10
from time import time
def run():  # Основной цикл программы
    global ticks
    davlenie_progress.update_all()  # Обновляем прогресс бары
    logic()  # Осуществляем логику игры
    root.update()  # Обновляем окно (на всякий случай)
    root.after(ticks_delay)  # Ждём 1 тик (по времени)
    ticks += 1  # Добавляем тик
    
init(autoreset=True)
CHECK_TRUE_TICKRATE = False
try:
    if not CHECK_TRUE_TICKRATE:  # Запуск цикла игры
        while root.winfo_exists():
            if running:
                run()
    else:  # Проверка тиков
        print(f'{Fore.CYAN}Проверка тиков')
        start = time()
        for i in range(1000):
            run()
        print(f'Истинная задержка тиков: {Fore.YELLOW}{round(time()-start, 1)}\n{Fore.WHITE}Задержка тиков в идеальном случае: {Fore.YELLOW}{ticks_delay}.0')
except Exception as e:
    skipping_exceptions = ('can\'t invoke "winfo" command: application has been destroyed',), ('invalid command name ".!canvas"',),\
                          ('invalid command name ".!canvas2"',), ('invalid command name ".!canvas3"',)
    if not e.args in skipping_exceptions:
        print(f'{Fore.RED}{e.args}')
        