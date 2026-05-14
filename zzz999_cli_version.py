from bs4 import BeautifulSoup
from curl_cffi import requests
import sys
import random
import time
import webbrowser
import re
from file_manager import FileManager


########################################
# USES OLD FileManager
# To make this work, an adjusted FileManager (CliFileManager)
# has to be made
########################################


# region Functions
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

    fake_headers = {"Referer": "https://www.stepstone.de/"}
    #if page_number == 1:
     #   fake_headers = {"Referer": "https://www.stepstone.de/"}

    #else:
    #    page_number -= 1
    #    previous_page = get_query_url(page_number)
    #    fake_headers = {"Referer": previous_page}

    try:
        raw_html = session.get(query_url, impersonate="chrome", timeout=15, headers=fake_headers)

        if raw_html.status_code != 200:
            print(f"Error: Stepstone responded with status {raw_html.status_code}")
            return
        
    except Exception as e:
        print(f"[Exception Error] - Details: {e}")
        return # implicit None
    
    html_text = raw_html.text

    return html_text


def extract_raw_links(html_text):
    soup = BeautifulSoup(html_text, 'lxml')
    return soup.select('a[href^="/stellenangebote--"]')


def get_job_urls(raw_job_links):
    base_url = "https://www.stepstone.de"
    job_urls = []

    for link in raw_job_links:
        job_urls.append(f"{base_url}{link['href']}")

    return job_urls


def filter_bad_words(list_to_filter):
    final_jobs_list = []
    filter_words = file_manager.get_words_to_filter()

    for url in list_to_filter:
        check_url = url.lower().replace("-", " ")
        wanted = True
        
        for word in filter_words:
            pattern = rf"\b{re.escape(word)}\b"
            
            if re.search(pattern, check_url):
                wanted = False
                # print(f"Filtered for '{word}': {url}")
                break
        
        if wanted:
            final_jobs_list.append(url)

    return final_jobs_list


def anti_bot_sleep(read_countdown):
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


def get_final_list_after_compare(links_to_check, seen_links):
    final_list = []
    for link in links_to_check:
        if link not in seen_links:
            final_list.append(link)
    return final_list


def run_interactive_loop(final_list):
    while len(final_list) > 0:
        job_title = final_list.pop(0)
        job_link = job_title
        job_title = job_title.split("--")[1].replace("-", " ")

        try:
            while True:
                answer = input(f"Open job: {job_title} ?\n Yes(y), No(n), Exit(e): ").strip()

                if answer.lower() not in ['y', 'n', 'e']:
                    print(f"- Error: '{answer}' is not a valid input.")

                elif answer.lower() == 'e':
                    file_manager.create_cache_file(job_link, final_list)
                    sys.exit(0)

                elif answer.lower() == 'y':
                    webbrowser.open_new_tab(job_link)
                    break

                elif answer.lower() == 'n':
                    break

            file_manager.populate_seen_file([job_link])

        except Exception as e:
            print(f"Error: {e}")
    
    print("- Finished all links.")
    file_manager.delete_cache_file()

# endregion

#################################################################################
#################################################################################

if __name__ == "__main__":
    session = requests.Session()
    file_manager = FileManager()

    # In case reading pause in anti_bot_sleep is needed
    # read_countdown = 0

    current_page = 1

    # Check for existing cache file which exists, if program was exited before finishing all links
    # Skip the scraping process and continue checking links from cache.
    if file_manager.check_cache():
        print("\n" + "="*40)
        print("- Cache file found. Continue at last link.")
        final_list = file_manager.get_cache_links()

    else:
        print("\n" + "="*40)
        page_amount = int(input("How many pages to scrape?\n"))

        while current_page != page_amount:
            print(f"- Trying to fetch html on page {current_page}/{page_amount}...")
            html_text = fetch_html_text(current_page, session)

            if html_text is None:
                print("- Can't continue operation without fetched data.")
                print("- Trying again in 30 seconds...\n")
                session = requests.Session()
                time.sleep(30)

            else:
                raw_job_links = extract_raw_links(html_text)
                job_urls = get_job_urls(raw_job_links)
                filtered_urls = filter_bad_words(job_urls)

                file_manager.populate_unfiltered_file(job_urls)
                file_manager.populate_unseen_file(filtered_urls)

                anti_bot_sleep(0) # Wait for random seconds to scrape next page.
                # read_countdown += 1

                # if read_countdown == 5:
                #     read_countdown = 0

                current_page += 1

        links_to_check = file_manager.get_unseen_links()
        seen_links = file_manager.get_seen_links()
        final_list = get_final_list_after_compare(links_to_check, seen_links)

    run_interactive_loop(final_list)

            