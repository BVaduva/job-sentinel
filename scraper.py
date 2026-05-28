from bs4 import BeautifulSoup
from curl_cffi import requests
import random
import time
import re
from file_manager import FileManager
from queue import Queue


class ScraperEngine:
    def __init__(self):
        self.base_url = "https://www.stepstone.de"
        self.session = requests.Session()
        self.file_manager = FileManager()
        self.current_page = 1
        self.stop_signal = False


    def run_scraper(self, page_amount, job_queue: Queue):
        seen_links = self.file_manager.get_seen_links()
        jobs_found = 0
        filtered_jobs = 0
        seen_jobs = 0

        while self.current_page <= page_amount:
            if self.stop_signal:
                break 
            print(f"Scraping page: {self.current_page}...")
            html_text = self.fetch_html_text(self.current_page, self.session)

            if html_text is None:
                self.session = requests.Session()
                return # Handle response in GUI
            
            else:
                # raw_job_links = self.extract_raw_links(html_text)
                # job_urls = self.get_job_data(raw_job_links)
                raw_job_cards = self.extract_job_cards(html_text)
                job_urls = self.get_job_data(raw_job_cards)
                unseen_jobs = self.filter_bad_words(job_urls)

                self.file_manager.populate_unfiltered_file(job_urls) # Populate until ~ 20k+
                self.file_manager.populate_unseen_file(unseen_jobs)

                current_batch = self.get_list_after_compare(unseen_jobs, seen_links)
                jobs_found += len(job_urls)
                seen_jobs += (len(unseen_jobs) - len(current_batch))
                filtered_jobs += (len(job_urls) - len(unseen_jobs))
                package = {
                    "jobs": current_batch,
                    "scraped_jobs_amount": jobs_found,
                    "filtered_jobs_amount": filtered_jobs,
                    "seen_jobs_amount": seen_jobs,
                    "current_page": self.current_page
                }
                
                job_queue.put(package)
                self.anti_bot_sleep()
                self.current_page += 1

        print("Scrape finished.")


    #region HELPERS
    # Backend Allround
    
    def get_query_url(self, page_number=1):
        return (
            f"https://www.stepstone.de/jobs/software-entwickler-in-or-backend-entwickler-in-net-"
            f"or-backend-entwickler-in-c%23-or-backendentwickler-in-or-backendentwicklung-"
            f"or-python-entwickler-in-or-c%23-entwickler-in-or-net-entwickler-in/in-stuttgart-"
            f"or-t%C3%BCbingen-or-ulm?radius=50&page={page_number}&sort=2&action=sort_publish&q"
            f"=(Software-Entwickler%2fin)+OR+(Backend-Entwickler%2fin+.NET)"
            f"+OR+(Backend-Entwickler%2fin+C%23)+OR+(Backendentwickler%2fin)"
            f"+OR+(Backendentwicklung)+OR+(Python-Entwickler%2fin)+OR+(C%23-Entwickler%2fin)"
            f"+OR+(.NET-Entwickler%2fin)&searchOrigin=Resultlist_top-search&di=IT"
        )
    

    # Backend C#/.NET ASP
    """
    def get_query_url(self, page_number=1):
        return (
            f"https://www.stepstone.de/jobs/netc%23c%23-netc%23-developerc%23-software-architectnet-"
            f"programmierungnet-backend-entwickler-inbackend-developer-c%23aspnet/in-stuttgart-or-ulm-"
            f"or-t%C3%BCbingen?radius=50&page={page_number}&sort=2&action=sort_publish&q="
            f"(.NET)%2c(C%23)%2c(C%23+.Net)%2c(C%23+Developer)%2c(C%23+Software+Architect)"
            f"%2c(.NET-Programmierung)%2c(.NET+Backend-Entwickler%2fin)%2c(Backend+Developer+C%23)%2c(ASP.NET)"
            f"&searchOrigin=Resultlist_top-search&di=IT"
        )
    """

    def fetch_html_text(self, page_number, session, max_retries=3):
        query_url = self.get_query_url(page_number)
        fake_headers = {"Referer": self.base_url}

        for attempt in range(max_retries):
            try:
                raw_html = session.get(query_url, impersonate="chrome", timeout=20, headers=fake_headers)
                
                if raw_html.status_code == 200:
                    return raw_html.text
                else:
                    print(f"\r[Attempt {attempt + 1}/{max_retries}] Stepstone responded with {raw_html.status_code}", end="")
            
            except Exception as e:
                print(f"\r[Attempt {attempt + 1}/{max_retries}] Network error/Timeout...", end="")
            
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt 
                time.sleep(sleep_time)
        
        print("\n[Error] All retries failed. Skipping this page.")
        return None


    def extract_job_cards(self, html_text):
        soup = BeautifulSoup(html_text, 'lxml')
        return soup.find_all("article", attrs={"data-at": "job-item"})
    

    def get_job_data(self, job_cards):
        job_data = []

        for card in job_cards:
            link_element = card.select_one('a[href^="/stellenangebote--"]')
            
            if not link_element:
                continue
                
            job_url = f"{self.base_url}{link_element['href']}"
            job_title = link_element.get_text(strip=True)

            company_element = card.find(attrs={"data-at": "job-item-company-name"})
            company_name = company_element.get_text(strip=True) if company_element else "Unbekannt"

            job_dict = {
                "title": job_title, 
                "url": job_url, 
                "company": company_name
            }
            job_data.append(job_dict)

        return job_data


    ''' w/o company name backup
    def extract_raw_links(self, html_text):
        soup = BeautifulSoup(html_text, 'lxml')
        return soup.select('a[href^="/stellenangebote--"]')


    def get_job_data(self, raw_job_links):
        job_data = []

        for link in raw_job_links:
            job_url = f"{self.base_url}{link['href']}"
            job_title = link.get_text(strip=True)
            job_dict = {"title": job_title, "url": job_url}
            job_data.append(job_dict)

        return job_data
    '''


    def filter_bad_words(self, list_to_filter):
        final_jobs_list = []
        filter_words = self.file_manager.get_words_to_filter()

        for url in list_to_filter:
            title_to_check = url["title"].lower()
            wanted = True
            
            for word in filter_words:
                pattern = rf"\b{re.escape(word.lower())}\b"
                
                if re.search(pattern, title_to_check):
                    wanted = False
                    # print(f"Filtered for '{word}': {url}")
                    break
            
            if wanted:
                final_jobs_list.append(url)

        return final_jobs_list


    def anti_bot_sleep(self, read_countdown=0):
        sleeping = 0
        reading = 0
        if read_countdown == 4:
            reading_pause = random.uniform(29.9, 60.1)
            while reading < reading_pause:
                print(f"\r- Simulating reading pause for {reading_pause - reading:.2f}...", end="")
                time.sleep(0.1)
                reading += 0.1
            print()

        sleep_time = random.uniform(6.4, 11.2)
        while sleeping < sleep_time:
            print(f"\r- Iterating next page in {sleep_time - sleeping:.2f} seconds...", end="")
            time.sleep(0.1)
            sleeping += 0.1
        print("\n")


    def get_list_after_compare(self, jobs_to_check, seen_links):
        final_list = []
        for job in jobs_to_check:
            if job["url"] not in seen_links:
                final_list.append(job)
        return final_list
    #endregion






            