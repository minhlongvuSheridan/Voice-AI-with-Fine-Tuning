import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class Root:
    def __init__(self, window_width_ratio, window_height_ratio, title, image_icon):
        self.window_width_ratio = window_width_ratio
        self.window_height_ratio = window_height_ratio
        self.title = title
        self.image_icon = image_icon
        
        self.root = tk.Tk()
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        self.window_height = int(screen_height * window_height_ratio)
        self.window_width = int(screen_width * window_width_ratio)
        
        # UI Elements
        self.box_frame = ttk.Frame(self.root)
        self.input_frame = ttk.Frame(self.root)
        self.input_entry = ttk.Entry(self.input_frame)

        
        self.canvas = tk.Canvas(self.box_frame)
        self.scrollbar = ttk.Scrollbar(self.box_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
    
            
    def _on_canvas_configure(self, event):
        # Force the frame inside the canvas to match the canvas width
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def create(self):
        self.root.title(self.title)
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, minsize=80, weight=0)
        self.root.columnconfigure(0, weight=1)
        
        self.box_frame.grid(padx=10, pady=10, row=0, column=0, sticky='nsew')
        self.input_frame.grid(padx=10, pady=10, row=1, column=0, sticky='ew')
        self.input_frame.columnconfigure(0, weight=1)
        # Using grid and ipady to increase height
        self.input_entry.grid(row=0, column=0, sticky='ew', ipady=10)
        
        

        
        # Canvas setup
        self.box_frame.columnconfigure(0, weight=1)
        self.box_frame.rowconfigure(0, weight=1)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # what is the difference of canvas_window and canvas?
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        #
        self.scrollable_frame.bind("<Configure>", self.on_adding_chat)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
    
    
    def on_adding_chat(self,event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(1.0)
    def get_root(self):
        return self.root
    
    def get_scrollable_frame(self):
        return self.scrollable_frame
    def get_input_entry(self):
        return self.input_entry    
    def start(self):
        self.root.mainloop()
    
        
class Chat:
    def __init__(self, name, role, image, root_frame):
        self.name = name
        self.role = role
        self.root_frame = root_frame
        original_image = Image.open(image)
        resized_image = original_image.resize((40, 40), Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(resized_image)
    
    def create_chat(self, chat):
        chat_frame = tk.Frame(self.root_frame, relief="groove", borderwidth=1)
        chat_frame.pack(fill=tk.X, pady=5, padx=5)
        
        
        # Configure columns so the text area takes available space
        
      
        img_label = tk.Label(chat_frame, image=self.image, width=40, height=40)
        name_label = tk.Label(chat_frame, text=self.name, font=("Arial", 10, "bold"))
        text_label = tk.Label(chat_frame, text=chat, wraplength=300, justify="left")
        
        if self.role == 'user':
            chat_frame.columnconfigure(1, minsize=50) 
            chat_frame.columnconfigure(0, weight=1)
            img_label.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky='ne')
            name_label.grid(row=0, column=0, padx=5, sticky='ne')
            text_label.grid(row=1, column=0, padx=5, pady=(0, 5), sticky='ne')
        else:
            chat_frame.columnconfigure(0, minsize=50) 
            chat_frame.columnconfigure(1, weight=1)
            img_label.grid(row=0, column=0, rowspan=2, padx=5, pady=5, sticky='nw')
            name_label.grid(row=0, column=1, padx=5, sticky='nw')
            text_label.grid(row=1, column=1, padx=5, pady=(0, 5), sticky='nw')