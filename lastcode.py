import os
import sys
import time
from PIL import Image, ImageTk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import ttk, messagebox

class CheckboxTreeview(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.checked_items = set()
        self.treeview = ttk.Treeview(self, selectmode="extended", columns=("Filename", "Similarity"))
        self.treeview.heading("#0", text="Check")
        self.treeview.heading("Filename", text="Filename")
        self.treeview.heading("Similarity", text="Similarity")
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        checked_img = Image.open("checked.png")
        unchecked_img = Image.open("circle.png")
        checked_img = checked_img.resize((16, 16))  # Resize to 16x16 pixels
        unchecked_img = unchecked_img.resize((16, 16))  # Resize to 16x16 pixels

        # Convert resized images to PhotoImage
        self.checked_image = ImageTk.PhotoImage(checked_img)
        self.unchecked_image = ImageTk.PhotoImage(unchecked_img)

        self.treeview.bind("<Button-1>", self.toggle_checkbox)

    def insert_checkbox(self, index, filename, similarity):
        item_id = self.treeview.insert("", index, text="", values=(filename, similarity))
        self.checked_items.discard(item_id)

    def toggle_checkbox(self, event):
        item_id = self.treeview.identify_row(event.y)
        if item_id:
            if item_id in self.checked_items:
                self.treeview.item(item_id, image=self.unchecked_image)
                self.checked_items.remove(item_id)
            else:
                self.treeview.item(item_id, image=self.checked_image)
                self.checked_items.add(item_id)

    def get_checked_items(self):
        checked_items = []
        for item_id in self.checked_items:
            try:
                item_values = self.treeview.item(item_id)
                if item_values is not None:  # Check if the item exists in the treeview
                    checked_items.append(item_values["values"][0])
            except tk.TclError:  # Catch the TclError if the item is not found
                pass
        return checked_items


def rolling_hash(text, window_size):
    """
    Compute rolling hash values for all windows of size `window_size`.
    """
    hash_values = []
    text_len = len(text)
    prime = 101  # Choose a prime number
    modulus = 2**32  # Typically a large prime number
    hash_value = 0
    for i in range(window_size):
        hash_value = (hash_value * prime + ord(text[i])) % modulus
    hash_values.append(hash_value)

    for i in range(1, text_len - window_size + 1):
        hash_value = (hash_value * prime - ord(text[i - 1]) * pow(prime, window_size, modulus) + ord(text[i + window_size - 1])) % modulus
        hash_values.append(hash_value)

    return hash_values

def find_similarity(file1, file2, window_size):
    """
    Find similarity between two text files using rolling hashing.
    """
    with open(file1, 'r',encoding='utf-8') as f1, open(file2, 'r',encoding='utf-8') as f2:
        text1 = f1.read()
        text2 = f2.read()

    hash_values1 = set(rolling_hash(text1, window_size))
    hash_values2 = set(rolling_hash(text2, window_size))

    common_hashes = hash_values1.intersection(hash_values2)
    similarity = (len(common_hashes) / (len(hash_values1) + len(hash_values2) - len(common_hashes))) * 100

    return similarity

def find_related_files(directory, file1, window_size):
    """
    Find and compare similarity of all files in the directory to file1.
    """
    related_files = []
    for filename in os.listdir(directory):
        if filename != file1 and filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            similarity = find_similarity(file1, filepath, window_size)
            related_files.append((filename, similarity))
    return related_files

def callSimilar(file_path, directory, window_size):
    file1 = file_path
    related_files = find_related_files(directory, file1, window_size)
    print(f"Similarity of {file1} with other files in the directory:")
    for filename, similarity in related_files:
        print(f"{filename}: {similarity:.2f}%")

    return related_files

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, directory, window_size):
        self.directory = directory
        self.window_size = window_size

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        output = callSimilar(file_path, self.directory, self.window_size)
        print(f"New file created: {file_path}")
        popup_window(output, file_path)

def popup_window(files, file_path):

    def delete_selected_files():
        nonlocal files
        checked_items = checkbox_treeview.get_checked_items()
        files_to_delete = []  # Accumulate files to delete
        for item in checked_items:
            selected_filename = item
            selected_file = next((file for file in files if file[0] == selected_filename), None)
            if selected_file:
                files.remove(selected_file)
                files_to_delete.append(selected_filename)  # Accumulate the filename
        if files_to_delete:
            # Construct a confirmation message listing all files to be deleted
            confirmation_message = f"Are you sure you want to delete the following files?\n\n"
            confirmation_message += "\n".join(files_to_delete)
            # Display a confirmation messagebox
            if messagebox.askyesno("Confirm Deletion", confirmation_message):
                # Delete files and display a success message
                for filename in files_to_delete:
                    file_path = os.path.join(directory, filename)
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        messagebox.showerror("Error", f"Failed to delete {filename}: {e}")
                messagebox.showinfo("Files Deleted", "Selected files have been deleted successfully.")
        checkbox_treeview.treeview.delete(*checkbox_treeview.treeview.get_children())
        for filename, similarity in files:
            checkbox_treeview.insert_checkbox(tk.END, filename, f"{similarity:.2f}%")


    root = tk.Tk()
    root.title("File Similarity Checker")
    root.geometry("900x700")
    root.attributes('-topmost', True) 
    main_frame = tk.Frame(root)
    main_frame.pack(pady=5)

    checkbox_treeview = CheckboxTreeview(main_frame)
    checkbox_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    for filename, similarity in files:
        cur_file = os.path.basename(file_path)
        if filename != cur_file:
            checkbox_treeview.insert_checkbox(tk.END, filename, f"{similarity:.2f}%")

    label = tk.Label(root, text=f"{file_path}")
    label.pack(pady=5)

    delete_button = tk.Button(root, text="Delete Selected Files", command=delete_selected_files)
    delete_button.pack(pady=5)

    root.mainloop()


# Usage:
# popup_window([("file1.txt", 90), ("file2.txt", 80)], "path/to/current/file.txt")



def watch_directory(directory, window_size):
    event_handler = NewFileHandler(directory, window_size)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py /path/to/directory window_size")
        sys.exit(1)

    directory = sys.argv[1]
    window_size = int(sys.argv[2])

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a directory.")
        sys.exit(1)
    watch_directory(directory, window_size)
