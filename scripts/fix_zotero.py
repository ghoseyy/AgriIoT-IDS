# #!/usr/bin/env python3
# """
# Zotero Library Metadata Fixer
# Fetches all items, finds ones missing metadata, and fixes them using DOI lookup.
# """

# import requests
# import json
# import time

# # ============================================================
# # CONFIGURATION - Fill these in before running
# # ============================================================
# API_KEY = os.environ.get("ZOTERO_API_KEY", "")  # Set ZOTERO_API_KEY in your environment
# USER_ID = "20553614"  # PASTE YOUR USER ID HERE (number from zotero.org/settings/keys)
# # ============================================================

# BASE_URL = f"https://api.zotero.org/users/{USER_ID}"
# HEADERS = {
#     "Zotero-API-Key": API_KEY,
#     "Zotero-API-Version": "3",
#     "Content-Type": "application/json"
# }

# def get_all_items():
#     """Fetch all items from Zotero library"""
#     print("Fetching all items from Zotero...")
#     items = []
#     start = 0
#     limit = 100
    
#     while True:
#         url = f"{BASE_URL}/items?limit={limit}&start={start}&itemType=-attachment"
#         response = requests.get(url, headers=HEADERS)
        
#         if response.status_code != 200:
#             print(f"Error: {response.status_code} - {response.text}")
#             break
            
#         batch = response.json()
#         if not batch:
#             break
            
#         items.extend(batch)
#         print(f"  Fetched {len(items)} items so far...")
        
#         if len(batch) < limit:
#             break
#         start += limit
#         time.sleep(0.5)
    
#     return items

# def check_missing_metadata(items):
#     """Find items with missing or incomplete metadata"""
#     missing = []
    
#     for item in items:
#         data = item.get("data", {})
#         item_type = data.get("itemType", "")
#         title = data.get("title", "")
        
#         # Skip attachments and notes
#         if item_type in ["attachment", "note"]:
#             continue
            
#         # Check for missing fields
#         has_author = bool(data.get("creators", []))
#         has_year = bool(data.get("date", ""))
#         has_journal = bool(data.get("publicationTitle", "") or 
#                           data.get("bookTitle", "") or 
#                           data.get("proceedingsTitle", ""))
#         has_doi = bool(data.get("DOI", ""))
        
#         if not has_author or not has_year or not has_journal:
#             missing.append({
#                 "key": item["key"],
#                 "title": title,
#                 "has_author": has_author,
#                 "has_year": has_year,
#                 "has_journal": has_journal,
#                 "has_doi": has_doi,
#                 "doi": data.get("DOI", "")
#             })
    
#     return missing

# def lookup_doi_metadata(doi):
#     """Look up metadata from CrossRef using DOI"""
#     url = f"https://api.crossref.org/works/{doi}"
#     try:
#         response = requests.get(url, timeout=10)
#         if response.status_code == 200:
#             return response.json().get("message", {})
#     except:
#         pass
#     return None

# def print_report(items, missing):
#     """Print a summary report"""
#     print("\n" + "="*60)
#     print("ZOTERO LIBRARY REPORT")
#     print("="*60)
#     print(f"Total items: {len(items)}")
#     print(f"Items with missing metadata: {len(missing)}")
    
#     if missing:
#         print("\nItems needing attention:")
#         print("-"*60)
#         for i, item in enumerate(missing, 1):
#             print(f"\n{i}. {item['title'][:70]}...")
#             print(f"   Key: {item['key']}")
#             print(f"   Missing: ", end="")
#             missing_fields = []
#             if not item['has_author']: missing_fields.append("authors")
#             if not item['has_year']: missing_fields.append("year")
#             if not item['has_journal']: missing_fields.append("journal")
#             print(", ".join(missing_fields))
#             if item['has_doi']:
#                 print(f"   DOI: {item['doi']} (can auto-fix!)")
#             else:
#                 print(f"   No DOI - needs manual fix")
    
#     # Count fixable vs manual
#     fixable = [i for i in missing if i['has_doi']]
#     manual = [i for i in missing if not i['has_doi']]
    
#     print("\n" + "="*60)
#     print(f"Auto-fixable (have DOI): {len(fixable)}")
#     print(f"Need manual fix (no DOI): {len(manual)}")
#     print("="*60)
    
#     return fixable, manual

# def auto_fix_item(item_key, doi):
#     """Try to fix item metadata using DOI"""
#     metadata = lookup_doi_metadata(doi)
#     if not metadata:
#         return False
    
#     # Build update payload
#     update = {}
    
#     # Get authors
#     authors = []
#     for author in metadata.get("author", []):
#         authors.append({
#             "creatorType": "author",
#             "firstName": author.get("given", ""),
#             "lastName": author.get("family", "")
#         })
#     if authors:
#         update["creators"] = authors
    
#     # Get year
#     published = metadata.get("published-print", metadata.get("published-online", {}))
#     date_parts = published.get("date-parts", [[]])[0]
#     if date_parts:
#         update["date"] = str(date_parts[0])
    
#     # Get journal
#     container = metadata.get("container-title", [])
#     if container:
#         update["publicationTitle"] = container[0]
    
#     # Get volume/pages
#     if metadata.get("volume"):
#         update["volume"] = str(metadata["volume"])
#     if metadata.get("page"):
#         update["pages"] = metadata["page"]
    
#     if not update:
#         return False
    
#     # Send update to Zotero
#     url = f"{BASE_URL}/items/{item_key}"
    
#     # First get current version
#     response = requests.get(url, headers=HEADERS)
#     if response.status_code != 200:
#         return False
    
#     current = response.json()
#     version = current["version"]
#     current_data = current["data"]
#     current_data.update(update)
    
#     # Patch the item
#     patch_headers = {**HEADERS, "If-Unmodified-Since-Version": str(version)}
#     patch_response = requests.patch(
#         url,
#         headers=patch_headers,
#         json=current_data
#     )
    
#     return patch_response.status_code == 204

# def export_bibtex():
#     """Export library as BibTeX"""
#     print("\nExporting library as BibTeX...")
#     url = f"{BASE_URL}/items?format=bibtex&limit=100"
#     response = requests.get(url, headers=HEADERS)
    
#     if response.status_code == 200:
#         with open("AgriIoT-IDS-fixed.bib", "w", encoding="utf-8") as f:
#             f.write(response.text)
#         print("✅ Exported to AgriIoT-IDS-fixed.bib")
#     else:
#         print(f"Export failed: {response.status_code}")

# def main():
#     if not USER_ID:
#         print("❌ Please add your USER_ID to the script first!")
#         print("   Find it at: https://www.zotero.org/settings/keys")
#         return
    
#     # Fetch all items
#     items = get_all_items()
    
#     if not items:
#         print("No items found or API error.")
#         return
    
#     # Check for missing metadata
#     missing = check_missing_metadata(items)
    
#     # Print report
#     fixable, manual = print_report(items, missing)
    
#     if not missing:
#         print("\n✅ All items have complete metadata!")
#         export_bibtex()
#         return
    
#     # Ask user what to do
#     if fixable:
#         print(f"\nWould you like to auto-fix {len(fixable)} items with DOIs?")
#         answer = input("Type 'yes' to fix, or 'no' to skip: ").strip().lower()
        
#         if answer == 'yes':
#             print("\nAuto-fixing items...")
#             fixed = 0
#             for item in fixable:
#                 print(f"  Fixing: {item['title'][:50]}...")
#                 if auto_fix_item(item['key'], item['doi']):
#                     print(f"  ✅ Fixed!")
#                     fixed += 1
#                 else:
#                     print(f"  ❌ Failed")
#                 time.sleep(0.5)
#             print(f"\nFixed {fixed}/{len(fixable)} items")
    
#     # Export BibTeX
#     export_bibtex()
    
#     # Print manual fix instructions
#     if manual:
#         print(f"\n⚠️  {len(manual)} items need manual fixing in Zotero:")
#         for item in manual:
#             print(f"   - {item['title'][:60]}...")
#         print("\nFor these: Right-click in Zotero → 'Retrieve Metadata for PDF'")

# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
"""
Zotero Library Metadata Fixer v2
"""

import requests
import json
import time

import os

API_KEY = os.environ.get("ZOTERO_API_KEY", "")
USER_ID = os.environ.get("ZOTERO_USER_ID", "20553614")  # Set ZOTERO_USER_ID or use default

BASE_URL = f"https://api.zotero.org/users/{USER_ID}"
HEADERS = {
    "Zotero-API-Key": API_KEY,
    "Zotero-API-Version": "3",
    "Content-Type": "application/json"
}

# Items to delete (junk)
JUNK_KEYS = [
    "2XLE9GPA",  # Email message received
    "8C6989QM",  # Hamilton cycles math paper
    "KZU69ZBA",  # My Library Zotero
    "DY64EEI7",  # Zotero better bibtex release
    "RHKLA68L",  # Zotero Connectors
    "Z4S6RI67",  # ML Security Solutions (webpage duplicate)
    "QZRS9UC4",  # AI Cybersecurity Smart Ag (webpage duplicate)
]

# Duplicate keys to delete (keep only one of each)
DUPLICATE_KEYS = [
    "QW22MEWV",  # duplicate Autonomous Attack Mitigation
    "8RNMK7QQ",  # duplicate Agentic AI Cyber Resilience
    "23N4HX5Z",  # duplicate Gymnasium
    "DZVRIIXA",  # duplicate Multi-Agent RL
    "YGD4YEQX",  # duplicate Deep RL
    "LFV3IMJ7",  # duplicate Gymnasium
    "BFU24V47",  # duplicate Autonomous Attack
    "25VPMDEI",  # duplicate Agentic AI
]

def delete_items(keys, label="items"):
    """Delete items by key"""
    print(f"\nDeleting {len(keys)} {label}...")
    deleted = 0
    for key in keys:
        url = f"{BASE_URL}/items/{key}"
        # Get version first
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 404:
            print(f"  ⚠️  {key} not found, skipping")
            continue
        if r.status_code != 200:
            print(f"  ❌ Failed to get {key}: {r.status_code}")
            continue
        version = r.json()["version"]
        title = r.json()["data"].get("title", "Unknown")[:50]
        
        # Delete
        del_headers = {**HEADERS, "If-Unmodified-Since-Version": str(version)}
        dr = requests.delete(url, headers=del_headers)
        if dr.status_code == 204:
            print(f"  ✅ Deleted: {title}")
            deleted += 1
        else:
            print(f"  ❌ Failed to delete {key}: {dr.status_code}")
        time.sleep(0.3)
    print(f"Deleted {deleted}/{len(keys)} {label}")

def lookup_crossref(doi):
    """Look up metadata from CrossRef"""
    url = f"https://api.crossref.org/works/{doi}"
    try:
        r = requests.get(url, timeout=10, 
                        headers={"User-Agent": "ZoteroFixer/1.0 (mailto:research@example.com)"})
        if r.status_code == 200:
            return r.json().get("message", {})
    except Exception as e:
        print(f"    CrossRef error: {e}")
    return None

def fix_item_metadata(key, doi):
    """Fix item metadata using CrossRef DOI lookup"""
    # Get current item
    url = f"{BASE_URL}/items/{key}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return False, f"Can't fetch item: {r.status_code}"
    
    item = r.json()
    version = item["version"]
    data = item["data"].copy()
    
    # Look up CrossRef
    meta = lookup_crossref(doi)
    if not meta:
        return False, "CrossRef lookup failed"
    
    # Update authors if missing
    if not data.get("creators"):
        authors = []
        for a in meta.get("author", []):
            authors.append({
                "creatorType": "author",
                "firstName": a.get("given", ""),
                "lastName": a.get("family", "")
            })
        if authors:
            data["creators"] = authors

    # Update date if missing
    if not data.get("date"):
        pub = meta.get("published-print", meta.get("published-online", 
              meta.get("created", {})))
        parts = pub.get("date-parts", [[]])[0]
        if parts:
            data["date"] = str(parts[0])

    # Update journal if missing
    if not data.get("publicationTitle"):
        containers = meta.get("container-title", [])
        if containers:
            data["publicationTitle"] = containers[0]

    # Update volume/pages
    if meta.get("volume") and not data.get("volume"):
        data["volume"] = str(meta["volume"])
    if meta.get("page") and not data.get("pages"):
        data["pages"] = meta["page"]

    # Send update - use PUT with full data
    put_headers = {**HEADERS, "If-Unmodified-Since-Version": str(version)}
    pr = requests.put(url, headers=put_headers, json=data)
    
    if pr.status_code == 204:
        return True, "Fixed!"
    else:
        return False, f"PUT failed: {pr.status_code} - {pr.text[:100]}"

def fix_no_doi_items():
    """Fix items without DOI using title search"""
    no_doi_keys = {
        "RIQKE5MN": "Machine Learning for Anomaly Detection in IoT networks Malware analysis IoT-23",
        "2DT3TWMH": "detailed analysis CICIDS2017 dataset designing Intrusion Detection Systems",
        "ZNDV2KN2": "Reinforcement Learning Cyber Defense AI Architectures Securing US Critical Infrastructure",
        "F2Z7UQHG": "AI Driven Self-Healing Cybersecurity Systems Agentic AI Adaptive Threat Response",
        "CWTJKD9F": "AI Driven Self-Healing Cybersecurity Systems Agentic AI Adaptive Threat Response",
        "9AFYG89C": "Reinforcement Learning Cyber Defense AI Architectures Securing US Critical Infrastructure",
        "WD8H2F75": "Reinforcement Learning Cyber Defense AI Architectures Securing US Critical Infrastructure",
        "5BNMBV4Z": "Survey Agentic AI Frameworks Network Security",
        "KCYLGSBT": "Large Language Models Cyber Security Systematic Literature Review",
    }
    
    print(f"\nSearching CrossRef by title for {len(no_doi_keys)} items...")
    fixed = 0
    
    for key, title_query in no_doi_keys.items():
        print(f"\n  Searching: {title_query[:60]}...")
        search_url = f"https://api.crossref.org/works?query={requests.utils.quote(title_query)}&rows=1"
        try:
            sr = requests.get(search_url, timeout=10,
                            headers={"User-Agent": "ZoteroFixer/1.0"})
            if sr.status_code == 200:
                items = sr.json().get("message", {}).get("items", [])
                if items:
                    doi = items[0].get("DOI", "")
                    if doi:
                        print(f"  Found DOI: {doi}")
                        success, msg = fix_item_metadata(key, doi)
                        if success:
                            print(f"  ✅ {msg}")
                            fixed += 1
                        else:
                            print(f"  ❌ {msg}")
                    else:
                        print(f"  ❌ No DOI in result")
                else:
                    print(f"  ❌ No results found")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        time.sleep(1)
    
    return fixed

def export_bibtex():
    """Export library as BibTeX"""
    print("\nExporting clean BibTeX...")
    all_bibtex = []
    start = 0
    limit = 100
    
    while True:
        url = f"{BASE_URL}/items?format=bibtex&limit={limit}&start={start}"
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200 or not r.text.strip():
            break
        all_bibtex.append(r.text)
        if len(r.text.split("@")) < limit:
            break
        start += limit
        time.sleep(0.5)
    
    with open("AgriIoT-IDS-clean.bib", "w", encoding="utf-8") as f:
        f.write("\n".join(all_bibtex))
    print("✅ Exported to AgriIoT-IDS-clean.bib")

def main():
    if not USER_ID:
        print("❌ Please add your USER_ID to the script!")
        return
    
    print("="*60)
    print("ZOTERO LIBRARY CLEANER v2")
    print("="*60)
    
    # Step 1: Delete junk
    print("\nStep 1: Deleting junk items...")
    delete_items(JUNK_KEYS, "junk items")
    
    # Step 2: Delete duplicates
    print("\nStep 2: Deleting duplicate items...")
    delete_items(DUPLICATE_KEYS, "duplicates")
    
    # Step 3: Fix items with DOI
    print("\nStep 3: Fixing items with DOI...")
    doi_items = {
        "DWH3RA9N": "10.48550/arXiv.2505.19837",
        "8SDY5JNV": "10.48550/arXiv.2111.02445",
        "GDEFI783": "10.48550/arXiv.2512.22883",
        "YTIJEFCN": "10.1007/978-3-030-97532-6_4",
        "XX3ACKW3": "10.48550/arXiv.2407.17032",
    }
    
    fixed_doi = 0
    for key, doi in doi_items.items():
        r = requests.get(f"{BASE_URL}/items/{key}", headers=HEADERS)
        if r.status_code == 404:
            continue
        title = r.json()["data"].get("title", "Unknown")[:50]
        print(f"  Fixing: {title}...")
        success, msg = fix_item_metadata(key, doi)
        print(f"  {'✅' if success else '❌'} {msg}")
        if success:
            fixed_doi += 1
        time.sleep(0.5)
    
    print(f"\nFixed {fixed_doi}/{len(doi_items)} DOI items")
    
    # Step 4: Fix items without DOI using title search
    print("\nStep 4: Searching for missing DOIs by title...")
    fixed_title = fix_no_doi_items()
    print(f"\nFixed {fixed_title} items via title search")
    
    # Step 5: Export
    print("\nStep 5: Exporting clean BibTeX...")
    export_bibtex()
    
    print("\n" + "="*60)
    print("DONE!")
    print("="*60)
    print(f"✅ Deleted junk and duplicates")
    print(f"✅ Fixed metadata where possible")
    print(f"✅ Exported to AgriIoT-IDS-clean.bib")
    print(f"\n⚠️  For remaining items: Right-click in Zotero → Retrieve Metadata for PDF")

if __name__ == "__main__":
    main()