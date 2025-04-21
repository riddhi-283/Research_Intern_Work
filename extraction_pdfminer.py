import re
from pdfminer.high_level import extract_text

def extract_sections_from_pdf(pdf_path):
    # Extract all text from the PDF
    text = extract_text(pdf_path)
    
    # Normalize text for easier regex matching
    text = text.replace('\r', '\n')
    
    # Extract Title: Assume title is the first non-empty line (improve heuristics as needed)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    title = lines[0] if lines else ""
    
    # Define regex patterns for sections (case-insensitive)
    patterns = {
        'abstract': re.compile(r'(?i)\babstract\b(.*?)(?=\b(introduction|1\.|i\.|background)\b)', re.DOTALL),
        'introduction': re.compile(r'(?i)\bintroduction\b(.*?)(?=\b(conclusion|results|discussion|2\.|ii\.)\b)', re.DOTALL),
        'conclusion': re.compile(r'(?i)\bconclusion[s]?\b(.*?)(?=\b(references|acknowledgment|bibliography)\b|$)', re.DOTALL),
    }
    
    # Extract sections using regex
    abstract = patterns['abstract'].search(text)
    introduction = patterns['introduction'].search(text)
    conclusion = patterns['conclusion'].search(text)
    
    # Clean and return results
    return {
        'title': title,
        'abstract': abstract.group(1).strip() if abstract else "",
        'introduction': introduction.group(1).strip() if introduction else "",
        'conclusion': conclusion.group(1).strip() if conclusion else "",
    }

# Usage
pdf_path = "data/target_paper.pdf"
sections = extract_sections_from_pdf(pdf_path)
print("Title:\n", sections['title'])
print("\nAbstract:\n", sections['abstract'])
print("\nIntroduction:\n", sections['introduction'])
print("\nConclusion:\n", sections['conclusion'])
