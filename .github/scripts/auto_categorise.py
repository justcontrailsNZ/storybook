#!/usr/bin/env python3
import re
import os
from pathlib import Path

GREEK_KEYWORDS = [
    'zeus', 'hera', 'athena', 'apollo', 'artemis', 'hermes', 'ares', 'aphrodite',
    'poseidon', 'hades', 'demeter', 'hestia', 'hercules', 'heracles', 'perseus',
    'theseus', 'odysseus', 'achilles', 'hector', 'trojan', 'olympus', 'midas',
    'medusa', 'minotaur', 'centaur', 'satyr', 'nymph', 'titan', 'prometheus',
    'icarus', 'daedalus', 'orpheus', 'eurydice', 'pandora', 'sisyphus', 'greece',
    'athens', 'sparta', 'iliad', 'odyssey'
]

MAORI_KEYWORDS = [
    'māui', 'maui', 'tāne', 'tane', 'tangaroa', 'tāwhirimātea', 'rangi', 'papa',
    'hatupatu', 'kupe', 'paikea', 'rona', 'hinemoa', 'tutanekai', 'matariki',
    'taniwha', 'pounamu', 'aoraki', 'pōhutukawa', 'iwi', 'whakapapa', 'haka',
    'waka', 'aotearoa', 'new zealand', 'maori', 'māori', 'ngāi tahu', 'ngāpuhi'
]

def detect_category(title, content):
    text = (title + ' ' + content).lower()
    # Normalise diacritics
    text = text.replace('ā', 'a').replace('ē', 'e').replace('ī', 'i').replace('ō', 'o').replace('ū', 'u')
    
    greek_score = sum(1 for kw in GREEK_KEYWORDS if kw in text)
    maori_score = sum(1 for kw in MAORI_KEYWORDS if kw in text)
    
    if 'greek myth' in text or 'ancient greece' in text:
        greek_score += 2
    if 'maori legend' in text or 'aotearoa' in text:
        maori_score += 2
    
    if greek_score > maori_score:
        return 'greek'
    elif maori_score > greek_score:
        return 'maori'
    else:
        return None

def update_front_matter(file_path, new_category):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.startswith('---\n'):
        print(f"⚠️  {file_path}: No front matter. Skipping.")
        return False
    
    parts = content.split('---\n', 2)
    if len(parts) < 3:
        print(f"⚠️  {file_path}: Malformed front matter.")
        return False
    
    front_matter = parts[1]
    body = parts[2]
    
    category_pattern = r'^category:\s*.*$'
    if re.search(category_pattern, front_matter, re.MULTILINE):
        new_front = re.sub(category_pattern, f'category: {new_category}', front_matter, flags=re.MULTILINE)
    else:
        lines = front_matter.split('\n')
        lines.insert(1, f'category: {new_category}')
        new_front = '\n'.join(lines)
    
    new_content = f'---\n{new_front}\n---\n{body}'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True

def main():
    posts_dir = Path('_posts')
    if not posts_dir.exists():
        print("No _posts folder found.")
        return
    
    for md_file in posts_dir.glob('*.md'):
        print(f"Processing: {md_file.name}")
        with open(md_file, 'r', encoding='utf-8') as f:
            raw = f.read()
        
        # Extract title from front matter
        title_match = re.search(r'^title:\s*(.*)$', raw, re.MULTILINE)
        title = title_match.group(1).strip('"\'') if title_match else md_file.stem.replace('-', ' ').title()
        
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
                print(f"   ❌ Failed to update")
        else:
            print(f"   ⚠️  Could not determine category – no changes made")

if __name__ == '__main__':
    main()
