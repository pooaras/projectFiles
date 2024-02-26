import re
import hashlib


def preprocess_text(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)
    # Tokenize text
    tokens = text.split()
    return tokens


def generate_shingles(tokens, k):
    shingles = set()
    for i in range(len(tokens) - k + 1):
        shingle = " ".join(tokens[i : i + k])
        shingles.add(shingle)
    return shingles


def hash_shingles(shingles, num_buckets):
    hashed_shingles = []
    for shingle in shingles:
        hash_value = hashlib.sha256(shingle.encode()).hexdigest()
        bucket = int(hash_value, 16) % num_buckets
        hashed_shingles.append(bucket)
    return hashed_shingles


def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union


def main(file1_path, file2_path, k=3, num_buckets=1000):
    with open(file1_path, "r", encoding="utf-8") as file1, open(
        file2_path, "r", encoding="utf-8"
    ) as file2:
        text1 = file1.read()
        text2 = file2.read()

    tokens1 = preprocess_text(text1)
    tokens2 = preprocess_text(text2)

    shingles1 = generate_shingles(tokens1, k)
    shingles2 = generate_shingles(tokens2, k)

    hashed_shingles1 = hash_shingles(shingles1, num_buckets)
    hashed_shingles2 = hash_shingles(shingles2, num_buckets)

    similarity = jaccard_similarity(set(hashed_shingles1), set(hashed_shingles2))

    print("Similarity Percentage:", similarity * 100)


# Example usage:
file1_path = "note.txt"
file2_path = "note copy.txt"
main(file1_path, file2_path)
