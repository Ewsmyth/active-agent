import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import shutil
import os
import sqlite3

class AddPostTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.images = []
        self.image_file_path = tk.StringVar()
        self.post_canvas = tk.Canvas(self)
        self.post_scroll = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.post_canvas.yview)
                
        # Content
        comment_label = tk.Label(self, text="Comment:   ")
        self.comment_input = tk.Text(self, width=40, height=2)
        image_label = tk.Label(self, text="Image:   ")
        image_input = tk.Button(self, text="Select Image", command=self.choose_image)
        submit_post = tk.Button(self, text="Submit", command=self.submit_post)
        self.post_container = tk.Frame(self.post_canvas)

        # Placement
        comment_label.grid(row=0, column=1, sticky="e")
        self.comment_input.grid(row=0, column=2, columnspan=2)
        image_label.grid(row=1, column=1, sticky="e")
        image_input.grid(row=1, column=2, sticky="w")
        submit_post.grid(row=0, column=5, rowspan=2)
        self.post_scroll.grid(row=3, column=34, sticky="ns")
        self.post_canvas.grid(row=3, column=3, columnspan="30", sticky="nsew")
        
        # Configure grid to fill available space
        self.grid_columnconfigure(0, minsize=40)
        self.grid_columnconfigure(4, minsize=40)
        self.grid_rowconfigure(2, minsize=30)
        self.grid_rowconfigure(3, weight=1)

        # Attach the scrollbar to the canvas
        self.post_canvas.config(yscrollcommand=self.post_scroll.set)

        # Attach the frame to the canvas
        self.post_canvas.create_window((0, 0), window=self.post_container, anchor=tk.NW)

        # Bind the canvas and scrollbar to scroll events
        self.post_canvas.bind("<Configure>", self.on_canvas_configure)
        self.post_canvas.bind("<Enter>", lambda event: self.post_canvas.focus_set())  # Set focus when mouse enters canvas
        self.post_scroll.bind("<MouseWheel>", self.on_mouse_wheel)  # Bind mouse wheel event for scrollbar

        # Bind mouse wheel event for post_container
        self.post_container.bind("<MouseWheel>", self.on_mouse_wheel)

        # Bind mouse wheel event for canvas to enable scrolling when hovering over the posts
        self.post_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Populate posts
        self.populate_post_container()

    def choose_image(self):
        # Open file dialog to select an image file
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
        if file_path:
            self.image_file_path.set(file_path)

    def submit_post(self):
        # Get comment from entry widget
        comment = self.comment_input.get("1.0", tk.END).strip()

        # Get selected image file path
        image_path = self.image_file_path.get()

        # Check if an image is selected
        if not image_path:
            messagebox.showerror("Error", "Please select an image.")
            return

        # Generate a unique name for the image file
        image_name = os.path.basename(image_path)
        image_name = str(hash(image_name)) + os.path.splitext(image_path)[1]  # Append file extension

        # Save the image to the "images" folder
        if not os.path.exists('images'):
            os.makedirs('images')
        destination_path = os.path.join('images', image_name)
        shutil.copyfile(image_path, destination_path)

        # Insert post data into the database
        conn = sqlite3.connect('active-agent-db.db')
        c = conn.cursor()
        c.execute("INSERT INTO posts (comment, picture) VALUES (?, ?)", (comment, image_name))
        conn.commit()
        conn.close()

        # Clear entry widgets after submission
        self.comment_input.delete("1.0", tk.END)
        self.image_file_path.set("")
        print("Post added successfully")  # Optional: Print confirmation message

        # Update post container to reflect the new post
        self.populate_post_container()
        print("post loaded")

        # Update the GUI to ensure immediate display of the new post
        self.update_idletasks()

    def delete_post(self, comment, image_name):
        # Confirm deletion
        confirm = messagebox.askyesno("Delete Post", f"Are you sure you want to delete this post?")
        if confirm:
            # Delete post from the database
            conn = sqlite3.connect('active-agent-db.db')
            c = conn.cursor()
            c.execute("DELETE FROM posts WHERE comment=? AND picture=?", (comment, image_name))
            conn.commit()
            conn.close()

            print("Post deleted successfully")  # Optional: Print confirmation message

            # Update post container to reflect the deleted post
            self.populate_post_container()

    def on_mouse_wheel(self, event):
        self.post_canvas.yview_scroll(-1 * int((event.delta / 120)), "units")
        
    def on_canvas_configure(self, event):
        self.post_canvas.configure(scrollregion=self.post_canvas.bbox("all"))

    def populate_post_container(self):
        # Clear existing posts
        for widget in self.post_container.winfo_children():
            widget.destroy()

        # Connect to database and retrieve posts
        conn = sqlite3.connect('active-agent-db.db')
        c = conn.cursor()
        c.execute("SELECT comment, picture FROM posts ORDER BY id DESC")
        posts = c.fetchall()
        conn.close()

        # Populate post container with posts
        for post in posts:
            comment, image_name = post
            image_path = os.path.join('images', image_name)
            if os.path.exists(image_path):
                # Create a frame for the post
                post_frame = tk.Frame(self.post_container, width=self.post_canvas.winfo_width(), height=250, padx=10, pady=10, bd=1, relief=tk.RAISED)
                post_frame.pack(fill=tk.BOTH, expand=True)


                # Display image
                image = Image.open(image_path)
                image_width = 350
                image_height = int((350 / image.width) * image.height)
                image = image.resize((image_width, image_height), Image.LANCZOS)
                photo_image = ImageTk.PhotoImage(image)
                self.images.append(photo_image)
                image_label = tk.Label(post_frame, image=photo_image)
                image_label.pack()

                # Display comment
                comment_label = tk.Label(post_frame, text=comment, wraplength=200)
                comment_label.pack()

                # Delete button
                delete_button = tk.Button(post_frame, text="Delete", command=lambda comment=comment, image_name=image_name: self.delete_post(comment, image_name))
                delete_button.place(relx=1, rely=0, anchor="ne")
            else:
                messagebox.showerror("Error", "Image not found")

        # Update the canvas scroll region to include the entire height of the post container
        self.post_canvas.update_idletasks()  # Ensure all widgets are updated before retrieving the height
        self.post_canvas.configure(scrollregion=self.post_canvas.bbox("all"))

        # Add a binding to update the canvas scroll region whenever the size of the post container changes
        self.post_container.bind(
            "<Configure>",
            lambda event, self=self: self.on_canvas_configure(event)
        )

if __name__ == "__main__":
    root = tk.Tk()
    add_post_tab = AddPostTab(root)
    add_post_tab.pack()
    root.mainloop()
