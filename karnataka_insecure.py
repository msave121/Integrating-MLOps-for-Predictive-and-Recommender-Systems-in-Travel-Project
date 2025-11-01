#!/usr/bin/env python3
"""
karnataka_open_details.py

- GETs the search page to collect cookies and any hidden form fields
- POSTS the search form for a district (preserving hidden fields)
- Extracts project IDs from the search results table
- For each project ID, fetches the project detail page and saves HTML to pages_html/{project_id}.html
- Stops after fetching/saving the detail pages (no parsing of details)
"""

from __future__ import annotations
import os
import time
import requests
from bs4 import BeautifulSoup
import urllib3
from typing import Dict, List

# --------- CONFIG ----------
DISTRICT = "Bengaluru Urban"                 # change to desired district
SEARCH_PAGE_URL = "https://rera.karnataka.gov.in/projectViewDetails"
SEARCH_POST_URL = "https://rera.karnataka.gov.in/projectDetails"   # endpoint used by site to load results
DETAILS_BASE_URL = "https://rera.karnataka.gov.in/projectViewDetails"
OUTPUT_DIR = "pages_html"                    # where detail pages will be saved
DELAY = 1.0                                  # seconds between requests
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
COOKIES: Dict[str, str] = {}                 # put auth cookies here if necessary
# If you want secure verification later, replace verify=False with verify=certifi.where()
VERIFY_SSL = False                           # set True if your environment supports certs
# ---------------------------

# Suppress the InsecureRequestWarning if VERIFY_SSL is False
if not VERIFY_SSL:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def mkdir_p(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def get_hidden_fields(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Collect all hidden input fields from the search page (useful for ASP.NET forms).
    """
    data: Dict[str, str] = {}
    for inp in soup.find_all("input", {"type": "hidden"}):
        name = inp.get("name")
        if not name:
            continue
        value = inp.get("value", "")
        data[name] = value
    return data


def fetch_search_page(session: requests.Session) -> BeautifulSoup:
    """
    GET the search page to collect cookies and hidden form values.
    """
    resp = session.get(SEARCH_PAGE_URL, verify=VERIFY_SSL, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


def post_search(session: requests.Session, hidden: Dict[str, str], district: str) -> BeautifulSoup:
    """
    POST the search form. We preserve hidden fields and add district and btn1.
    """
    # Build form data starting with hidden fields
    form = dict(hidden)  # copy
    # Some pages expect specific keys; include common items used earlier
    form.update({
        "district": district,
        "btn1": "Search",
        "action": "6"   # harmless for many endpoints; remove if it causes issues
    })

    resp = session.post(SEARCH_POST_URL, data=form, verify=VERIFY_SSL, timeout=30)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


def extract_project_ids_from_search(soup: BeautifulSoup) -> List[str]:
    """
    Find anchors with onclick that calls showFileApplicationPreview(this);
    the anchor's id attribute is the project id we need.
    """
    ids: List[str] = []
    for a in soup.find_all("a", onclick=True):
        onclick = a.get("onclick", "")
        if "showFileApplicationPreview" in onclick:
            pid = a.get("id")
            if pid and pid not in ids:
                ids.append(pid)
    return ids


def fetch_and_save_detail(session: requests.Session, project_id: str, out_dir: str) -> None:
    """
    Fetch project detail page and save raw HTML to out_dir/{project_id}.html
    """
    url = f"{DETAILS_BASE_URL}?projectId={project_id}"
    resp = session.get(url, verify=VERIFY_SSL, timeout=30)
    resp.raise_for_status()
    path = os.path.join(out_dir, f"{project_id}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(resp.text)


def main():
    mkdir_p(OUTPUT_DIR)

    with requests.Session() as session:
        session.headers.update(HEADERS)
        if COOKIES:
            session.cookies.update(COOKIES)

        print("GET search page to capture cookies & hidden fields...")
        try:
            search_page_soup = fetch_search_page(session)
        except Exception as e:
            print("Failed to GET search page:", e)
            return

        hidden_fields = get_hidden_fields(search_page_soup)
        print(f"Found {len(hidden_fields)} hidden form fields (including viewstate if present).")

        print(f"POST search for district: {DISTRICT}")
        try:
            results_soup = post_search(session, hidden_fields, DISTRICT)
        except Exception as e:
            print("Search POST failed:", e)
            return

        project_ids = extract_project_ids_from_search(results_soup)
        print(f"Found {len(project_ids)} project IDs in the search results.")

        if not project_ids:
            print("No project IDs found. If the site uses a different AJAX endpoint or requires extra fields,")
            print("inspect the Network tab in DevTools and replicate that request. This script tried to preserve hidden inputs.")
            return

        for idx, pid in enumerate(project_ids, start=1):
            print(f"[{idx}/{len(project_ids)}] Fetching detail page for project ID: {pid} ...")
            try:
                fetch_and_save_detail(session, pid, OUTPUT_DIR)
                print(f"Saved: {os.path.join(OUTPUT_DIR, pid + '.html')}")
            except Exception as e:
                print(f"  ! Failed to fetch/save {pid}: {e}")
            time.sleep(DELAY)

    print("All done — detail pages downloaded (or attempted).")


if __name__ == "__main__":
    main()
