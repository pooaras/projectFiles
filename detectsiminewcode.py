import os
import sys
import time
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CheckboxListbox(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.checked_items = set()
        self.listbox = tk.Listbox(self, selectmode=tk.MULTIPLE)
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.checked_image = ImageTk.PhotoImage(Image.open("checked.png").resize((16, 16)))
        self.unchecked_image = ImageTk.PhotoImage(Image.open("unchecked.png").resize((16, 16)))

        self.listbox.bind("<Button-1>", self.toggle_checkbox)

    def insert_checkbox(self, index, text):
        self.listbox.insert(index, text)
        self.listbox.itemconfig(index, image=self.unchecked_image)

    def toggle_checkbox(self, event):
        index = self.listbox.nearest(event.y)
        if index in self.checked_items:
            self.listbox.itemconfig(index, image=self.unchecked_image)
            self.checked_items.remove(index)
        else:
            self.listbox.itemconfig(index, image=self.checked_image)
            self.checked_items.add(index)

    def get_checked_items(self):
        return [self.listbox.get(idx) for idx in self.checked_items]

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
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
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
        try:
            notification.notify(
                title="New File Created",
                message=f"A new file has been created: {os.path.basename(file_path)}",
                app_name="File Watcher",
            )
        except Exception as e:
            print("Error displaying notification:", e)


def popup_window(output, file_path):
    root = tk.Tk()
    root.title("File Similarity Checker")
    root.geometry("900x700")

    main_frame = tk.Frame(root)
    main_frame.pack(pady=5)

    checkbox_listboxes = []

    for filename, similarity in output:
        cur_file = os.path.basename(file_path)
        if filename != cur_file:
            frame = tk.Frame(main_frame)
            frame.pack(anchor=tk.W)

            checkbox_listbox = CheckboxListbox(frame)
            checkbox_listbox.pack(side=tk.LEFT)
            checkbox_listbox.insert_checkbox(tk.END, f"{filename}: {similarity:.2f}%")

            checkbox_listboxes.append(checkbox_listbox)

    label = tk.Label(root, text=f"{file_path}")
    label.pack(pady=5)

    def delete_selected_files():
        for checkbox_listbox in checkbox_listboxes:
            checked_items = checkbox_listbox.get_checked_items()
            if checked_items:
                selected_file = checked_items[0]
                selected_filename = selected_file.split(":")[0].strip()
                selected_file_path = os.path.join(os.path.dirname(file_path), selected_filename)
                os.remove(selected_file_path)
        messagebox.showinfo("Files Deleted", "Selected files have been deleted successfully.")

        root.destroy()

    delete_button = tk.Button(root, text="Delete Selected Files", command=delete_selected_files)
    delete_button.pack(pady=5)

    root.mainloop()


def open_file(file_path):
    os.startfile(file_path)

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
