#!/usr/bin/env python3
"""
Organize PDFs from Zotero storage into project paper folders
based on the .bib file and keyword matching
"""

import os
import shutil
import re

# ============================================================
# CONFIGURATION
# ============================================================
ZOTERO_STORAGE = os.environ.get("ZOTERO_STORAGE", os.path.expanduser("~/Zotero/storage"))
PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.getcwd())  # override via env var
BIB_FILE = os.path.join(PROJECT_ROOT, "zotero/AgriIoT-IDS-Research.bib")
# ============================================================

# Folder assignment rules based on keywords in title
FOLDER_RULES = {
    "01-Background": [
        "smart agriculture current state",
        "iot and ai in agriculture",
        "machine learning-based security solutions for iot networks",
        "survey on cybersecurity in iot",
        "systematic review of iot security",
        "comprehensive survey",
        "overview",
    ],
    "02-Agricultural-IoT-Security": [
        "smart agriculture",
        "agricultural iot",
        "securing smart agriculture",
        "cyber security in smart agriculture",
        "cybersecurity in smart agriculture",
        "cyber threat intelligence platform",
        "vulnerable-by-design iot sensor",
        "iot-driven farms",
        "precision agriculture",
    ],
    "03-Intrusion-Detection-Systems": [
        "intrusion detection system",
        "intrusion detection for iot",
        "network intrusion detection",
        "ids for iot",
        "iot-23 dataset",
        "cicids2017",
        "anomaly detection",
    ],
    "04-Machine-Learning-Methods": [
        "random forest",
        "deep learning",
        "neural network",
        "support vector machine",
        "machine learning based intrusion",
        "rnn anomaly",
        "cnn",
        "decision forest",
    ],
    "05-Datasets": [
        "cicids2017",
        "n-baiot",
        "iot-23",
        "dataset",
        "benchmark",
        "malware analysis on the iot-23",
        "detailed analysis of cicids",
    ],
}

def parse_bib(bib_file):
    """Parse .bib file and extract title + file paths"""
    entries = []
    
    with open(bib_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all entries
    entry_pattern = re.compile(r'@\w+\{([^,]+),(.+?)(?=\n@|\Z)', re.DOTALL)
    
    for match in entry_pattern.finditer(content):
        key = match.group(1).strip()
        body = match.group(2)
        
        # Extract title
        title_match = re.search(r'title\s*=\s*\{(.+?)\}', body, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""
        title = re.sub(r'\{|\}|\\relax', '', title).strip()
        
        # Extract file paths
        file_match = re.search(r'file\s*=\s*\{(.+?)\}', body, re.DOTALL)
        files = []
        if file_match:
            file_str = file_match.group(1)
            # Extract all PDF paths
            pdf_paths = re.findall(r'([^;{}]+\.pdf)', file_str, re.IGNORECASE)
            files = [p.strip() for p in pdf_paths if os.path.exists(p.strip())]
        
        if title:
            entries.append({
                "key": key,
                "title": title,
                "files": files
            })
    
    return entries

def assign_folder(title):
    """Assign a paper to a folder based on title keywords"""
    title_lower = title.lower()
    
    # Check each folder's rules
    scores = {}
    for folder, keywords in FOLDER_RULES.items():
        score = 0
        for kw in keywords:
            if kw.lower() in title_lower:
                score += 1
        if score > 0:
            scores[folder] = score
    
    if scores:
        # Return folder with highest score
        return max(scores, key=scores.get)
    
    return None

def find_pdf_in_storage(key, title):
    """Search Zotero storage for a PDF matching the key or title"""
    found_pdfs = []
    
    if not os.path.exists(ZOTERO_STORAGE):
        return found_pdfs
    
    # Search all subdirectories
    for root, dirs, files in os.walk(ZOTERO_STORAGE):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                # Match by title keywords
                title_words = title.lower().split()[:4]
                file_lower = file.lower()
                matches = sum(1 for w in title_words if w in file_lower)
                if matches >= 2:
                    found_pdfs.append(full_path)
    
    return found_pdfs

def organize():
    """Main organization function"""
    print("="*60)
    print("PAPER ORGANIZER")
    print("="*60)
    
    if not os.path.exists(BIB_FILE):
        print(f"❌ BibTeX file not found: {BIB_FILE}")
        return
    
    print(f"Reading: {BIB_FILE}")
    entries = parse_bib(BIB_FILE)
    print(f"Found {len(entries)} entries in .bib file\n")
    
    copied = 0
    not_found = []
    
    for entry in entries:
        title = entry["title"]
        key = entry["key"]
        files = entry["files"]
        
        # Assign folder
        folder = assign_folder(title)
        if not folder:
            continue
        
        dest_dir = os.path.join(PROJECT_ROOT, "papers", folder)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Try files from .bib first
        pdf_copied = False
        for pdf_path in files:
            if os.path.exists(pdf_path):
                filename = f"{key} - {title[:50]}.pdf"
                # Clean filename
                filename = re.sub(r'[<>:"/\\|?*{}]', '', filename)
                dest = os.path.join(dest_dir, filename)
                shutil.copy2(pdf_path, dest)
                print(f"✅ [{folder}] {title[:55]}")
                copied += 1
                pdf_copied = True
                break
        
        if not pdf_copied:
            # Try searching Zotero storage
            found = find_pdf_in_storage(key, title)
            if found:
                filename = f"{key} - {title[:50]}.pdf"
                filename = re.sub(r'[<>:"/\\|?*{}]', '', filename)
                dest = os.path.join(dest_dir, filename)
                shutil.copy2(found[0], dest)
                print(f"✅ [{folder}] {title[:55]} (found by search)")
                copied += 1
            else:
                not_found.append((folder, title))
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully copied: {copied} PDFs")
    
    if not_found:
        print(f"\n❌ PDFs not found for {len(not_found)} papers:")
        for folder, title in not_found:
            print(f"   [{folder}] {title[:60]}")
        print("\nFor missing PDFs:")
        print("  1. Download them manually")
        print(f"  2. Place in correct papers/ subfolder")
    
    print(f"\n{'='*60}")
    print("FOLDER SUMMARY")
    print(f"{'='*60}")
    for folder in FOLDER_RULES.keys():
        folder_path = os.path.join(PROJECT_ROOT, "papers", folder)
        if os.path.exists(folder_path):
            count = len([f for f in os.listdir(folder_path) if f.endswith('.pdf')])
            print(f"  {folder}: {count} PDFs")

if __name__ == "__main__":
    organize()