import tkinter as tk
from tkinter import ttk
import requests
import sqlite3
import random
import os
import time
import threading

class ExecuteTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.cancel_flag = False  # Flag to control cancellation
        self.is_running = False  # Flag to indicate if the bot is running

        # Dropdown input for protocol selection
        self.protocol_var = tk.StringVar(value="http://")
        protocol_label = tk.Label(self, text="Protocol:")
        protocol_label.grid(row=0, column=1, sticky="w")
        protocol_dropdown = ttk.Combobox(self, textvariable=self.protocol_var, values=["http://", "https://"])
        protocol_dropdown.grid(row=1, column=1, sticky="w")

        # Input for URL/IP
        self.url_var = tk.StringVar()
        url_label = tk.Label(self, text="URL/IP:")
        url_label.grid(row=0, column=2, sticky="w")
        url_entry = tk.Entry(self, textvariable=self.url_var)
        url_entry.grid(row=1, column=2, sticky="w")

        # Number input for PORT
        self.port_var = tk.StringVar()
        port_label = tk.Label(self, text="PORT:")
        port_label.grid(row=0, column=3, sticky="w")
        port_entry = tk.Entry(self, textvariable=self.port_var)
        port_entry.grid(row=1, column=3, sticky="w")

        # Dropdown selection for post frequency
        self.frequency_var = tk.StringVar(value="1")
        frequency_label = tk.Label(self, text="Post Frequency:")
        frequency_label.grid(row=3, column=1, sticky="w")
        frequency_dropdown = ttk.Combobox(self, textvariable=self.frequency_var, values=["1", "5", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55", "60"])
        frequency_dropdown.grid(row=3, column=2, sticky="w")

        # Time input for duration
        self.duration_var = tk.StringVar(value="00:00")
        duration_label = tk.Label(self, text="Duration:")
        duration_label.grid(row=4, column=1, sticky="w")
        duration_entry = ttk.Entry(self, textvariable=self.duration_var)
        duration_entry.grid(row=4, column=2, sticky="w")

        # Button to execute bot
        self.execute_button = tk.Button(self, text="Execute Bot", command=self.execute_bot_periodically)
        self.execute_button.grid(row=5, column=1, pady=10)

        # Button to cancel execution
        self.cancel_button = tk.Button(self, text="Cancel", command=self.cancel_execution)
        self.cancel_button.grid(row=5, column=2, pady=10)

        # Label to indicate if bot is running
        self.status_label = tk.Label(self, text="")
        self.status_label.grid(row=6, column=1, columnspan=3)

        # Text widget to display logs
        self.log_message = tk.Text(self, height=20, width=80)
        self.log_message.grid(row=7, column=1, columnspan=12, padx=10, pady=10)

        # Configure grid to fill available space
        self.grid_columnconfigure(0, minsize=40)

    def execute_bot(self, protocol, url, port):
        # Construct the base URL and login URL
        if port:
            base_url = f"{protocol}{url}:{port}"
        else:
            base_url = f"{protocol}{url}"
        login_url = base_url

        try:
            conn = sqlite3.connect('example.db')
            c = conn.cursor()

            session = requests.Session()
            c.execute("SELECT id, username, password FROM users ORDER BY RANDOM() LIMIT 1")
            user_data = c.fetchone()

            if user_data:
                user_id, username, password = user_data
                login_data = {'a2': username, 'b2': password}
                response = session.post(login_url, data=login_data)

                if response.status_code == 200 and 'userhome' in response.url:
                    self.log_message.insert(tk.END, f"{self.get_timestamp()} - Login successful for user: {username}\n")
                    print(f"Login successful for user: {username}")

                    post_url = f"{base_url}/{username}/userpost"
                    post_response = session.get(post_url)

                    if post_response.status_code == 200:
                        self.log_message.insert(tk.END, f"{self.get_timestamp()} - Successfully navigated to user's post page: {post_url}\n")
                        print(f"Successfully navigated to user's post page: {post_url}")

                        c.execute("SELECT id, comment, picture FROM posts ORDER BY RANDOM() LIMIT 1")
                        post_data = c.fetchone()

                        if post_data:
                            post_id, comment, picture = post_data
                            payload = {'a2': comment}
                            image_path = os.path.join(os.getcwd(), 'images', picture)
                            files = {'media_files': open(image_path, 'rb')}
                            submit_response = session.post(post_url, data=payload, files=files)

                            if submit_response.status_code == 200:
                                self.log_message.insert(tk.END, f"{self.get_timestamp()} - {username} successfully posted {comment}!\n")
                                print(f"{username} successfully posted {comment}!")
                            else:
                                self.log_message.insert(tk.END, f"{self.get_timestamp()} - Failed to submit the post.\n")
                                print("Failed to submit the post.")
                        else:
                            self.log_message.insert(tk.END, f"{self.get_timestamp()} - No posts found in database.\n")
                            print("No posts found in the database.")
                    else:
                        self.log_message.insert(tk.END, f"{self.get_timestamp()} - Failed to navigate to user's post page: {post_url}\n")
                        print(f"Failed to navigate to user's post page: {post_url}")
                else:
                    self.log_message.insert(tk.END, f"{self.get_timestamp()} - Login failed for user: {username}\n")
                    print(f"Login failed for user: {username}")
            else:
                self.log_message.insert(tk.END, f"{self.get_timestamp()} - No users found in the database.\n")
                print("No users found in the database.")

            session.close()
            conn.close()

        except Exception as e:
            self.log_message.insert(tk.END, f"{self.get_timestamp()} - An error occurred while executing bot: {str(e)}\n")
            print(f"An error occurred while executing bot: {str(e)}")

    def get_timestamp(self):
        return time.strftime("%Y-%m-%d %H:%M:%S")

    def execute_bot_periodically(self):
        protocol = self.protocol_var.get()
        url = self.url_var.get()
        port = self.port_var.get()
        post_frequency = int(self.frequency_var.get())
        duration = time.time() + (int(self.duration_var.get()[:2]) * 3600) + (int(self.duration_var.get()[3:]) * 60)

        threading.Thread(target=self.execute_bot_periodically_thread, args=(protocol, url, port, post_frequency, duration)).start()
        self.is_running = True
        self.update_status_label()

    def execute_bot_periodically_thread(self, protocol, url, port, post_frequency, duration):
        while time.time() < duration and not self.cancel_flag:
            self.execute_bot(protocol, url, port)
            time.sleep(post_frequency * 60)  # Convert minutes to seconds

        self.cancel_flag = False  # Reset cancel flag after execution completes
        self.is_running = False
        self.update_status_label()

        # Check if the window is closed and exit the thread if so
        if self.parent.window_closed:
            return

    def cancel_execution(self):
        self.cancel_flag = True
        self.is_running = False
        self.update_status_label()

    def update_status_label(self):
        if self.is_running:
            self.status_label.config(text="Bot is running...")
        else:
            self.status_label.config(text="Bot is not running")

    def on_close(self):
        # Set cancel flag to True to stop the execution threads
        self.cancel_flag = True
        # Wait for the execution threads to finish before closing the application
        self.parent.after(100, self.parent.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    execute_tab = ExecuteTab(root)
    execute_tab.pack(expand=True, fill="both")
    root.mainloop()
