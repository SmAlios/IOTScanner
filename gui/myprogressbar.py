from tkinter.ttk import Progressbar, Style
import tkinter as tk
import threading
from time import sleep

class Myprogressbar(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.value = 0

    def draw_progressbar(self, master, columnspan, row, column):
        self.master = master

        self.style = Style()
        self.style.layout(
            'text.Horizontal.TProgressbar',
            [
                (
                    'Horizontal.Progressbar.trough', 
                    {'children':
                        [
                            ('Horizontal.Progressbar.pbar',
                                {
                                    'side': 'left',
                                    'sticky': 'ns'
                                }
                            )
                        ],
                        'sticky': 'nswe'
                    }
                ),
                (
                    'Horizontal.Progressbar.label',
                    {'sticky': 'nswe'}
                )
            ]
        )
        self.style.configure('text.Horizontal.TProgressbar', text=f"{self.value} %", anchor='center', foreground='black', background='green')
        #style.configure("TProgressbar", background="green")

        self.progressbar_label= tk.Label(
            self.master,
            text="Click on start to begin the scan"
        )
        self.progressbar_label.grid(columnspan=columnspan, row=row, column=column, sticky="n")

        self.progressbar = Progressbar(
                self.master,
                cursor="spider",
                style="text.Horizontal.TProgressbar",
                orient='horizontal',
                length=520,
                mode='determinate'
            )
        self.progressbar.grid(columnspan=columnspan, row=(row + 1), column=column, sticky="n")

        #to save the display when navigat between tabs
        if self.value > 0:
            self.progressbar['value'] = self.value
            self.master.update_idletasks()

        if self.value > 0 and self.value < 100:
            self.progressbar_label["text"] = "Scan in progress, it's slow and should take some minutes ..."
        elif self.value >= 100:
            self.progressbar_label["text"] = "Scan is complete, antennas continue to perform background"


    def start(self, get_value, scan_start_value, scan_end_value):
        self.get_value = get_value
        self.scan_start_value = scan_start_value
        self.scan_end_value = scan_end_value

        self.running = True
        super().start()

    def stop(self):
        self.running = False
        daemon=False

    def run(self):
        self.progressbar_label["text"] = "Scan in progress, it's slow and should take some minutes ..."

        while self.value < 100 and self.running:

            get_value = self.get_value.get_progressbar_value()

            self.value = get_value * (100 / (self.scan_end_value - self.scan_start_value))
            
            #print(f"{get_value} => {self.value}%")

            self.progressbar['value'] = self.value
            self.style.configure('text.Horizontal.TProgressbar', text=f"{self.value} %")
            self.master.update_idletasks()

            sleep(1)

            if self.value == 100:
                self.running == False

        print("Stopping progressbar thread ...")
        self.progressbar_label["text"] = "Scan is complete, antennas continue to perform background"
        self.stop()