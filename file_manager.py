import os
import json

class FileManager:
    def __init__(self):
        current_dir = os.path.dirname(__file__)
        files_dir = os.path.join(current_dir, "files")
        os.makedirs(files_dir, exist_ok=True)

        self.files = {
            "unfiltered": os.path.join(files_dir, "unfiltered_jobdata.json"),
            "unseen": os.path.join(files_dir, "unseen_jobs.json"),
            "seen": os.path.join(files_dir, "seen_links.txt"),
            "filter": os.path.join(files_dir, "words_to_filter.txt"),
            "company": os.path.join(files_dir, "company_notes.json"),
            "backlog": os.path.join(files_dir, "backlog.json"),
            "cache": os.path.join(files_dir, "cached_jobs.json")
        }

        for key, file in self.files.items():
            if key != "cache":
                with open(file, "a"):
                    pass


    def check_cache(self) -> None:
        cache_file = self.files["cache"]
        if os.path.exists(cache_file):
            return True
        else: return False


    def update_json_file(self, file_key: str, job_data: dict[str, str]) -> None:
        with open(self.files[file_key], "w", encoding="utf-8") as file:
            json.dump(job_data, file, indent=4, ensure_ascii=False)
    

    def delete_cache_file(self) -> None:
        file = self.files["cache"]
        if os.path.exists(file):
            os.remove(file)

    
    def save_company_note(self, company_name: str, note: str) -> None:
        company_file = self._read_json_file("company", {})
        company_file[company_name] = note

        with open(self.files["company"], "w", encoding="utf-8") as file:
            json.dump(company_file, file, indent=4, ensure_ascii=False)


#region POPULATER
    def populate_seen_file(self, link: str) -> None:
        seen = self.get_seen_links()
        if link not in seen:
            self._populate_file("seen", link)


    def populate_unseen_file(self, job_data: dict[str, str]) -> None:
        self._populate_json("unseen", job_data)


    def populate_unfiltered_file(self, job_data: dict[str, str]) -> None:
        self._populate_json("unfiltered", job_data)


    def populate_filter_file(self, words) -> None: # words list or str
        self._populate_file("filter", words)


    def populate_backlog_file(self, job_data: dict[str, str]) -> None:
        self._populate_json("backlog", [job_data])
#endregion


#region GETERS
    def get_words_to_filter(self) -> list:
        return self._read_text_file("filter")
    

    def get_unseen_jobs(self) -> dict[str, str]:
        return self._read_json_file("unseen")
    

    def get_seen_links(self) -> list:
        return set(self._read_text_file("seen"))


    def get_cache_data(self) -> dict[str, str]:
        return self._read_json_file("cache")
    

    def get_company_note(self, company_name: str) -> str:
        company_note = self._read_json_file("company", {})
        return company_note.get(company_name, "")
    

    def get_backlog_jobs(self) -> dict[str, str]:
        return self._read_json_file("backlog")
#endregion


#region HELPERS
    def _read_text_file(self, file_key: str) -> list:
        content = []
        file_name = self.files[file_key]
        with open(file_name, "r", encoding="utf-8") as file:
            for line in file:
                content.append(line.strip())
        return content
    
    
    def _read_json_file(self, file_key: str, default_return=None) -> dict[str, str]:
        if default_return is None:
            default_return = []

        file_name = self.files[file_key]
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return default_return


    def _populate_file(self, file_key: str, content) -> None: # content str or list
        file_name = self.files[file_key]
        with open(file_name, "a") as file:
            if isinstance(content, list):
                for line in content:
                    file.write(f"{line}\n")
            else:
                file.write(f"{content}\n")
            

    def _populate_json(self, file_key: str, content: list) -> None:
        current_data = self._read_json_file(file_key)
        current_data.extend(content)
        with open(self.files[file_key], "w", encoding="utf-8") as file:
            json.dump(current_data, file, indent=4, ensure_ascii=False)
#endregion


#region UTILITY
    def clean_filter_file(self) -> None:
        filter_file = self.files["filter"]
        with open(filter_file, "r", encoding="utf-8") as file:
            words = [line.strip().lower() for line in file if line.strip()]

        unique_sorted_words = sorted(list(set(words)))
        with open(filter_file, "w", encoding="utf-8") as file:
            for word in unique_sorted_words:
                file.write(f"{word}\n")
#endregion