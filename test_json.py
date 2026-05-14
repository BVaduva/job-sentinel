import os
import json
from file_manager import FileManager

"""
if os.path.exists("t_e.json"):
    with open("t_e.json", "r", encoding="utf-8") as file:
        alle_jobs = json.load(file)
else:
    alle_jobs = []

alle_jobs.extend(alle_jobs) 

with open("test_ergebnisse.json", "w", encoding="utf-8") as file:
    json.dump(alle_jobs, file, indent=4, ensure_ascii=False)
"""

if __name__ == "__main__":
    file_manager = FileManager()