import os
import shutil
import tkinter as tk
from tkinter import simpledialog, ttk

class CustomDialog(simpledialog.Dialog):
    def __init__(self, master, file):
        self.file = file
        super().__init__(master)

    def buttonbox(self):
        box = ttk.Frame(self)
        self.resizable(width=False, height=False)
        self.result = []

        self.do_for_all_conflicts = tk.BooleanVar(value = None)
        w = ttk.Label(box,padding= 0,text=f"{self.file['filename']} is not in the root directory, \n would you like to copy it to the new root directory?", wraplength=300)
        w.pack(side=tk.TOP, padx=5, pady=5)
        w = ttk.Checkbutton(box,variable=self.do_for_all_conflicts, text="Do for all conflicts", width=30, command=self.yes_to_all)
        w.pack(side=tk.TOP, padx=5, pady=5)
        w = ttk.Button(box, text="Yes", width=15, command=self.yes)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="No", width=15, command=self.no)
        w.pack(side=tk.LEFT, padx=5, pady=5)
    
        self.bind("<Escape>", self.no)
        box.pack()

    def yes(self, event=None):
        self.result.append("yes")
        self.destroy()

    def no(self, event=None):
        self.result.append("no")
        
        self.destroy()

    def yes_to_all(self, event=None):
        self.result.append("yes_to_all")


def copy_file(source_folder, dest_folder, filename):
    source_file_path = os.path.join(source_folder, filename)
    dest_file_path = os.path.join(dest_folder, filename)

    if not os.path.exists(source_file_path):
        return

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    shutil.copy2(source_file_path, dest_file_path)

def ask_yes_no_and_to_all(top_root, file_dict):
    dialog = CustomDialog(top_root, file_dict)
    result = dialog.result
    return result
