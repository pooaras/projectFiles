import os
import sys
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification


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


class NewFileHandler(FileSystemEventHandler):
    def __init__(self, directory, window_size):
        self.directory = directory
        self.window_size = window_size

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        callSimilar(file_path, self.directory, self.window_size)
        print(f"New file created: {file_path}")
        notification.notify(
            title="New File Created",
            message=f"A new file has been created: {os.path.basename(file_path)}",
            app_name="File Watcher",
        )


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
