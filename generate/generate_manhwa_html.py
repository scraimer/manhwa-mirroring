#!/usr/bin/env python3
"""
Generates HTML files for displaying vertically scrolling manga/manhwa chapters.
Creates a TOC page and individual chapter pages with full-screen vertical scrolling.
"""

import os
import re
import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Optional
import json
from urllib.parse import quote


def parse_chapter_number(folder_name: str) -> Tuple[float, str]:
    """
    Parse chapter number from folder name like 'Chapter_001_Chapter 001'.
    Returns (numeric_value, display_name) for sorting.
    """
    match = re.match(r'Chapter_(\d+(?:\.\d+)?)(.*)', folder_name)
    if match:
        num_str = match.group(1)
        num = float(num_str)
        display = folder_name.replace('Chapter_', '')
        return (num, display)
    return (float('inf'), folder_name)


def get_chapters(base_path: str) -> List[Tuple[str, str, str]]:
    """
    Get all chapters from base path.
    Returns list of (folder_name, display_name, full_path).
    """
    chapters = []
    base = Path(base_path)
    
    for item in base.iterdir():
        if item.is_dir() and item.name.startswith('Chapter_'):
            num, display = parse_chapter_number(item.name)
            chapters.append((item.name, display, str(item)))
    
    # Sort by chapter number
    chapters.sort(key=lambda x: parse_chapter_number(x[0])[0])
    return chapters


def get_pages(chapter_path: str) -> List[str]:
    """
    Get all image files from chapter folder, sorted.
    Supports .webp, .jpg, .jpeg, .png
    """
    chapter_dir = Path(chapter_path)
    images = []
    
    for ext in ['*.webp', '*.jpg', '*.jpeg', '*.png', '*.gif']:
        images.extend(sorted(chapter_dir.glob(ext)))
        images.extend(sorted(chapter_dir.glob(ext.upper())))
    
    return [img.name for img in sorted(set(images))]


def chapter_anchor_id(folder_name: str) -> str:
    anchor = re.sub(r'[^A-Za-z0-9_-]+', '-', folder_name).strip('-')
    return anchor or 'chapter'


def build_chapter_payload(chapters: List[Tuple[str, str, str]]) -> str:
    return json.dumps([
        {
            "folder": folder_name,
            "display": display_name,
            "anchor": chapter_anchor_id(folder_name),
            "file": f"chapter_{folder_name}.html",
        }
        for folder_name, display_name, _ in chapters
    ])


def generate_toc_html(
    chapters: List[Tuple[str, str, str]],
    output_dir: str,
    story_name: str
) -> str:
    """Generate Table of Contents HTML."""
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{story_name}</title>
    <link rel="stylesheet" href="assets/style-toc.css">
</head>
<body>
    <div class="container">
        <div class="toc-links">
            <a href="/" class="home-link">Home</a>
        </div>
        <h1>{story_name}</h1>
        <div class="chapters-grid">
'''.format(story_name=story_name)
    
    for folder_name, display_name, _ in chapters:
        anchor_id = chapter_anchor_id(folder_name)
        chapter_file = f"chapter_{folder_name}.html"
        html += f'''            <a href="{chapter_file}" class="chapter-link" id="{anchor_id}" data-chapter="{folder_name}">
                <h3>{display_name}</h3>
                <span class="hidden-badge" aria-hidden="true">Hidden</span>
            </a>
'''
    
    chapter_payload = build_chapter_payload(chapters)
    html += f'''        </div>
    </div>
    <script>
        window.CHAPTERS = {chapter_payload};
        window.STORY_NAME = {json.dumps(story_name)};
        window.HIDE_CHAPTER_ENDPOINT = "/cgi-bin/hide_chapter.py";
    </script>
    <script src="assets/script-toc.js"></script>
</body>
</html>'''
    
    return html


def generate_chapter_html(
    chapter_folder: str,
    chapter_display: str,
    pages: List[str],
    chapter_index: int,
    total_chapters: int,
    chapters: List[Tuple[str, str, str]],
    story_name: str
) -> str:
    """Generate chapter page HTML with vertical scrolling."""
    
    # Calculate previous and next chapter
    prev_chapter = chapters[chapter_index - 1][0] if chapter_index > 0 else None
    next_chapter = chapters[chapter_index + 1][0] if chapter_index < total_chapters - 1 else None
    prev_chapter_file = f"chapter_{prev_chapter}.html" if prev_chapter else None
    next_chapter_file = f"chapter_{next_chapter}.html" if next_chapter else None
    
    # Build navigation buttons
    prev_btn = (
        f'<a href="{prev_chapter_file}" class="nav-btn js-nav-link" data-nav="prev" data-fallback-href="{prev_chapter_file}">← PREV</a>'
        if prev_chapter_file else
        '<button class="nav-btn" data-nav="prev" disabled>← PREV</button>'
    )
    next_btn = (
        f'<a href="{next_chapter_file}" class="nav-btn js-nav-link" data-nav="next" data-fallback-href="{next_chapter_file}">NEXT →</a>'
        if next_chapter_file else
        '<button class="nav-btn" data-nav="next" disabled>NEXT →</button>'
    )
    toc_anchor = chapter_anchor_id(chapter_folder)
    toc_btn = f'<a href="index.html#{toc_anchor}" class="nav-btn toc-btn">📖 TOC</a>'
    edit_btn = '<button class="nav-btn edit-mode-btn" type="button" data-action="edit-mode-toggle">Edit Mode</button>'
    hide_btn = '<button class="nav-btn edit-only hide-chapter-btn" type="button" data-action="hide-chapter-toggle">Hide Chapter</button>'
    
    # Extract chapter number from display name for title
    chapter_num = chapter_display.split('_')[0]
    
    # Build image container - reference images relative to the parent directory
    images_html = ''
    encoded_chapter_folder = quote(chapter_folder, safe='')
    first_chunk_end = (len(pages) + 2) // 3
    second_chunk_end = ((len(pages) * 2) + 2) // 3
    for index, page in enumerate(pages):
        page_number = index + 1
        encoded_page = quote(page, safe='')
        image_path = f"../{encoded_chapter_folder}/{encoded_page}"
        if index < first_chunk_end:
            chunk = 1
        elif index < second_chunk_end:
            chunk = 2
        else:
            chunk = 3

        if chunk == 1:
            img_tag = (
                f'<img src="{image_path}" alt="Page" class="manga-page" '
                f'data-chunk="{chunk}" data-page="{page_number}">'
            )
        else:
            img_tag = (
                f'<img data-src="{image_path}" alt="Page" class="manga-page deferred-page" '
                f'data-chunk="{chunk}" data-page="{page_number}">'
            )

        select_btn = (
            f'<button class="page-select-btn edit-only" type="button" '
            f'data-action="toggle-last-page" data-page="{page_number}">Set as Last Page</button>'
        )

        images_html += (
            f'            <div class="page-container" data-page="{page_number}">\n'
            f'                {img_tag}\n'
            f'                {select_btn}\n'
            f'            </div>\n'
        )
    
    dropzone_html = (
        '        <div class="next-chapter-dropzone" id="nextChapterDropzone">\n'
        '            <div class="next-chapter-dropzone-arrow">&#8595;</div>\n'
        '        </div>\n'
        if next_chapter_file else
        ''
    )

    page_count = len(pages)
    next_chapter_file_json = json.dumps(next_chapter_file) if next_chapter_file else "null"
    prev_chapter_file_json = json.dumps(prev_chapter_file) if prev_chapter_file else "null"
    chapter_payload = build_chapter_payload(chapters)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{story_name} - {chapter_num}</title>
    <link rel="stylesheet" href="assets/style-chapter.css">
</head>
<body>
    <div class="progress-bar" id="progress"></div>
    
    <div class="swipe-indicator" id="swipeIndicator">
       <div class="swipe-arrow">&#10132;</div>
    </div>
    <div class="swipe-progress-line" id="swipeProgressLine"></div>
    
    <div class="vertical-swipe-indicator" id="verticalSwipeIndicator">
       <div class="vertical-swipe-arrow">&#8595;</div>
    </div>
    <div class="vertical-swipe-progress-line" id="verticalSwipeProgressLine"></div>
      
    <div class="top-nav">
        <div class="chapter-title">{chapter_display}</div>
        <div class="nav-buttons">
            {prev_btn}
            {next_btn}
            {toc_btn}
            {edit_btn}
            {hide_btn}
        </div>
        <div class="page-counter"><span id="current-page">1</span>/{page_count}</div>
    </div>
    
    <div class="container" id="container">
{images_html}{dropzone_html}    </div>
    
    <div class="bottom-nav">
        {prev_btn}
        {next_btn}
        {toc_btn}
        {edit_btn}
        {hide_btn}
    </div>
    
    <script>
        window.PAGE_COUNT = {page_count};
        window.CHAPTERS = {chapter_payload};
        window.STORY_NAME = {json.dumps(story_name)};
        window.CURRENT_CHAPTER = {json.dumps(chapter_folder)};
        window.PREV_CHAPTER_FILE = {prev_chapter_file_json};
        window.NEXT_CHAPTER_FILE = {next_chapter_file_json};
        window.HIDE_CHAPTER_ENDPOINT = "/cgi-bin/hide_chapter.py";
        window.LAST_PAGE_ENDPOINT = "/cgi-bin/last_page.py";
    </script>
    <script src="assets/script-chapter.js"></script>
</body>
</html>'''
    
    return html


def copy_assets(output_dir: str) -> None:
    """Copy static assets to the output directory."""
    assets_dir = Path(__file__).parent / 'assets'
    output_assets_dir = Path(output_dir) / 'assets'
    
    if not assets_dir.exists():
        print("⚠ Warning: assets directory not found, skipping asset copy")
        return
    
    output_assets_dir.mkdir(exist_ok=True)
    
    # Copy all files from assets directory
    for asset_file in assets_dir.iterdir():
        if asset_file.is_file():
            shutil.copy2(asset_file, output_assets_dir / asset_file.name)
    
    print("✓ Assets copied to output directory")


def generate_all_html(base_path: str, output_dir: Optional[str] = None) -> None:
    """
    Main function to generate all HTML files.
    """
    base_path = os.path.abspath(base_path)
    
    if not os.path.isdir(base_path):
        print(f"Error: {base_path} is not a valid directory")
        sys.exit(1)
    
    # Create output directory
    if output_dir is None:
        output_dir = os.path.join(base_path, 'html_output')
    
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📚 Scanning chapters in: {base_path}")
    chapters = get_chapters(base_path)
    
    if not chapters:
        print("❌ No chapters found!")
        sys.exit(1)
    
    print(f"✅ Found {len(chapters)} chapters\n")
    
    story_name = os.path.basename(base_path)
    
    # Copy assets first
    print("📦 Copying assets...")
    copy_assets(output_dir)
    print()
    
    # Generate TOC
    print("📖 Generating Table of Contents...")
    toc_html = generate_toc_html(chapters, output_dir, story_name)
    toc_path = os.path.join(output_dir, 'index.html')
    with open(toc_path, 'w', encoding='utf-8') as f:
        f.write(toc_html)
    print(f"   ✓ Saved: index.html")
    
    # Generate chapter pages
    print("📄 Generating chapter pages...")
    for idx, (folder_name, display_name, chapter_path) in enumerate(chapters):
        pages = get_pages(chapter_path)
        
        if not pages:
            print(f"   ⚠ {display_name}: No images found, skipping")
            continue
        
        chapter_html = generate_chapter_html(
            folder_name,
            display_name,
            pages,
            idx,
            len(chapters),
            chapters,
            story_name
        )
        
        output_file = os.path.join(output_dir, f'chapter_{folder_name}.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(chapter_html)
        
        print(f"   ✓ {display_name} ({len(pages)} pages)")
    
    print(f"\n✨ Complete! Open {os.path.join(output_dir, 'index.html')} to start reading")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python generate_manhwa_html.py <path_to_manga_folder> [output_dir]")
        print("\nExample:")
        print('  python generate_manhwa_html.py "/path/to/For My Derelict Favorite"')
        print('  python generate_manhwa_html.py "/path/to/manga" "/path/to/output"')
        sys.exit(1)
    
    base_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    generate_all_html(base_path, output_dir)
