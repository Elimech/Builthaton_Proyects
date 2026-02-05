import customtkinter as ctk
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image
import os

from core.processor import DocumentProcessor

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class VisualMemoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Visual Memory 2.0")
        self.geometry("1200x800")
        
        # Data
        self.processor = DocumentProcessor()
        self.folder_path = None
        self.results = []
        
        # Init UI
        self._setup_layout()
        
    def _setup_layout(self):
        # Grid layout 1x2 (Sidebar, Main)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="Visual Memory", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_load = ctk.CTkButton(self.sidebar, text="Load Folder", command=self.load_folder)
        self.btn_load.grid(row=1, column=0, padx=20, pady=10)

        self.btn_process = ctk.CTkButton(self.sidebar, text="Process Images", command=self.start_processing)
        self.btn_process.grid(row=2, column=0, padx=20, pady=10)
        
        self.lbl_status = ctk.CTkLabel(self.sidebar, text="Ready",wraplength=180)
        self.lbl_status.grid(row=5, column=0, padx=20, pady=20)
        
        self.progress_bar = ctk.CTkProgressBar(self.sidebar)
        self.progress_bar.grid(row=6, column=0, padx=20, pady=10)
        self.progress_bar.set(0)

        # --- Main Area ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Search
        self.search_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        self.entry_search = ctk.CTkEntry(self.search_frame, placeholder_text="Search images...", width=400)
        self.entry_search.pack(side="left", padx=(0, 10))
        self.entry_search.bind("<Return>", lambda e: self.search())
        
        self.btn_search = ctk.CTkButton(self.search_frame, text="Search", width=100, command=self.search)
        self.btn_search.pack(side="left")

        # Content Split: List (Left) vs Details (Right)
        self.content_split = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_split.grid(row=1, column=0, sticky="nsew")
        self.content_split.grid_columnconfigure(0, weight=1) # List
        self.content_split.grid_columnconfigure(1, weight=1) # Detail
        self.content_split.grid_rowconfigure(0, weight=1)

        # List Area
        self.list_frame = ctk.CTkScrollableFrame(self.content_split, label_text="Images")
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Detail Area
        self.detail_frame = ctk.CTkScrollableFrame(self.content_split, label_text="Details")
        self.detail_frame.grid(row=0, column=1, sticky="nsew")
        
        # Detail Widgets
        self.img_preview = ctk.CTkLabel(self.detail_frame, text="[No Image Selected]")
        self.img_preview.pack(pady=10)
        
        self.lbl_desc_title = ctk.CTkLabel(self.detail_frame, text="Description:", font=ctk.CTkFont(weight="bold"))
        self.lbl_desc_title.pack(anchor="w", pady=(10, 0))
        
        self.txt_desc = ctk.CTkTextbox(self.detail_frame, height=100)
        self.txt_desc.pack(fill="x", pady=5)
        
        self.lbl_ocr_title = ctk.CTkLabel(self.detail_frame, text="Detected Text:", font=ctk.CTkFont(weight="bold"))
        self.lbl_ocr_title.pack(anchor="w", pady=(10, 0))
        
        self.txt_ocr = ctk.CTkTextbox(self.detail_frame, height=200)
        self.txt_ocr.pack(fill="x", pady=5)

    def load_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = Path(folder)
            self.lbl_status.configure(text=f"Loaded: {self.folder_path.name}")
            # Try to populate if cache exists, but don't auto-process heavy logic
            # Just clear list for now
            for widget in self.list_frame.winfo_children():
                widget.destroy()
                
    def start_processing(self):
        if not self.folder_path:
            messagebox.showwarning("Warning", "Load a folder first!")
            return
            
        self.btn_process.configure(state="disabled")
        self.lbl_status.configure(text="Processing... (This may take a while for first run)")
        self.progress_bar.set(0)
        
        # Threading
        thread = threading.Thread(target=self._process_task)
        thread.start()
        
    def _process_task(self):
        def progress_cb(current, total):
            # Update UI from main thread
            val = current / total
            self.after(0, lambda: self.progress_bar.set(val))
            self.after(0, lambda: self.lbl_status.configure(text=f"Processing {current}/{total}"))

        try:
            self.results = self.processor.process_folder(self.folder_path, progress_callback=progress_cb)
            self.after(0, self._on_processing_complete)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self.btn_process.configure(state="normal"))

    def _on_processing_complete(self):
        self.lbl_status.configure(text="Processing Complete!")
        self.btn_process.configure(state="normal")
        self.update_list(self.results)

    def update_list(self, items):
        # Clear
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        for item in items:
            name = Path(item["file"]).name
            score = item.get("score")
            text = f"{name} ({score:.2f})" if score is not None else name
            
            btn = ctk.CTkButton(
                self.list_frame, 
                text=text, 
                anchor="w",
                fg_color="transparent", 
                border_width=1,
                text_color=("gray10", "#DCE4EE"),
                command=lambda i=item: self.show_details(i)
            )
            btn.pack(fill="x", pady=2)

    def show_details(self, item):
        # Image
        try:
            img = Image.open(item["file"])
            # Aspect ratio resize
            base_width = 300
            w_percent = (base_width / float(img.size[0]))
            h_size = int(float(img.size[1]) * float(w_percent))
            img = img.resize((base_width, h_size), Image.Resampling.LANCZOS)
            
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(base_width, h_size))
            self.img_preview.configure(image=ctk_img, text="")
        except Exception as e:
            self.img_preview.configure(image=None, text=f"Error loading image: {e}")

        # Text
        self.txt_desc.delete("0.0", "end")
        self.txt_desc.insert("0.0", item.get("description", ""))
        
        self.txt_ocr.delete("0.0", "end")
        self.txt_ocr.insert("0.0", item.get("text", ""))

    def search(self):
        query = self.entry_search.get()
        if not query:
            self.update_list(self.results)
            return
            
        matches = self.processor.search(query, top_k=10)
        self.update_list(matches)

if __name__ == "__main__":
    app = VisualMemoryApp()
    app.mainloop()
