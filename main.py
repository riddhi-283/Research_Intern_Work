# related_work_generator/main.py

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

# Mock cited papers (for demo)
cited_papers = [
    {
        "title": "Automatic generation of related work through summarizing citations",
        "authors": ["Chen", "Zhuge"],
        "year": "2019",
        "abstract": "This paper proposes a method to generate related work using citation summaries.",
        "spans": ["Chen and Zhuge (2019) introduced a citation-based summarization approach."]
    },
    {
        "title": "Relation-aware Related work Generator",
        "authors": ["Chen", "et al."],
        "year": "2021",
        "abstract": "This model captures relations between papers and generates related work sections.",
        "spans": ["Chen et al. (2021) proposed an abstractive generator with relational awareness."]
    }
]

print("Step 2: Generate faceted summaries...")
target_faceted = generate_faceted_summary(taic_sections)

for paper in cited_papers:
    paper["faceted"] = generate_faceted_summary({"title": paper["title"], "abstract": paper["abstract"], "introduction": "", "conclusion": ""})

print("Step 3: Generate relationships...")
relationships = []
for paper in cited_papers:
    title_A = taic_sections["title"]
    author_A = "TargetAuthor"
    year_A = "2024"
    title_B = paper["title"]
    author_B = paper["authors"][0]
    year_B = paper["year"]
    citation_marker = f"{author_B} et al. ({year_B})"

    rel = generate_relationship(
        title_A, author_A, year_A, target_faceted,
        title_B, author_B, year_B, paper["faceted"],
        citation_marker=citation_marker,
        spans=paper["spans"]
    )
    relationships.append(rel)

print("Step 4: Generate enriched usage descriptions...")
for paper in cited_papers:
    paper["usage"] = generate_enriched_usage(
        paper["authors"][0],
        paper["year"],
        relationships,
        paper["spans"]
    )

print("Step 5: Generate main idea...")
main_idea = generate_main_idea(
    taic_sections["title"],
    target_faceted,
    "The following papers are relevant to our work in citation generation and relationship modeling..."
)

print("Step 6: Generate final related work section...")
related_work = generate_related_work_section(
    title=taic_sections["title"],
    abstract=taic_sections["abstract"],
    introduction=taic_sections["introduction"],
    conclusion=taic_sections["conclusion"],
    main_idea=main_idea,
    cited_papers=cited_papers,
    relationships=relationships
)

os.makedirs("output", exist_ok=True)
with open(output_path, "w") as f:
    f.write(related_work)

print("\n--- Final Related Work Section ---\n")
print(related_work)
