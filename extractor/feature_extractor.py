# extractor/feature_extractor.py
import openai
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI()
def call_openai(prompt, model="gpt-3.5-turbo", temperature=0.5):
    response = client.responses.create(
        model=model,
        input=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.output_text

def generate_faceted_summary(taic_dict):
    prompt_template = Path("prompts/generate_faceted_summary.txt").read_text()
    prompt = prompt_template.format(
        title=taic_dict.get("title", ""),
        abstract=taic_dict.get("abstract", ""),
        introduction=taic_dict.get("introduction", ""),
        conclusion=taic_dict.get("conclusion", ""),
        objective="", method="", findings="", contribution="", keywords=""
    )
    return call_openai(prompt)

def generate_relationship(title_A, author_A, year_A, faceted_A,
                          title_B, author_B, year_B, faceted_B,
                          citation_marker="[1]", spans=None):
    prompt_template = Path("prompts/infer_relationship.txt").read_text()
    spans_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(spans or [])])
    prompt = prompt_template.format(
        title_A=title_A,
        author_A=author_A,
        year_A=year_A,
        faceted_A=faceted_A,
        title_B=title_B,
        author_B=author_B,
        year_B=year_B,
        faceted_B=faceted_B,
        citation_marker=citation_marker,
        span_1=spans[0] if spans else "",
        span_2=spans[1] if spans and len(spans) > 1 else ""
    )
    return call_openai(prompt)

def generate_enriched_usage(author_B, year_B, relations, citation_spans):
    prompt_template = Path("prompts/enrich_usage.txt").read_text()
    relation_text = "\n".join(relations)
    span_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(citation_spans)])
    prompt = prompt_template.format(
        author_B=author_B,
        year_B=year_B,
        relations=relation_text,
        span_1=citation_spans[0] if citation_spans else "",
        span_2=citation_spans[1] if citation_spans and len(citation_spans) > 1 else ""
    )
    return call_openai(prompt)

def generate_main_idea(title, faceted_summary, related_work_section):
    prompt_template = Path("prompts/generate_main_idea.txt").read_text()
    prompt = prompt_template.format(
        title=title,
        faceted_summary=faceted_summary,
        related_work_section=related_work_section,
        main_ideas=""
    )
    return call_openai(prompt)

def generate_related_work_section(title, abstract, introduction, conclusion,
                                   main_idea, cited_papers, relationships):
    prompt_template = Path("prompts/generate_related_work.txt").read_text()

    cited_str = "\n\n".join([
        f"Title: {cp['title']}\nAuthors: {', '.join(cp['authors'])}\nYear: {cp['year']}\nFaceted Summary: {cp['faceted']}\nUsage: {cp['usage']}"
        for cp in cited_papers
    ])
    relationship_str = "\n\n".join(relationships)

    prompt = prompt_template.format(
        title=title,
        abstract=abstract,
        introduction=introduction,
        conclusion=conclusion,
        main_idea=main_idea,
        cited_info=cited_str,
        relationships=relationship_str
    )
    return call_openai(prompt, model="gpt-4", temperature=0.3)