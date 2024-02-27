import tkinter as tk
from tkinter import ttk
import functools
fp = functools.partial

class ScrollableFrame(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Use a frame inside the canvas to hold the items
        self.item_frame = tk.Frame(self.canvas)
        self.item_frame.pack(fill="both", expand=True)

        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="both")

        # Configure scrolling
        self._item_frame_id = self.canvas.create_window(
            self.canvas.winfo_width() / 2, 0, anchor="nw", window=self.item_frame
        )

        self.item_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def on_frame_configure(self, event):
        # Update the scroll region of the canvas when the size of the item frame changes
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfigure(self._item_frame_id, width=self.canvas.winfo_width())

#This code come from the JackTheEngineer/ScrolledFrame.py's Github page
#It allow the scrollableFrame to be actually scrollable with mousewheel 
class ScrollFrame(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
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
        self.canvas.yview_scroll(int(scroll), "units")

    def _bind_to_mousewheel(self, event):
        self.canvas.bind_all("<Button-4>", fp(self._on_mousewheel, scroll=-1))
        self.canvas.bind_all("<Button-5>", fp(self._on_mousewheel, scroll=1))

    def _unbind_from_mousewheel(self, event):
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")
