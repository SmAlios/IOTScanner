import tkinter as tk


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
