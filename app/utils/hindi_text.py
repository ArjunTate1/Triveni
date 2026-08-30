"""
Utility functions for Hindi text processing
"""
import re
import unicodedata
from typing import List


def normalize_hindi_text(text: str) -> str:
    """
    Normalize Hindi text using Unicode normalization
    NFC (Canonical Decomposition, followed by Canonical Composition)
    """
    return unicodedata.normalize('NFC', text)


def clean_hindi_text(text: str) -> str:
    """
    Clean Hindi text by removing extra whitespace and normalizing
    """
    text = normalize_hindi_text(text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def split_sentences(text: str) -> List[str]:
    """
    Split Hindi text into sentences using Devanagari punctuation
    """
    text = clean_hindi_text(text)
    # Split on । (Devanagari danda) or . or |
    sentences = re.split(r'[।\.\|]', text)
    # Clean and filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def tokenize_hindi(text: str) -> List[str]:
    """
    Simple word tokenization for Hindi text
    Splits on whitespace and punctuation
    """
    text = clean_hindi_text(text)
    # Remove common punctuation but keep Devanagari characters
    text = re.sub(r'[,;:\(\)\[\]\{\}\"\'।\.]', ' ', text)
    # Split on whitespace
    tokens = text.split()
    # Filter empty tokens
    tokens = [t.strip() for t in tokens if t.strip()]
    return tokens


def extract_numbers(text: str) -> List[int]:
    """
    Extract numbers from text (both Devanagari and Arabic numerals)
    """
    # Devanagari numerals mapping
    devanagari_to_arabic = {
        '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
        '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
    }
    
    # Convert Devanagari numerals to Arabic
    converted_text = text
    for dev, arab in devanagari_to_arabic.items():
        converted_text = converted_text.replace(dev, arab)
    
    # Extract all numbers
    numbers = re.findall(r'\d+', converted_text)
    return [int(n) for n in numbers]


def contains_keyword(text: str, keyword: str) -> bool:
    """
    Check if text contains keyword (case-insensitive for Hindi)
    """
    text = clean_hindi_text(text.lower())
    keyword = clean_hindi_text(keyword.lower())
    return keyword in text


def count_keyword_matches(text: str, keywords: List[str]) -> int:
    """
    Count how many keywords from the list appear in the text
    """
    text = clean_hindi_text(text.lower())
    count = 0
    for keyword in keywords:
        keyword = clean_hindi_text(keyword.lower())
        if keyword in text:
            count += 1
    return count
