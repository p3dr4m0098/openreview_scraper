import openreview
import csv
from config import EMAIL, PASSWORD
import dill
import requests
import re
import html as html_lib
from urllib.parse import unquote
import os


def get_client():
    """
    Returns a tuple of (client_v1, client_v2) for both OpenReview API versions.
    """
    client_v1 = openreview.Client(
        baseurl="https://api.openreview.net", username=EMAIL, password=PASSWORD
    )

    client_v2 = openreview.api.OpenReviewClient(
        baseurl="https://api2.openreview.net", username=EMAIL, password=PASSWORD
    )

    return client_v1, client_v2


def papers_to_list(papers):
    all_papers = []
    for grouped_venues in papers.values():
        for venue_papers in grouped_venues.values():
            for paper in venue_papers:
                all_papers.append(paper)
    return all_papers


def to_csv(papers_list, fpath):
    def write_csv():
        with open(fpath, "a+") as fp:
            fp.seek(0, 0)  # seek to beginning of file and then read
            previous_contents = fp.read()
            writer = csv.DictWriter(fp, fieldnames=field_names)
            if previous_contents.strip() == "":
                writer.writeheader()
            writer.writerows(papers_list)

    if len(papers_list) > 0:
        field_names = list(
            papers_list[0].keys()
        )  # choose one of the papers, get all the keys as they'll be same for rest of them
        write_csv()


def save_papers(papers, fpath):
    with open(fpath, "wb") as fp:
        dill.dump(papers, fp)
        print(f"Papers saved at: {fpath}")


def load_papers(fpath):
    with open(fpath, "rb") as fp:
        papers = dill.load(fp)
    print(f"Papers loaded from: {fpath}")
    return papers


def fetch_html(forum_id):
    url = f"https://openreview.net/forum?id={forum_id}&format=bibtex"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text.strip()
        else:
            print(f"Failed to fetch html for {forum_id}: {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error fetching html for {forum_id}: {e}")
        return ""


def fetch_bibtex_from_data_bibtex(forum_id):
    """
    Fetches and decodes the BibTeX entry from the `data-bibtex` attribute on the OpenReview forum page.
    """
    url = f"https://openreview.net/forum?id={forum_id}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch HTML for {forum_id}: {response.status_code}")
            return ""

        html_text = response.text

        # Find data-bibtex="..."
        match = re.search(r'data-bibtex="([^"]+)"', html_text)
        if not match:
            print(f"No data-bibtex found in HTML for {forum_id}")
            return ""

        encoded_bibtex = match.group(1)
        decoded_bibtex = unquote(encoded_bibtex)

        return decoded_bibtex.strip()

    except Exception as e:
        print(f"Error fetching bibtex for {forum_id}: {e}")
        return ""


def build_bibtex_from_note(note, venue_name="OpenReview"):
    """
    Build a BibTeX entry from an OpenReview note object.
    """
    try:
        import datetime

        # Helper to extract value if wrapped in {"value": ...}
        def extract_value(field):
            if isinstance(field, dict) and "value" in field:
                return field["value"]
            return field

        # Extract metadata with value-unpacking
        authors_raw = note.content.get("authors", [])
        authors = extract_value(authors_raw)
        if isinstance(authors, list):
            authors = [extract_value(a) for a in authors]
        else:
            authors = [str(authors)]
        authors_str = " and ".join(authors)

        title_raw = note.content.get("title", "No Title")
        title = extract_value(title_raw).strip()

        # Get publication year
        if hasattr(note, "tcdate") and isinstance(note.tcdate, int):
            year = datetime.datetime.fromtimestamp(note.tcdate / 1000).year
        else:
            year = "????"

        # Construct OpenReview URL
        url = f"https://openreview.net/forum?id={note.forum}"

        # Create citation key: lastnameYEARkeyword
        first_author_lastname = authors[0].split()[-1].lower() if authors else "anon"
        title_words = [w for w in title.lower().split() if w.isalnum()]
        suffix_word = title_words[0] if title_words else "paper"
        key = f"{first_author_lastname}{year}{suffix_word}"

        # Compose BibTeX entry
        bibtex = f"""@inproceedings{{
  {key},
  title={{ {title} }},
  author={{ {authors_str} }},
  booktitle={{ {venue_name} }},
  year={{ {year} }},
  url={{ {url} }}
}}"""
        return bibtex

    except Exception as e:
        return f"Error: {str(e)}"


def download_pdf(pdf_url, dest_folder="pdfs", filename=None):
    """
    Downloads a PDF from the given URL to the specified folder.
    If filename is not provided, it will use the last part of the URL.
    Returns the path to the saved PDF.
    """
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    if filename is None:
        filename = pdf_url.split("/")[-1]
    dest_path = os.path.join(dest_folder, filename)
    try:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            with open(dest_path, "wb") as f:
                f.write(response.content)
            return dest_path
        else:
            print(f"Failed to download PDF: {pdf_url} (status {response.status_code})")
            return None
    except Exception as e:
        print(f"Error downloading PDF {pdf_url}: {e}")
        return None


def unwrap_value(value):
    """
    Unwraps a value that may be wrapped in a {"value": ...} dict.
    Recursively unwraps until the final value is returned.
    """
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    return value