from bs4 import BeautifulSoup
from curl_cffi import requests
import json

"""
base_url = "https://www.stepstone.de"
session = requests.Session()

def get_query_url(page_number=1):
    return (
        f"https://www.stepstone.de/jobs/software-entwickler-in-or-backend-entwickler-in-net-"
        f"or-backend-entwickler-in-c%23-or-backendentwickler-in-or-backendentwicklung-"
        f"or-python-entwickler-in-or-c%23-entwickler-in-or-net-entwickler-in/in-stuttgart-"
        f"or-t%C3%BCbingen-or-ulm?radius=50&page={page_number}&sort=2&action=sort_publish&q"
        f"=(Software-Entwickler%2fin)+OR+(Backend-Entwickler%2fin+.NET)"
        f"+OR+(Backend-Entwickler%2fin+C%23)+OR+(Backendentwickler%2fin)"
        f"+OR+(Backendentwicklung)+OR+(Python-Entwickler%2fin)+OR+(C%23-Entwickler%2fin)"
        f"+OR+(.NET-Entwickler%2fin)&searchOrigin=Resultlist_top-search"
    )

def fetch_html_text(page_number, session):
    query_url = get_query_url(page_number)
    fake_headers = {"Referer": base_url}

    try:
        raw_html = session.get(query_url, impersonate="chrome", timeout=15, headers=fake_headers)
        if raw_html.status_code != 200:
            print(f"Error: Stepstone responded with status {raw_html.status_code}")
            return
    except Exception as e:
        print(f"[Exception Error] - Details: {e}")
        return
    
    return raw_html.text

html_text = fetch_html_text(1, session)
soup = BeautifulSoup(html_text, 'lxml')
raw_job_links = soup.select('a[href^="/stellenangebote--"]')

print(f"Es wurden {len(raw_job_links)} Links gefunden.\n")

job_data = []

for link in raw_job_links:
    job_url = f"{base_url}{link['href']}"
    job_title = link.get_text(strip=True)
    job_dict = {"title": job_title, "url": job_url}
    job_data.append(job_dict)

# 3. Die komplette Liste sauber in eine Datei schreiben
with open("test.json", "w", encoding="utf-8") as file:
    # dump übersetzt die Python-Liste automatisch in perfekten Datei-Text
    # indent=4 macht es schön lesbar (mit Zeilenumbrüchen)
    # ensure_ascii=False sorgt dafür, dass ä, ö, ü nicht kaputt gehen
    json.dump(job_data, file, indent=4, ensure_ascii=False)


    def run_scraper(self, page_amount):
        while self.current_page != page_amount:
            html_text = self.fetch_html_text(self.current_page, self.session)

            if html_text is None:
                self.session = requests.Session()
                return # Handle response in GUI
            
            else:
                raw_job_links = self.extract_raw_links(html_text)
                job_urls = self.get_job_data(raw_job_links)
                filtered_jobs = self.filter_bad_words(job_urls)

                self.file_manager.populate_unfiltered_file(job_urls)
                self.file_manager.populate_unseen_file(filtered_jobs)

                self.anti_bot_sleep()

                self.current_page += 1

        jobs_to_check = self.file_manager.get_unseen_jobs()
        seen_links = self.file_manager.get_seen_links()
        print("Scrape finished.")
            
        return self.get_final_list_after_compare(jobs_to_check, seen_links)
"""

create_job_row
    x_btn = ...self.x.btn


process_job
