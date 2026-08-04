#!/usr/bin/env python3
"""
Check for missing chapter numbers in a folder structure.

This script scans a directory for subdirectories named "Chapter_{num}_{postfix}"
and reports any missing chapter numbers in the sequence, or confirms all are present.

Run like this:

    python3 check_missing_chapters.py "/home/shalom/Dropbox/backups/quests, hobbies and entertainment/manhwa/For My Derelict Favorite"

"""

import sys
import os
import re
from pathlib import Path


def extract_chapter_numbers(folder_path):
    """
    Extract chapter numbers from folder names.
    
    Args:
        folder_path: Path to the folder to scan
        
    Returns:
        A sorted list of chapter numbers found
    """
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory")
        sys.exit(1)
    
    chapter_numbers = set()
    pattern = re.compile(r'^Chapter_(\d+)_')
    
    try:
        for item in os.listdir(folder_path):
            match = pattern.match(item)
            if match:
                chapter_num = int(match.group(1))
                chapter_numbers.add(chapter_num)
    except PermissionError:
        print(f"Error: Permission denied accessing '{folder_path}'")
        sys.exit(1)
    
    return sorted(chapter_numbers)


def find_missing_chapters(chapter_numbers):
    """
    Find missing chapter numbers in the sequence.
    
    Args:
        chapter_numbers: Sorted list of chapter numbers
        
    Returns:
        List of missing chapter numbers, or empty list if none are missing
    """
    if not chapter_numbers:
        return []
    
    min_num = chapter_numbers[0]
    max_num = chapter_numbers[-1]
    expected = set(range(min_num, max_num + 1))
    found = set(chapter_numbers)
    
    return sorted(expected - found)


def main():
    if len(sys.argv) != 2:
        print("Usage: python check_missing_chapters.py <path_to_folder>")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    chapter_numbers = extract_chapter_numbers(folder_path)
    
    if not chapter_numbers:
        print("No chapter folders found in the specified directory.")
        sys.exit(0)
    
    missing = find_missing_chapters(chapter_numbers)
    
    min_num = chapter_numbers[0]
    max_num = chapter_numbers[-1]
    
    if missing:
        print(f"Missing chapters from {min_num} to {max_num}:")
        print(", ".join(str(num) for num in missing))
    else:
        print(f"All chapters present from {min_num} to {max_num}.")


if __name__ == "__main__":
    main()
