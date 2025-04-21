import fitz  # PyMuPDF
import re

def extract_sections_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    lines = []
    blocks_with_fonts = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    text_line = ""
                    font_sizes = []
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            text_line += text + " "
                            font_sizes.append(span["size"])
                    cleaned = text_line.strip()
                    if cleaned:
                        lines.append(cleaned)
                        blocks_with_fonts.append({
                            "text": cleaned,
                            "font_sizes": font_sizes,
                            "page": page_num
                        })

    # --- Title Extraction ---
    first_page = [b for b in blocks_with_fonts if b["page"] == 0]
    first_page = sorted(first_page, key=lambda x: max(x["font_sizes"]), reverse=True)
    title = ""
    for block in first_page:
        if len(block["text"].split()) > 3:
            title = block["text"]
            break

    # --- Detect All-Caps Headings (Except Abstract) ---
    def is_all_caps(line):
        return line.isupper() and len(line.split()) <= 6 and len(line) >= 5

    section_headings = []
    for i, line in enumerate(lines):
        if is_all_caps(line) and "abstract" not in line.lower():
            section_headings.append((line, i))

    # --- Extract Section Texts Between Headings ---
    section_texts = {}
    for idx, (heading, line_index) in enumerate(section_headings):
        next_index = section_headings[idx + 1][1] if idx + 1 < len(section_headings) else len(lines)
        section_body = "\n".join(lines[line_index + 1: next_index]).strip()
        section_texts[heading] = section_body

    # --- Abstract: Handle Separately ---
    abstract = "Not Found"
    for i, line in enumerate(lines[:40]):  # only search early lines
        if re.match(r"^(abstract|abstract:)$", line.strip().lower()):
            # Take next few lines until next ALL CAPS heading
            abstract_lines = []
            for j in range(i + 1, len(lines)):
                if is_all_caps(lines[j]):
                    break
                abstract_lines.append(lines[j])
            abstract = "\n".join(abstract_lines).strip()
            break

    # --- If not found, fallback: after title
    if abstract == "Not Found":
        for i, line in enumerate(lines[:40]):
            if title.lower() in line.lower():
                for j in range(i + 1, len(lines)):
                    if len(lines[j].split()) > 30:
                        abstract = lines[j]
                        break
                break

    # --- Normalize Section Keys ---
    def find_section(name_options):
        for key in section_texts.keys():
            if any(name in key.lower() for name in name_options):
                return section_texts[key]
        return "Not Found"

    introduction = find_section(["introduction"])
    conclusion = find_section(["conclusion"])

    return {
        "Title": title,
        "Abstract": abstract,
        "Introduction": introduction,
        "Conclusion": conclusion,
        "Detected_Headings": list(section_texts.keys())
    }

# Example usage
pdf_path = "data/target_paper.pdf"
sections = extract_sections_from_pdf(pdf_path)

print(f"\n=== Title ===\n{sections['Title']}")
print(f"\n=== Abstract ===\n{sections['Abstract'][:1000]}")
print(f"\n=== Introduction ===\n{sections['Introduction'][:1000]}")
print(f"\n=== Conclusion ===\n{sections['Conclusion'][:1000]}")
print(f"\n=== Detected Headings ===\n{sections['Detected_Headings']}")
