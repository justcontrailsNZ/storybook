#!/usr/bin/env python3
"""
Auto-categorise Jekyll posts as 'greek' or 'maori' based on content keywords.
Run this script before `jekyll build`.
"""

import re
import os
from pathlib import Path

# Keywords that strongly indicate Greek myths
GREEK_KEYWORDS = [
    'zeus', 'hera', 'athena', 'apollo', 'artemis', 'hermes', 'ares', 'aphrodite',
    'poseidon', 'hades', 'demeter', 'hestia', 'hercules', 'heracles', 'perseus',
    'theseus', 'odysseus', 'achilles', 'hector', 'trojan', 'olympus', 'midas',
    'medusa', 'minotaur', 'centaur', 'satyr', 'nymph', 'titan', 'prometheus',
    'icarus', 'daedalus', 'orpheus', 'eurydice', 'pandora', 'sisyphus', 'greece',
    'athens', 'sparta', 'iliad', 'odyssey'
]

# Keywords that strongly indicate Māori legends
MAORI_KEYWORDS = [
    'māui', 'maui', 'tāne', 'tane', 'tangaroa', 'tāwhirimātea', 'rangi', 'papa',
    'hatupatu', 'kupe', 'paikea', 'rona', 'hinemoa', 'tutanekai', 'matariki',
    'taniwha', 'pounamu', 'aoraki', 'pōhutukawa', 'iwi', 'whakapapa', 'haka',
    'waka', 'aotearoa', 'new zealand', 'maori', 'māori', 'ngāi tahu', 'ngāpuhi'
]

def detect_category(title, content):
    """Return 'greek', 'maori', or None if uncertain."""
    text = (title + ' ' + content).lower()
    # Remove diacritics for easier matching (e.g., Māori -> maori)
    text = text.replace('ā', 'a').replace('ē', 'e').replace('ī', 'i').replace('ō', 'o').replace('ū', 'u')
    
    greek_score = sum(1 for kw in GREEK_KEYWORDS if kw in text)
    maori_score = sum(1 for kw in MAORI_KEYWORDS if kw in text)
    
    # Also check for explicit phrases
    if 'greek myth' in text or 'ancient greece' in text:
        greek_score += 2
    if 'maori legend' in text or 'aotearoa' in text:
        maori_score += 2
    
    if greek_score > maori_score:
        return 'greek'
    elif maori_score > greek_score:
        return 'maori'
    else:
        return None  # tie or no keywords found

def update_front_matter(file_path, new_category):
    """Read a markdown file, add/update category in front matter, write back."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if front matter exists (--- at start)
    if not content.startswith('---\n'):
        print(f"⚠️  {file_path}: No front matter found. Skipping.")
        return False
    
    # Split front matter from body
    parts = content.split('---\n', 2)
    if len(parts) < 3:
        print(f"⚠️  {file_path}: Malformed front matter. Skipping.")
        return False
    
    front_matter = parts[1]
    body = parts[2]
    
    # Look for existing category line
    category_pattern = r'^category:\s*.*$'
    if re.search(category_pattern, front_matter, re.MULTILINE):
        # Replace existing category
        new_front = re.sub(category_pattern, f'category: {new_category}', front_matter, flags=re.MULTILINE)
    else:
        # Insert category after the first line (e.g., after layout or title)
        lines = front_matter.split('\n')
        # Insert before first empty line or at the end of front matter
        insert_pos = 1  # after the first line (usually layout or title)
        lines.insert(insert_pos, f'category: {new_category}')
        new_front = '\n'.join(lines)
    
    new_content = f'---\n{new_front}\n---\n{body}'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True

def main():
    posts_dir = Path('_posts')
    if not posts_dir.exists():
        print("❌ '_posts' folder not found. Run this script from your Jekyll root.")
        return
    
    for md_file in posts_dir.glob('*.md'):
        print(f"Processing: {md_file.name}")
        with open(md_file, 'r', encoding='utf-8') as f:
            raw = f.read()
        
        # Extract title from front matter or filename
        title_match = re.search(r'^title:\s*(.*)$', raw, re.MULTILINE)
        title = title_match.group(1).strip('"\'') if title_match else md_file.stem.replace('-', ' ').title()
        
        # Remove front matter to get pure content
        body = raw
        if raw.startswith('---\n'):
            parts = raw.split('---\n', 2)
            if len(parts) >= 3:
                body = parts[2]
        
        category = detect_category(title, body)
        if category:
            if update_front_matter(md_file, category):
                print(f"   ✅ Categorised as {category}")
            else:
                print(f"   ❌ Failed to update {md_file}")
        else:
            print(f"   ⚠️  Could not determine category (no strong keywords). You may need to add 'category: greek' or 'category: maori' manually.")

if __name__ == '__main__':
    main()
