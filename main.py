# related_work_generator/main.py

import os
import json
from pathlib import Path
from extractor.taic_extractor import extract_taic_from_pdf
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
print(taic_sections)
# print(json.dumps(taic_sections, indent=2))

print("Step 2: Extract TAIC & generate faceted summaries for cited papers...")
cited_papers = []
cited_paths = list(Path(cited_papers_dir).glob("*.pdf"))

for pdf in cited_paths:
    print(f"Processing cited paper: {pdf.name}")
    taic = extract_taic_from_pdf(str(pdf))
    print(taic)
    faceted = generate_faceted_summary(taic)
    print(faceted)
    # cited_papers.append({
    #     "title": taic.get("title", pdf.stem),
    #     "authors": ["Author"],  # Placeholder unless you want to extract authors
    #     "year": "2023",  # You can modify this to extract from metadata if needed
    #     "abstract": taic.get("abstract", ""),
    #     "faceted": faceted,
    #     "spans": [f"{pdf.stem} (2023) discusses relevant ideas in citation generation."]
    # })

print("Step 3: Generate faceted summary for target paper...")
target_faceted = generate_faceted_summary(taic_sections)
print(target_faceted)

# print("Step 4: Generate relationships...")
# relationships = []
# for paper in cited_papers:
#     title_A = taic_sections["title"]
#     author_A = "TargetAuthor"
#     year_A = "2024"
#     title_B = paper["title"]
#     author_B = paper["authors"][0]
#     year_B = paper["year"]
#     citation_marker = f"{author_B} et al. ({year_B})"

#     rel = generate_relationship(
#         title_A, author_A, year_A, target_faceted,
#         title_B, author_B, year_B, paper["faceted"],
#         citation_marker=citation_marker,
#         spans=paper["spans"]
#     )
#     relationships.append(rel)

# print("Step 5: Generate enriched usage descriptions...")
# for paper in cited_papers:
#     paper["usage"] = generate_enriched_usage(
#         paper["authors"][0],
#         paper["year"],
#         relationships,
#         paper["spans"]
#     )

# print("Step 6: Generate main idea...")
# main_idea = generate_main_idea(
#     taic_sections["title"],
#     target_faceted,
#     "These papers are relevant to our work in citation generation and related work modeling."
# )

# print("Step 7: Generate final related work section...")
# related_work = generate_related_work_section(
#     title=taic_sections["title"],
#     abstract=taic_sections["abstract"],
#     introduction=taic_sections["introduction"],
#     conclusion=taic_sections["conclusion"],
#     main_idea=main_idea,
#     cited_papers=cited_papers,
#     relationships=relationships
# )

# os.makedirs("output", exist_ok=True)
# with open(output_path, "w") as f:
#     f.write(related_work)

# print("\n--- Final Related Work Section ---\n")
# print(related_work)
