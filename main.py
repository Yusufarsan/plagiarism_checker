import time
import re
import os
import docx
import fitz  # PyMuPDF
from collections import Counter

def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_docx_file(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def read_pdf_file(file_path):
    pdf_document = fitz.open(file_path)
    full_text = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        full_text.append(page.get_text())
    return '\n'.join(full_text)

def read_file(file_path):
    if file_path.endswith('.txt'):
        return read_text_file(file_path)
    elif file_path.endswith('.docx'):
        return read_docx_file(file_path)
    elif file_path.endswith('.pdf'):
        return read_pdf_file(file_path)
    else:
        raise ValueError("Unsupported file format")

def preprocess_text(text):
    return re.sub(r'\W+', ' ', text).lower()

# Knuth-Morris-Pratt (KMP) Algorithm
def compute_lps(pattern):
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def kmp_search(text, pattern):
    lps = compute_lps(pattern)
    i = j = 0
    matches = []
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == len(pattern):
            matches.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return matches

# Boyer-Moore (BM) Algorithm
def preprocess_bad_character_rule(pattern):
    NO_OF_CHARS = 150000  # Size depends on character set. This is for extended ASCII.
    bad_char = [-1]*NO_OF_CHARS
    m = len(pattern)
    for i in range(m):
        bad_char[ord(pattern[i])] = i
    return bad_char

def bm_search(text, pattern):
    bad_char = preprocess_bad_character_rule(pattern)
    m = len(pattern)
    n = len(text)
    s = 0
    matches = []
    while s <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        if j < 0:
            matches.append(s)
            s += (m - bad_char[ord(text[s + m])] if s + m < n else 1)
        else:
            if ord(text[s+j]) < len(bad_char):  # Check if the value is within the range of the list
                s += max(1, j - bad_char[ord(text[s + j])])
            else:
                s += 1  # Skip the character if it's not within the range
    return matches

def word_frequencies(text, algorithm):
    words = text.split()
    frequencies = Counter()
    for word in set(words):
        if algorithm == 'KMP':
            matches = kmp_search(text, word)
        elif algorithm == 'BM':
            matches = bm_search(text, word)
        else:
            raise ValueError("Unsupported algorithm. Choose 'KMP' or 'BM'.")
        frequencies[word] = len(matches)
    return frequencies

def calculate_similarity(text1, text2, algorithm):
    freq1 = word_frequencies(text1, algorithm)
    freq2 = word_frequencies(text2, algorithm)
    
    all_words = set(freq1.keys()).union(set(freq2.keys()))
    match_count = 0
    total_count = 0

    for word in all_words:
        count1 = freq1.get(word, 0)
        count2 = freq2.get(word, 0)
        match_count += min(count1, count2)
        total_count += max(count1, count2)

    if total_count == 0:
        return 100.0

    sim_percentage = (match_count / total_count) * 100
    return sim_percentage



def calculate_jaccard_similarity(text1, text2, k=5):
    def get_k_grams(text, k):
        return [text[i:i+k] for i in range(len(text) - k + 1)]

    k_grams1 = set(get_k_grams(text1, k))
    k_grams2 = set(get_k_grams(text2, k))

    intersection = len(k_grams1.intersection(k_grams2))
    union = len(k_grams1.union(k_grams2))

    if union == 0:
        return 0.0

    return (intersection / union) * 100

def main(file_path1, file_path2, algorithm):
    text1 = preprocess_text(read_file(file_path1))
    text2 = preprocess_text(read_file(file_path2))
    similarity = calculate_similarity(text1, text2, algorithm)
    print(f"Similarity: {similarity:.2f}%")

if __name__ == "__main__":
    # input file paths
    file1 = input("Enter first document filename: ")
    file2 = input("Enter second document filename: ")
    algorithm = input("Enter the algorithm to use ('KMP' or 'BM'): ").strip().upper()

    file1 = "test/" + file1
    file2 = "test/" + file2

    print()
    
    if not os.path.exists(file1) or not os.path.exists(file2):
        print("One or both of the files do not exist.")
    elif file1.split('.')[-1] != file2.split('.')[-1]:
        print("Both files must be of the same format.")
    elif file1.split('.')[-1] not in ['txt', 'docx', 'pdf']:
        print("Unsupported file format.")
    else:
        start_time = time.time()
        main(file1, file2, algorithm)
        print("\nExecution time: %s seconds" % (time.time() - start_time))
        print()