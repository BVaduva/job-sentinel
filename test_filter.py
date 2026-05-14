import re
import json

def get_jobs_to_check():
    with open("test.json", "r", encoding="utf-8") as file_unseen:
        return json.load(file_unseen)


def filter_bad_words(job_list):
    final_jobs_list = []
    filter_words = get_filter_words()

    for job in job_list:
        # Hier ist die Magie: Wir greifen direkt auf den echten Titel zu!
        # Kein URL-Hacking mit replace("-", " ") mehr nötig.
        title_to_check = job["title"].lower()
        wanted = True
        
        for word in filter_words:
            # Wir stellen sicher, dass auch das Filterwort kleingeschrieben ist
            pattern = rf"\b{re.escape(word.lower())}\b"
            
            if re.search(pattern, title_to_check):
                wanted = False
                # print(f"Filtered for '{word}': {job['title']}")
                break
        
        if wanted:
            final_jobs_list.append(job)

    return final_jobs_list


def get_filter_words():
    filter_words = []
    with open("files/words_to_filter.txt", "r", encoding="utf-8") as file: # Pfad evtl. anpassen
        for line in file:
            filter_words.append(line.strip())
    return filter_words


if __name__ == "__main__":
    unfiltered_jobs = get_jobs_to_check()
    final_jobs = filter_bad_words(unfiltered_jobs)
    
    # print(f"Übrig gebliebene Jobs: {len(final_jobs)}")
    
    # Auch das Speichern des Tests machen wir nun sauber als JSON
    with open("test2.json", "w", encoding="utf-8") as file:
        json.dump(final_jobs, file, indent=4, ensure_ascii=False)