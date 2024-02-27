import tkinter as tk
from tkinter import ttk
import functools
from platform import system

fp = functools.partial
os = system()
expanded_scrollbar = True

#This code come from the JackTheEngineer/ScrolledFrame.py's Github page
#It allow the scrollableFrame to be actually scrollable with mousewheel 
class ScrollFrame(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        if expanded_scrollbar:
            i = 1
        else:
            i = 0

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vscrollbar.pack(fill=tk.BOTH, side=tk.RIGHT, expand=i)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                            yscrollcommand=self.vscrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        self.vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.item_frame = item_frame = ttk.Frame(self.canvas)
        self.item_frame_id = self.canvas.create_window(0, 0, window=item_frame,anchor=tk.NW)

        item_frame.bind('<Configure>', self._configure_interior)
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.canvas.bind('<Enter>', self._bind_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbind_from_mousewheel)

    def _configure_interior(self, event):
        size = (self.item_frame.winfo_reqwidth(), self.item_frame.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.item_frame.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.item_frame.winfo_reqwidth())

    def _configure_canvas(self, event):
        if self.item_frame.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.itemconfigure(self.item_frame_id, width=self.canvas.winfo_width())

    def _on_mousewheel(self, event, scroll):
        if os == "Linux" or os == "Linux2":
            self.canvas.yview_scroll(int(scroll), "units")
        else:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


    def _bind_to_mousewheel(self, event):
        if os == "Linux" or os == "Linux2":
            self.canvas.bind_all("<Button-4>", fp(self._on_mousewheel, scroll=-1))
            self.canvas.bind_all("<Button-5>", fp(self._on_mousewheel, scroll=1))
        else:
            self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_from_mousewheel(self, event):
        if os == "Linux" or os == "Linux2":
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.unbind_all("<MouseWheel>")
