import tkinter as tk
from tkinter import ttk
from adduser import AddUserTab
from addpost import AddPostTab
from execute import ExecuteTab
from build_db import build_database

build_database()

class BotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interactify Bot")
        self.geometry("800x600")

        self.window_closed = False  # Flag to indicate if the window is closed

        tab_control = ttk.Notebook(self)
        
        add_user_tab = AddUserTab(tab_control)
        add_post_tab = AddPostTab(tab_control)
        execute_tab = ExecuteTab(tab_control)
        
        tab_control.add(add_user_tab, text="Add User")
        tab_control.add(add_post_tab, text="Add Post")
        tab_control.add(execute_tab, text="Run Bot")
        
        tab_control.pack(expand=1, fill="both")

        # Bind the on_close method to the window close event
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Method to handle window close event."""
        self.window_closed = True
        self.destroy()  # Close the window

if __name__ == "__main__":
    app = BotApp()
    app.mainloop()
