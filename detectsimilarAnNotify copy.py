import os
import sys
import time
os.environ['PLYER_BACKEND'] = 'win10toast'
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification
import tkinter as tk
from tkinter import messagebox

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
        output=callSimilar(file_path, self.directory, self.window_size)
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

    file_listbox = tk.Listbox(root, height=10, width=60)
    file_listbox.pack(pady=5)
    for filename, similarity in output:
        cur_file=os.path.basename(file_path)
        if(filename!=cur_file):
            file_listbox.insert(tk.END, f"{filename}: {similarity:.2f}%")
    def open_selected_file(event):
        index = file_listbox.curselection()
        if index:
            selected_file = file_listbox.get(index)
            selected_filename = selected_file.split(":")[0].strip()
            selected_file_path = os.path.join(os.path.dirname(file_path), selected_filename)
            os.startfile(selected_file_path)
    label=tk.Label(root,text=f"{file_path}")
    label.pack(pady=5)
    file_listbox.bind("<Double-Button-1>", open_selected_file)
    if os.path.exists(file_path):
        
        if any(similarity == 100 for _, similarity in output):
            match_label = tk.Label(root, text="File already exists with 100% match. Do you want to delete existing files except the current file?", font=("Arial", 10, "bold"), fg="red")
            match_label.pack(pady=5)
            
            delete_button = tk.Button(root, text="Delete All Matching Files", command=lambda: delete_files(output,file_path, root, file_listbox))
            delete_button.pack(pady=5)
    root.mainloop()
def open_file(file_path):
    os.startfile(file_path)
def delete_files(related_files,file_path, root, file_listbox):
    directory = os.path.dirname(file_path)
    files_deleted = False
    for filename, similarity in related_files:
        if similarity == 100 and os.path.join(directory, filename) != file_path:
            os.remove(os.path.join(directory, filename))
            files_deleted = True
    
    if files_deleted:
        messagebox.showinfo("Files Deleted", "All matching files except the current file have been deleted successfully.")
        
        # Clear existing items in the listbox
        file_listbox.delete(0, tk.END)
        
        # Get updated similarity information
        updated_related_files = find_related_files(directory, file_path, window_size)
        
        # Insert updated similarity information into the listbox
        for filename, similarity in updated_related_files:
            file_listbox.insert(tk.END, f"{filename}: {similarity:.2f}%")
    else:
        messagebox.showinfo("No Files Deleted", "No matching files found to delete.")

    root.mainloop()



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
