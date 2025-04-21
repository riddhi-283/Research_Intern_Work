import requests
import xml.etree.ElementTree as ET

def extract_sections_from_pdf(pdf_path, grobid_url="http://localhost:8070/api/processFulltextDocument"):
    # Step 1: Send PDF to Grobid
    with open(pdf_path, 'rb') as pdf_file:
        response = requests.post(
            grobid_url,
            files={'input': pdf_file},
            data={'consolidateHeader': '1', 'consolidateCitations': '0'}
        )
    if response.status_code != 200:
        raise Exception("Failed to process PDF with Grobid:", response.text)

    # Step 2: Parse the XML
    root = ET.fromstring(response.text)

    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    result = {}

    # Extract title
    title_elem = root.find(".//tei:titleStmt/tei:title", ns)
    if title_elem is not None:
        result['title'] = title_elem.text.strip()

    # Extract abstract
    abstract_elem = root.find(".//tei:abstract", ns)
    if abstract_elem is not None:
        result['abstract'] = " ".join(abstract_elem.itertext()).strip()

    # Extract body content and specific sections
    for div in root.findall(".//tei:div", ns):
        head = div.find("tei:head", ns)
        if head is not None:
            section_title = head.text.strip().upper()

            # Match based on capitalized headings
            if "INTRODUCTION" in section_title:
                result['introduction'] = " ".join(div.itertext()).strip()
            elif "CONCLUSION" in section_title or "CONCLUSIONS" in section_title:
                result['conclusion'] = " ".join(div.itertext()).strip()

    return result


# Example usage
pdf_file_path = "target_paper.pdf"
sections = extract_sections_from_pdf(pdf_file_path)

for sec, content in sections.items():
    print(f"\n--- {sec.upper()} ---\n")
    print(content[:1000], "...")  # Print first 1000 chars for readability
