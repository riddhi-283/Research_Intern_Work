import fitz  # PyMuPDF

def extract_taic_from_pdf(pdf_path):
    """
    Extract Title, Abstract, Introduction, Conclusion from a PDF.
    This is a lightweight and heuristic-based extractor.
    """
    doc = fitz.open(pdf_path)
    full_text = " ".join(page.get_text() for page in doc)

    # Normalize
    full_text = full_text.replace("\n", " ").lower()

    def extract_section(section_name):
        try:
            start = full_text.index(section_name.lower())
            next_headers = ["introduction", "background", "related work", "conclusion", "references"]
            next_headers.remove(section_name.lower())
            next_positions = [full_text.find(h, start + 10) for h in next_headers if full_text.find(h, start + 10) != -1]
            end = min(next_positions) if next_positions else start + 1000
            return full_text[start:end].strip()
        except ValueError:
            return ""

    return {
        "title": doc.metadata.get("title", "Unknown Title"),
        "abstract": extract_section("abstract"),
        "introduction": extract_section("introduction"),
        "conclusion": extract_section("conclusion")
    }
