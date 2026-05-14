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
            "cache": os.path.join(files_dir, "cached_jobs.json")
        }

        for key, file in self.files.items():
            if key != "cache":
                with open(file, "a"):
                    pass


    def check_cache(self):
        cache_file = self.files["cache"]
        if os.path.exists(cache_file):
            return True
        else: return False


    def create_cache_file(self, current_job_link, link_list):
        cache_list = [current_job_link] + link_list
        self.__populate_json("cache", cache_list)
    

    def delete_cache_file(self):
        file = self.files["cache"]
        if os.path.exists(file):
            os.remove(file)

#region POPULATER

    def populate_seen_file(self, content):
        self.__populate_file("seen", content)


    def populate_unseen_file(self, content):
        self.__populate_json("unseen", content)


    def populate_unfiltered_file(self, content):
        self.__populate_json("unfiltered", content)


    def populate_filter_file(self, content):
        self.__populate_file("filter", content)

#endregion

#region GETERS
    def get_words_to_filter(self):
        return self.__read_text_file("filter")
    

    def get_unseen_jobs(self):
        return self.__read_json_file("unseen")
    

    def get_seen_links(self):
        return set(self.__read_text_file("seen"))


    def get_cache_data(self):
        return self.__read_json_file("cache")
#endregion


#region HELPERS
    def __read_text_file(self, file_key):
        content = []
        file_name = self.files[file_key]
        with open(file_name, "r", encoding="utf-8") as file:
            for line in file:
                content.append(line.strip())
        return content
    
    
    def __read_json_file(self, file_key):
        file_name = self.files[file_key]
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                content = json.load(file)
                return content
        except Exception as e:
            return []


    def __populate_file(self, file_key, content):
        file_name = self.files[file_key]
        with open(file_name, "a") as file:
            for line in content:
                file.write(f"{line}\n")


    def __populate_json(self, file_key, content):
        current_data = self.__read_json_file(file_key)
        current_data.extend(content)
        with open(self.files[file_key], "w", encoding="utf-8") as file:
            json.dump(current_data, file, indent=4, ensure_ascii=False)


#endregion