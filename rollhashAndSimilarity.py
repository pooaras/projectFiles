import os

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


if __name__ == "__main__":
    directory = "/home/mukesh/code"
    file1 = "note.txt"
    window_size = 10  # Adjust window size as needed

    related_files = find_related_files(directory, file1, window_size)
    print(f"Similarity of {file1} with other files in the directory:")
    for filename, similarity in related_files:
        print(f"{filename}: {similarity:.2f}%")
