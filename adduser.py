import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3

class AddUserTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Add a label for instructions
        instruction_label = tk.Label(self, text="Add users to this app, make sure the users you add here already exist in Interactify's database.")
        instruction_label.grid(row=0, column=0, columnspan=3, pady=5, sticky="n")
        
        # Username input
        username_label = tk.Label(self, text="Username:")
        username_label.grid(row=1, column=0, sticky="e", padx=(5, 0), pady=5)
        self.username_entry = tk.Entry(self, width=20)  # Set width to 20 characters
        self.username_entry.grid(row=1, column=1, padx=(0, 5), pady=5, sticky="ew")
        
        # Password input
        password_label = tk.Label(self, text="Password:")
        password_label.grid(row=2, column=0, sticky="e", padx=(5, 0), pady=5)
        self.password_entry = tk.Entry(self, show="*", width=20)  # Show asterisks for password
        self.password_entry.grid(row=2, column=1, padx=(0, 5), pady=5, sticky="ew")

        # Button to submit data
        submit_button = tk.Button(self, text="Submit", command=self.submit_user)
        submit_button.grid(row=3, column=0, columnspan=3, pady=5)
        
        # Frame to contain the Treeview
        treeview_frame = tk.Frame(self)
        treeview_frame.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # Treeview to display usernames, passwords, and delete buttons
        self.user_treeview = ttk.Treeview(treeview_frame, columns=("Username", "Password", "Action"), show="headings")
        self.user_treeview.heading("Username", text="Username")
        self.user_treeview.heading("Password", text="Password")
        self.user_treeview.heading("Action", text="Action")
        self.user_treeview.column("Username", width=30, anchor="center")  # Adjust width of Username column
        self.user_treeview.column("Password", width=30, anchor="center")  # Adjust width of Password column
        self.user_treeview.column("Action", width=20, anchor="center")  # Adjust width of Action column
        self.user_treeview.pack(side="left", fill="both", expand=True)
        
        # Scrollbar for the Treeview
        treeview_scroll = ttk.Scrollbar(treeview_frame, orient="vertical", command=self.user_treeview.yview)
        treeview_scroll.pack(side="right", fill="y")

        # Configure scrollbar and Treeview
        self.user_treeview.config(yscrollcommand=treeview_scroll.set)

        # Populate Treeview with existing usernames and passwords
        self.populate_user_treeview()
        
        # Center content horizontally
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(4, weight=1)  # Allow the Treeview to expand vertically

    def populate_user_treeview(self):
        # Connect to database and retrieve usernames and passwords
        conn = sqlite3.connect('active-agent-db.db')
        c = conn.cursor()
        c.execute("SELECT username, password FROM users")
        users = c.fetchall()
        conn.close()
        
        # Clear existing items in Treeview
        self.user_treeview.delete(*self.user_treeview.get_children())
        
        # Insert usernames, passwords, and delete buttons into Treeview
        for username, password in users:
            self.user_treeview.insert("", tk.END, values=(username, password, "Delete"), tags=("delete_button",))

            # Bind click event to delete button
            self.user_treeview.tag_bind("delete_button", "<ButtonRelease-1>", self.confirm_delete_user)

    def submit_user(self):
        # Get username and password from entry widgets
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Insert user data into the database
        conn = sqlite3.connect('active-agent-db.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        
        # Clear entry widgets after submission
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        print("User added successfully")  # Optional: Print confirmation message
        
        # Update Treeview to reflect the new user
        self.populate_user_treeview()

    def confirm_delete_user(self, event):
        # Get the item selected in the Treeview
        selected_item = self.user_treeview.selection()
        if not selected_item:
            return

        # Get the username from the selected item
        username = self.user_treeview.item(selected_item)['values'][0]

        # Ask for confirmation
        confirmation = messagebox.askyesno("Confirmation", f"Are you sure you want to delete {username}?")
        if confirmation:
            # Delete the user from the database
            conn = sqlite3.connect('active-agent-db.db')
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE username=?", (username,))
            conn.commit()
            conn.close()
            
            # Update Treeview to reflect the deletion
            self.populate_user_treeview()

if __name__ == "__main__":
    root = tk.Tk()
    add_user_tab = AddUserTab(root)
    add_user_tab.pack(expand=True, fill="both")
    root.mainloop()
