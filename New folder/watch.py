import os
import sys
import time
from PyPDF2 import PdfReader
from PIL import Image, ImageTk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import ttk, messagebox
import textract
from docx import Document
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

# Initialize NLTK resources
stop_words = set(stopwords.words('english'))
ps = PorterStemmer()
lemmatizer = WordNetLemmatizer()

class CheckboxTreeview(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.checked_items = set()
        self.treeview = ttk.Treeview(self, selectmode="extended", columns=("Filename", "Similarity"))
        self.treeview.heading("#0", text="Check")
        self.treeview.heading("Filename", text="Filename")
        self.treeview.heading("Similarity", text="Similarity")
        self.treeview.column("#0", width=50)  # Adjust the width of the Check column if needed
        self.treeview.column("Filename", width=500)  # Adjust the width of the Filename column as needed
        self.treeview.column("Similarity", width=100)  # Adjust the width of the Similarity column as needed
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        checked_img = Image.open("checked.png")
        checked_img = checked_img.resize((16, 16))  # Resize to 16x16 pixels

        # Convert resized images to PhotoImage
        self.checked_image = ImageTk.PhotoImage(checked_img)

        self.treeview.bind("<Button-1>", self.toggle_checkbox)

    def insert_checkbox(self, index, filename, similarity):
        item_id = self.treeview.insert("", index, text="", values=(filename, similarity))
        self.checked_items.discard(item_id)

    def toggle_checkbox(self, event):
        item_id = self.treeview.identify_row(event.y)
        if item_id:
            if item_id in self.checked_items:
                self.treeview.item(item_id, image="")
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

def preprocess_text(text):
    # Remove special characters, punctuation, and extra whitespaces
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    # Convert text to lowercase
    text = text.lower()

    # Tokenize the text
    words = word_tokenize(text)

    # Remove stopwords
    words = [word for word in words if word not in stop_words]

    # Lemmatize words (or alternatively, use stemming with ps.stem(word))
    words = [lemmatizer.lemmatize(word) for word in words]

    # Join the preprocessed words back into a single string
    preprocessed_text = ' '.join(words)
    
    return preprocessed_text

def extract_text_from_pdf(pdf_path):
    print(f"Reading PDF: {pdf_path}")
    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)
        text = ''
        total_pages = len(reader.pages)
        for i, page in enumerate(reader.pages, 1):
            print(f"Processing page {i}/{total_pages}")
            text += page.extract_text()
        print("PDF reading complete.")
        
    # Preprocess the extracted text
    preprocessed_text = preprocess_text(text)
    
    return preprocessed_text

def extract_text_from_docx(docx_path):
    try:
        doc = Document(docx_path)
        text = ''
        for paragraph in doc.paragraphs:
            text += paragraph.text
        
        # Preprocess the extracted text
        preprocessed_text = preprocess_text(text)
        print(preprocessed_text)
        return preprocessed_text
    except Exception as e:
        print(f"Error extracting text from {docx_path}: {e}")
        return None

def extract_text_from_file(file_path):
    """
    Extract text content from a supported file format.
    """
    supported_extensions = ['.txt', '.pdf', '.doc', '.docx', '.rtf', '.html', '.htm', '.odt']  # Add more extensions as needed
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        # Extract text from PDF
        return extract_text_from_pdf(file_path)
    elif file_extension == '.txt':
        # Read text from plain text file
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    elif file_extension in ['.doc','.docx']:
        text2 = extract_text_from_docx(file_path)
        print(text2)
        return text2
    elif file_extension in ['.rtf', '.html', '.htm', '.odt']:
        # Extract text from other supported formats using textract
        try:
            text = textract.process(file_path, encoding='utf-8').decode('utf-8')
            return text
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return ""
    else:
        print(f"Unsupported file format: {file_extension}")
        return ""

def find_similarity(file1, file2, window_size):
    """
    Find similarity between two text files using rolling hashing.
    """
    print(f"Calculating similarity between {file1} and {file2}")
    text1 = extract_text_from_file(file1)
    text2 = extract_text_from_file(file2)

    hash_values1 = set(rolling_hash(text1, window_size))
    hash_values2 = set(rolling_hash(text2, window_size))

    common_hashes = hash_values1.intersection(hash_values2)
    similarity = (len(common_hashes) / (len(hash_values1) + len(hash_values2) - len(common_hashes))) * 100

    print(f"Similarity calculation complete.")
    return similarity

def find_related_files(directory, file1, window_size):
    """
    Find and compare similarity of related files in the directory to file1.
    """
    related_files = []
    new_file_size = os.path.getsize(file1)
    supported_extensions = ['.txt', '.pdf', '.doc', '.docx', '.rtf', '.html', '.htm', '.odt']  # Add more extensions as needed
    for filename in os.listdir(directory):
        if filename != file1 and os.path.splitext(filename)[1].lower() in supported_extensions:
            filepath = os.path.join(directory, filename)
            # Check file size
            if os.path.getsize(filepath) <= new_file_size + new_file_size/2:
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
    def __init__(self, directory, window_size, delay=5):
        self.directory = directory
        self.window_size = window_size
        self.delay = delay  # Delay in seconds

    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        # Check if the file is a temporary file (e.g., .crdownload)
        if file_path.endswith('.crdownload'):
            print(f"Skipping incomplete download: {file_path}")
            return
        
        # Wait for the file to be completely downloaded
        time.sleep(self.delay)
        
        output = callSimilar(file_path, self.directory, self.window_size)
        print(f"New file created: {file_path}")
        popup_window(output, file_path)


def popup_window(files, file_path, autocheck=True):
    def delete_selected_files():
        nonlocal files
        checked_items = checkbox_treeview.get_checked_items()
        files_to_delete = []  # Accumulate files to delete
        for item in checked_items:
            selected_filename = item
            selected_file = next((file for file in files if file[0] == selected_filename), None)
            if selected_file:
                files_to_delete.append(selected_file)  # Accumulate the file object
        if files_to_delete:
            # Construct a confirmation message listing all files to be deleted
            confirmation_message = f"Are you sure you want to delete the following files?\n\n"
            confirmation_message += "\n".join(file[0] for file in files_to_delete)
            # Display a confirmation messagebox
            if messagebox.askyesno("Confirm Deletion", confirmation_message):
                # Delete files and display a success message
                for file_to_delete in files_to_delete:
                    files.remove(file_to_delete)
                    filepath = os.path.join(directory, file_to_delete[0])
                    try:
                        os.remove(filepath)
                    except OSError as e:
                        messagebox.showerror("Error", f"Failed to delete {file_to_delete[0]}: {e}")
                messagebox.showinfo("Files Deleted", "Selected files have been deleted successfully.")
                refresh_treeview()
        elif checked_items:  # Add this condition to check if any files are selected for deletion
            messagebox.showinfo("No Files Selected", "No files selected for deletion.")

    def auto_delete_selected_files():
        nonlocal files
        checked_items = checkbox_treeview.get_checked_items()
        files_to_delete = []
        for item in checked_items:
            selected_filename = item
            selected_file = next((file for file in files if file[0] == selected_filename), None)
            if selected_file:
                files.remove(selected_file)
                files_to_delete.append(selected_filename)
        auto_checked_for_deletion = [filename for filename in autochecked_files if filename not in files_to_delete]
        if auto_checked_for_deletion:
                # Delete auto-checked files and display a success message
            for filename in auto_checked_for_deletion:
                filepath = os.path.join(directory, filename)
                try:
                    os.remove(filepath)
                except OSError as e:
                    messagebox.showerror("Error", f"Failed to delete {filename}: {e}")
            messagebox.showinfo("Files Deleted", "Auto-checked files with 100% similarity have been deleted successfully.")
            # Remove auto-checked files from the list before refreshing the treeview
            files = [file for file in files if file[0] not in auto_checked_for_deletion]
            refresh_treeview()

    def refresh_treeview():
        checkbox_treeview.treeview.delete(*checkbox_treeview.treeview.get_children())
        for filename, similarity in files:
            cur_file = os.path.basename(file_path)
            if filename != cur_file:
                checkbox_treeview.insert_checkbox(tk.END, filename, f"{similarity:.2f}%")

    root = tk.Tk()
    root.title("File Similarity Checker")
    root.geometry("900x700")
    root.attributes('-topmost', True)
    main_frame = tk.Frame(root)
    main_frame.pack(pady=5)

    checkbox_treeview = CheckboxTreeview(main_frame)
    checkbox_treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    item_ids = {}  # Dictionary to store item IDs corresponding to filenames
    autochecked_files = []  
    matching=""# Files to be auto-checked
    checkIf=0
    for filename, similarity in files:
        cur_file = os.path.basename(file_path)
        if filename != cur_file:
            item_id = checkbox_treeview.insert_checkbox(tk.END, filename, f"{similarity:.2f}%")
            item_ids[filename] = item_id  # Store item ID corresponding to filename
            if autocheck and similarity == 100 and checkIf!=2 and checkIf!=3:
                autochecked_files.append(filename)
                matching="100"
                checkIf=1
            elif autocheck and similarity >= 90 and checkIf!=1 and checkIf!=3:
                autochecked_files.append(filename)
                matching="Above 90"
                checkIf=2
            elif autocheck and similarity >= 80 and checkIf!=2 and checkIf!=1:
                autochecked_files.append(filename)
                matching="Above 80"
                checkIf=3
    label = tk.Label(root, text=f"{file_path}")
    label.pack(pady=5)

    delete_button = tk.Button(root, text="Delete Selected Files", command=delete_selected_files)
    delete_button.pack(pady=5)

    if autocheck:
        auto_delete_button = tk.Button(root, text="Auto-Delete", command=auto_delete_selected_files)
        auto_delete_button.pack(pady=5)
        autochecked_label = tk.Label(root, text=f"Files matching with {file_path}: {matching}")
        autochecked_label.pack(pady=5)

    root.mainloop()

def main(directory, window_size=10, autocheck=True):
    event_handler = NewFileHandler(directory, window_size)
    observer = Observer()
    observer.schedule(event_handler, directory)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    directory = r"D:\project\projectFiles\New folder"
    main(directory, autocheck=True)
