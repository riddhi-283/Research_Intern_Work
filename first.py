# related_work_generator/main.py

"""
Main pipeline script for the implementation of:
"Explaining Relationships Among Research Papers" (2024).
"""

import os
import json
from extractor.taic_extractor import extract_taic_from_pdf
from extractor.paper_retriever import get_papers_from_references
from extractor.feature_extractor import (
    generate_faceted_summary,
    generate_relationship,
    generate_enriched_usage,
    generate_main_idea,
    generate_related_work_section
)

# Define file paths
target_pdf_path = "data/target_paper.pdf"
cited_papers_dir = "data/cited_papers"
output_path = "output/related_work.txt"

print("Step 1: Extract TAIC from target paper...")
taic_sections = extract_taic_from_pdf(target_pdf_path)
print(json.dumps(taic_sections, indent=2))

# (Optional) Extract and download cited papers (mocked here)
cited_papers = [
    {
        "title": "Automatic generation of related work through summarizing citations",
        "authors": ["Chen", "Zhuge"],
        "year": "2019",
        "abstract": "This paper proposes a method to generate related work using citation summaries."
    },
    {
        "title": "Relation-aware Related work Generator",
        "authors": ["Chen", "et al."],
        "year": "2021",
        "abstract": "This model captures relations between papers and generates related work sections."
    }
]

print("Step 2: Generate faceted summaries...")
target_faceted = generate_faceted_summary(taic_sections)
for cited in cited_papers:
    cited["faceted"] = generate_faceted_summary({"title": cited["title"], "abstract": cited["abstract"]})

print("Step 3: Generate citation relationships...")
relationships = []
for cited in cited_papers:
    rel = generate_relationship(target_faceted, cited["faceted"])
    relationships.append(rel)

print("Step 4: Generate citation usages...")
for cited in cited_papers:
    cited["usage"] = generate_enriched_usage(cited["faceted"], relationships)

print("Step 5: Generate main idea plan...")
main_idea = generate_main_idea(taic_sections)

print("Step 6: Generate final related work section...")
related_work = generate_related_work_section(taic_sections, main_idea, cited_papers, relationships)

os.makedirs("output", exist_ok=True)
with open(output_path, "w") as f:
    f.write(related_work)

print("\n--- Final Related Work Section ---\n")
print(related_work)

# extractor/taic_extractor.py
import fitz  # PyMuPDF

def extract_taic_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = " ".join(page.get_text() for page in doc)
    def extract_between(section_name):
        try:
            start = full_text.lower().index(section_name.lower())
            end = full_text.lower().index("\n", start + len(section_name))
            return full_text[start:end].strip()
        except:
            return ""

    return {
        "title": extract_between("title"),
        "abstract": extract_between("abstract"),
        "introduction": extract_between("introduction"),
        "conclusion": extract_between("conclusion")
    }

# extractor/paper_retriever.py

def get_papers_from_references(target_pdf_path, save_dir):
    # Placeholder for future implementation using Semantic Scholar API
    return []

# extractor/feature_extractor.py
import openai
from pathlib import Path

def call_openai(prompt, model="gpt-3.5-turbo", temperature=0.5):
    res = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return res["choices"][0]["message"]["content"].strip()

def generate_faceted_summary(taic):
    template = Path("prompts/generate_faceted_summary.txt").read_text()
    return call_openai(template.format(**taic))

def generate_relationship(faceted_a, faceted_b):
    template = Path("prompts/infer_relationship.txt").read_text()
    return call_openai(template.format(facet_a=faceted_a, facet_b=faceted_b))

def generate_enriched_usage(facet, relations):
    template = Path("prompts/enrich_usage.txt").read_text()
    rel_str = "\n".join(relations)
    return call_openai(template.format(facet=facet, relations=rel_str))

def generate_main_idea(taic):
    template = Path("prompts/generate_main_idea.txt").read_text()
    return call_openai(template.format(**taic))

def generate_related_work_section(taic, main_idea, cited_papers, relationships):
    template = Path("prompts/generate_related_work.txt").read_text()
    cited_info = "\n".join([
        f"{i+1}. {p['title']} by {', '.join(p['authors'])} ({p['year']})\n{p['faceted']}\n<Usage> {p['usage']}" 
        for i, p in enumerate(cited_papers)
    ])
    rel_info = "\n".join(relationships)
    return call_openai(template.format(
        title=taic["title"],
        abstract=taic["abstract"],
        introduction=taic["introduction"],
        conclusion=taic["conclusion"],
        main_idea=main_idea,
        cited_info=cited_info,
        relationships=rel_info
    ), model="gpt-4", temperature=0.3)

# prompts/generate_faceted_summary.txt
Title: {title}
Abstract: {abstract}
Introduction: {introduction}
Conclusion: {conclusion}

What are the objective, method, findings, contributions and keywords of the paper above? Answer in this format:
Objective: ...
Method: ...
Findings: ...
Contribution: ...
Keywords: A; B; C

# prompts/infer_relationship.txt
Faceted summary of A:
{facet_a}

Faceted summary of B:
{facet_b}

Very briefly explain the relationship between Paper A and Paper B. TLDR:

# prompts/enrich_usage.txt
Faceted summary of B:
{facet}

How B is cited by others:
{relations}

Summarize how B is known and commonly cited. Format: "B is known for ... and cited for ..."

# prompts/generate_main_idea.txt
Title: {title}
Abstract: {abstract}
Introduction: {introduction}
Conclusion: {conclusion}

Write a short summary of the main idea of the related work section.

# prompts/generate_related_work.txt
Title: {title}
Abstract: {abstract}
Introduction: {introduction}
Conclusion: {conclusion}

Main idea of the related work section:
{main_idea}

List of cited papers:
{cited_info}

Relationships among papers:
{relationships}

Write a related work section that includes all papers, integrates their content, and uses transitions. Do not list summaries. Use paragraph structure.
