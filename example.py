from scraper import Scraper
from extract import Extractor
from filters import title_filter, keywords_filter, abstract_filter
from selector import Selector
from utils import *
import os


years = list(map(str, range(2025, 2026)))

conferences = [
    "ICLR",
    # "ICML",
    # "EMNLP",
    # "ACL",
    # "arXiv",
]

# AND outside, OR inside
# Example: ["a", ["b", "c"], "d"] means: (a) AND (b OR c) AND (d)
keywords = [
    ["Large Language Model", "LLM"],
    ["Game Theory", "equilibrium", "Nash"],
    ["Reinforcement Learning", "RL", "Multi-Agent"],
]


def modify_paper(paper):
    forum_id = paper.forum
    paper.forum = f"https://openreview.net/forum?id={forum_id}"
    pdf_url = f"https://openreview.net{unwrap_value(paper.content['pdf'])}"
    paper.content["pdf"] = pdf_url
    # Download PDF
    pdf_filename = f"{forum_id}.pdf"
    pdf_path = download_pdf(pdf_url, dest_folder="pdfs", filename=pdf_filename)
    if pdf_path:
        paper.content["pdf_local"] = os.path.abspath(pdf_path)
    else:
        paper.content["pdf_local"] = ""
    # Fetch BibTeX only for filtered/selected papers
    paper.content["bibtex"] = fetch_bibtex_from_data_bibtex(forum_id)
    return paper


extractor = Extractor(
    fields=["forum"],
    subfields={
        "content": [
            "title",
            "authors",
            "keywords",
            "abstract",
            "pdf",
            "pdf_local",
            "match",
            "bibtex",
        ]
    },
)

selector = Selector()
scraper = Scraper(
    conferences=conferences,
    years=years,
    keywords=keywords,
    extractor=extractor,
    fpath="/home/p3dr4m0098/HWs/NLPLAB/Scrapper/mine/openreview_scraper/example.csv",
    fns=[modify_paper],
    # Set to None to skip selection;
    # use instance of Selector, i.e. selector to enable selection
    selector=None,
    filter_mode="MIX",
)

scraper.add_filter(title_filter)
scraper.add_filter(keywords_filter)
scraper.add_filter(abstract_filter)

scraper()

save_papers(scraper.papers, fpath="papers.pkl")
saved_papers = load_papers(fpath="papers.pkl")
