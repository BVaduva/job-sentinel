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
        self.read_countdown = 0


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
                return  # Handle response in GUI

            raw_job_cards = self.extract_job_cards(html_text)
            job_urls = self.get_job_data(raw_job_cards)

            # Jobs not excluded by filter
            candidate_jobs = self.filter_bad_words(job_urls)

            # Truly new jobs:
            # - not filtered
            # - not already in seen_links.txt
            # - not already found during scrape
            current_batch = self.get_list_after_compare(candidate_jobs, seen_links)

            # Permanent raw-archive
            self.file_manager.populate_unfiltered_file(job_urls)

            # In-Memory set to exclude duplicates during scrape
            for job in current_batch:
                seen_links.add(job["url"])

            jobs_found += len(job_urls)
            filtered_jobs += len(job_urls) - len(candidate_jobs)
            seen_jobs += len(candidate_jobs) - len(current_batch)

            package = {
                "jobs": current_batch,
                "scraped_jobs_amount": jobs_found,
                "filtered_jobs_amount": filtered_jobs,
                "seen_jobs_amount": seen_jobs,
                "current_page": self.current_page
            }

            job_queue.put(package)
            self.anti_bot_sleep(self.read_countdown)
            self.current_page += 1
            self.read_countdown = 0

        print("Scrape finished.")


    #region HELPERS
    # Backend C#/.NET ASP ~15 ish pages
    
    def get_query_url(self, page_number=1):
        return(
            f"https://www.stepstone.de/jobs/c%23-or-net-or-net-backend-entwickler-in-or-c%23-developer-or-backend-developer-c%23-or-aspnet-core-or-web-api-or-restful-api-or-sql/in-stuttgart-or-t%C3%BCbingen-or-ulm?radius=50&page={page_number}&sort=2&action=sort_publish&q=(C%23)+OR+(.NET)+OR+(.NET+Backend-Entwickler%2fin)+OR+(C%23+Developer)+OR+(Backend+Developer+C%23)+OR+(ASP.NET+Core)+OR+(Web+API)+OR+(RESTful+API)+OR+(SQL)&ct=222&di=IT"
        )
    

    # Backend Allround ~48 ish pages
    """
    def get_query_url(self, page_number=1):
        return (
            f"https://www.stepstone.de/jobs/softwareentwickleranwendungsentwicklerbackend-entwicklerjava-backend-entwicklerpython-entwicklerpython-entwickler-inback-end-php-entwickler-inphp-entwickler-backendschnittstellen-entwickler-inschnittstellenentwicklungapi-entwicklungrest-apims-sql-entwickler-insql-entwickler-insql-entwicklerinhouse-entwickler/in-stuttgart-or-t%c3%bcbingen-or-ulm?radius=50&page={page_number}&sort=2&action=sort_publish&q=%28Softwareentwickler%29%2c%28Anwendungsentwickler%29%2c%28Backend+Entwickler%29%2c%28Java+Backend+Entwickler%29%2c%28Python+Entwickler%29%2c%28Python-Entwickler%2fin%29%2c%28Back+End+PHP+Entwickler%2fin%29%2c%28PHP+Entwickler+Backend%29%2c%28Schnittstellen-Entwickler%2fin%29%2c%28Schnittstellenentwicklung%29%2c%28API+Entwicklung%29%2c%28REST+API%29%2c%28MS+SQL+Entwickler%2fin%29%2c%28SQL-Entwickler%2fin%29%2c%28SQL+Entwickler%29%2c%28Inhouse+Entwickler%29&searchOrigin=Resultlist_top-search&di=IT"
        )
    """

    # Schnittstellen / Automation ~40 ish pages
    """
    def get_query_url(self, page_number=1):
        return (
            f"https://www.stepstone.de/jobs/internal-tools-developerschnittstellenpython-automationc%23-anwendungssoftwareai-applicationdata-processingsimulationpr%C3%BCfsoftware/in-stuttgart-or-t%C3%BCbingen-or-ulm?radius=50&page={page_number}&sort=2&action=sort_publish&q=(Internal+Tools+Developer)%2c(Schnittstellen)%2c(Python+Automation)%2c(C%23+Anwendungssoftware)%2c(AI+Application)%2c(Data+Processing)%2c(Simulation)%2c(Pr%C3%BCfsoftware)&ct=222&di=IT"
            )
    """
        
    # Intern tools, MDE/BDE/MES/API ~65 ish pages
    """
    def get_query_url(self, page_number=1):
        return (
        f"https://www.stepstone.de/jobs/schnittstellenentwicklerschnittstellenentwicklungsystemintegration-softwaresoftwareentwickler-interne-systemeentwickler-interne-toolspython-automatisierungdatenverarbeitung-pythonetl-entwicklersql-pythonapi-entwicklermes-entwicklerbde-entwicklermde-entwickler/in-stuttgart-or-t%C3%BCbingen-or-ulm?radius=50&page={page_number}&sort=2&action=sort_publish&q=(Schnittstellenentwickler)%2c(Schnittstellenentwicklung)%2c(Systemintegration+Software)%2c(Softwareentwickler+interne+Systeme)%2c(Entwickler+interne+Tools)%2c(Python+Automatisierung)%2c(Datenverarbeitung+Python)%2c(ETL+Entwickler)%2c(SQL+Python)%2c(API+Entwickler)%2c(MES+Entwickler)%2c(BDE+Entwickler)%2c(MDE+Entwickler)&searchOrigin=Resultlist_top-search&di=IT"
        )
    """


    def fetch_html_text(self, page_number, session, max_retries=5):
        query_url = self.get_query_url(page_number)
        #header_url = self.get_query_url(page_number+1)
        fake_headers = {"Referer": self.base_url}
        #fake_headers = {"Referer": header_url}

        for attempt in range(max_retries):
            try:
                raw_html = session.get(query_url, impersonate="chrome", timeout=34, headers=fake_headers)
                
                if raw_html.status_code == 200:
                    return raw_html.text
                else:
                    self.read_countdown = 4
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
            reading_pause = random.uniform(21.9, 38.1)
            while reading < reading_pause:
                print(f"\r- Simulating reading pause for {reading_pause - reading:.2f}...", end="")
                time.sleep(0.1)
                reading += 0.1
            print()

        sleep_time = random.uniform(9.3, 15.1)
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






            
