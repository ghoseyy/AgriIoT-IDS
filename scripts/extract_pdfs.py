from pathlib import Path
import fitz  # PyMuPDF

base = Path("papers")

for pdf in base.rglob("*.pdf"):
    txt_path = pdf.with_suffix(".txt")

    doc = fitz.open(pdf)
    text = "\n".join(page.get_text() for page in doc)

    txt_path.write_text(text, encoding="utf-8")

    print(f"Extracted: {pdf.name}")