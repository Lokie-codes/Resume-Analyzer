import nltk
from nltk.stem import PorterStemmer
import re
from nltk.corpus import stopwords

# Initialize resources
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def clean_text(text: str) -> str:
    """Cleans the text by removing stop words and non-alphanumeric characters."""
    cleaned_words = []

    for word in nltk.word_tokenize(text.strip().lower()):
        if word.isalnum() and word not in stop_words:
            cleaned_words.append(word)

    return " ".join(cleaned_words)

def stem_words(text: str) -> str:
    """Stems the cleaned text."""
    seen_stems = set()
    stemmed_words = []

    for word in nltk.word_tokenize(text):
        stemmed_word = stemmer.stem(word)
        if stemmed_word not in seen_stems:
            seen_stems.add(stemmed_word)
            stemmed_words.append(stemmed_word)

    return " ".join(stemmed_words)

def sanitize_text(content: str) -> dict:
    """Sanitizes content by dividing it into blocks, cleaning and stemming each block."""
    blocks = divide_text_into_blocks(content)
    # return {key: stem_words(clean_text(value)) for key, value in blocks.items()}
    return {key: stem_words(clean_text(value)) for key, value in blocks.items()}


def divide_text_into_blocks(text: str) -> dict:
    """Divides the text into blocks based on titles and content."""
    pattern = r'(?<=\n)([A-Za-z\s]+)\n'
    sections = re.split(pattern, text.strip())
    blocks = {}

    for section in sections:
        lines = section.split('\n', 1)
        title = lines[0].strip().lower() if len(lines) > 1 else "default"
        content = lines[1].strip().lower().replace('\n', ' ') if len(lines) > 1 else lines[0].strip().lower()
        
        blocks[title] = blocks.get(title, '') + (' ' + content if title in blocks else content)

    return blocks

def remove_bullet_points(text: str) -> str:
    """Removes bullet points from the text."""
    bullet_pattern = r'[-*•]\s*|^\s*\d+\.\s*'
    cleaned_text = re.sub(bullet_pattern, '', text, flags=re.MULTILINE)
    return cleaned_text.strip()
