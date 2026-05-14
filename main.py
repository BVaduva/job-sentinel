import customtkinter as ctk
from file_manager import FileManager
from scraper import ScraperEngine
import threading
import queue
import os
import sys

class JobSentinelGUI(ctk.CTk):
    def __init__(self, final_list, scraper:ScraperEngine, file_manager:FileManager):
        super().__init__()

        self.final_list = final_list 
        self.active_jobs_in_batch = 0
        self.job_queue = queue.Queue()
        self.scraper = scraper
        self.file_manager = file_manager
        self.cache_exists = self.file_manager.check_cache()
        self.jobs_container = None
        self.status_label = None

        # Basic Window
        self.title("Stepstone Job Scraper")
        self.geometry("2400x1350")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        if not self.cache_exists:
            self.create_start_frame()
        else:
            self.final_list = self.file_manager.get_cache_data()
            self.create_jobs_frame()
            self.load_batch()
            self.update_status_text()

        self.debug_btn = ctk.CTkButton(
            self, text="Reload", font=("Arial", 20), width=140, height=60, 
            fg_color="gray", command=self.restart_app
            )
        self.debug_btn.place(x=2200, y=10)


    #region STARTER
    def create_start_frame(self):
        start_frame = ctk.CTkFrame(self, fg_color="transparent")
        start_frame.pack(fill="both", expand=True)

        center_frame = ctk.CTkFrame(start_frame, fg_color="transparent")
        center_frame.pack(expand=True)

        instruction = ctk.CTkLabel(
            center_frame, font=("Arial", 28), 
            text="Enter how many pages to scrape.\n(At most the max amount of pages available after search)",
            wraplength=800
            )
        instruction.pack(pady=(0, 40))

        entry = ctk.CTkEntry(
            center_frame, placeholder_text="10", font=("Arial", 28), 
            width=150, height=60, justify="center"
            )
        entry.pack(pady=20)

        start_btn = ctk.CTkButton(
            center_frame, text="Start Scrape", font=("Arial", 28, "bold"), 
            fg_color="#8B0000", hover_color="#5c0000", width=250, height=60,
            command=lambda: self.handle_start_click(start_frame, entry)
            )
        start_btn.pack(pady=40)


    def handle_start_click(self, start_frame, entry_widget):
        page_amount = int(entry_widget.get())
        print(f"Eingabe war: {page_amount}")
        
        start_frame.destroy()
        self.create_jobs_frame()
        self.status_label.configure(text="Waiting for first page to be scraped...")
        self.run_scraping_thread(page_amount)


    def run_scraping_thread(self, page_amount):
        thread = threading.Thread(target=scraper.run_scraper, args=(page_amount,))
        thread.start()
    #endregion


    def create_jobs_frame(self):
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 24, "bold"))
        self.status_label.pack(pady=20)

        self.jobs_container = ctk.CTkFrame(self, fg_color="transparent")
        self.jobs_container.pack(fill="both", expand=True, padx=40)

        exit_btn = ctk.CTkButton(
            self, text="Exit & Save Cache", font=("Arial", 16), 
            fg_color="#8B0000", hover_color="#5c0000", command=self.exit_app
            )
        exit_btn.pack(pady=20)


    def create_job_row(self, job_data):
        job_card = ctk.CTkFrame(self.jobs_container, corner_radius=15)
        job_card.pack(fill="x", pady=15, padx=20, ipady=20) 

        title_label = ctk.CTkLabel(
            job_card, 
            text=job_data["title"], 
            font=("Arial", 22, "bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=25, pady=(20, 10))

        button_row = ctk.CTkFrame(job_card, fg_color="transparent")
        button_row.pack(fill="x", padx=20)

        open_btn = ctk.CTkButton(
            button_row, text="Open", fg_color="#219150", width=120, 
            command=lambda frame=job_card, data=job_data["url"]: 
            self.process_job("open", frame, data)
            )
        open_btn.pack(side="left", padx=5)

        skip_btn = ctk.CTkButton(
            button_row, text="Skip", fg_color="#634118", width=120, 
            command=lambda frame=job_card, data=job_data["url"]: 
            self.process_job("skip", frame, data)
            )
        skip_btn.pack(side="left", padx=5)

        filter_btn = ctk.CTkButton(
            button_row, text="Filter Word", fg_color="#2b2b2b", width=120,
            command=lambda frame=job_card, data=job_data["title"]: 
            self.process_job("filter", frame, data)
            )
        filter_btn.pack(side="left", padx=5)


    def process_job(self, action, row_frame, job_data):
        if action == "open":
            print(f"Browser öffnet: {job_data}")
        elif action == "skip":
            print(f"Übersprungen: {job_data}")
        elif action == "filter":
            print(f"Filter word...")
            filter_input = self.input_filter_word_popup(job_data)
            if filter_input is None:
                print(f"None clause triggered.")
                return
            elif filter_input.strip() == "":
                print(f"Emtpy string clause triggered.")
                return
            clean_words = [word.strip() for word in filter_input.split(",")]
            file_manager.populate_filter_file(clean_words)
            print(f"'{clean_words}' added to filter...")

        row_frame.destroy()
        self.active_jobs_in_batch -= 1
        self.update_status_text()

        if self.active_jobs_in_batch == 0:
            self.load_batch()


    def load_batch(self):
        # Get up to 5 jobs or less, if list is empty.
        batch_size = min(5, len(self.final_list))
        self.active_jobs_in_batch = batch_size

        if batch_size == 0:
            self.status_label.configure(text="Done! No more jobs to check.")
            return

        for _ in range(batch_size):
            job_data = self.final_list.pop(0)
            self.create_job_row(job_data)


    def update_status_text(self):
        total_jobs_left = len(self.final_list) + self.active_jobs_in_batch
        self.status_label.configure(text=f"Jobs to check left: {total_jobs_left}")
    

    def input_filter_word_popup(self, job_title):
        instruction = "\n (You can add multiple words: senior, lead ...)"
        input_window = ctk.CTkInputDialog(text=job_title+instruction, title="Filter Word")
        filter_input = input_window.get_input()
        print(f"filter_input -> {filter_input}")
        return filter_input


    def check_queue(self):
        if not self.job_queue.empty():
            new_job = self.job_queue.get()

        self.update_status_labels()
        self.after(1000, self.check_queue)


    def exit_app(self):
        print("Speichere Rest in Cache und beende...")
        self.destroy()

    
    def restart_app(self):
        """Startet das komplette Python-Skript neu."""
        os.execl(sys.executable, sys.executable, *sys.argv)


if __name__ == "__main__":
    file_manager = FileManager()
    scraper = ScraperEngine()
    test_links = [
    {
        "title": "Softwareentwickler (m/w/d) für Exoskelette",
        "url": "https://www.stepstone.de/stellenangebote--Softwareentwickler-m-w-d-fuer-Exoskelette-Horb-am-Neckar-hTRIUS-GmbH--13998867-inline.html"
    },
    {
        "title": "Softwareentwickler (m/w/d) für relationale Datenbanksysteme",
        "url": "https://www.stepstone.de/stellenangebote--Softwareentwickler-m-w-d-fuer-relationale-Datenbanksysteme-Stuttgart-WGV-Wuerttembergische-Gemeinde-Versicherung-a-G--13999336-inline.html"
    },
    {
        "title": "AI Automation Engineer (m/w/d)",
        "url": "https://www.stepstone.de/stellenangebote--AI-Automation-Engineer-m-w-d-Ulm-Seifert-Logistics-Group--13998692-inline.html"
    },
    {
        "title": "Software Engineer Embedded Systems Smart Cabin (m/w/d)",
        "url": "https://www.stepstone.de/stellenangebote--Software-Engineer-Embedded-Systems-Smart-Cabin-m-w-d-Reutlingen-Kraemer-Automotive-Systems-GmbH--13407654-inline.html"
    },
    {
        "title": "Entwickler Steuerungsprogrammierung Robotik (m/w/d)",
        "url": "https://www.stepstone.de/stellenangebote--Entwickler-Steuerungsprogrammierung-Robotik-m-w-d-Schorndorf-bei-Stuttgart-ASYS-Automatic-Systems-GmbH-Co-KG--13915223-inline.html"
    },
    {
        "title": "Hardware-Entwickler Elektronik (m/w/d)",
        "url": "https://www.stepstone.de/stellenangebote--Hardware-Entwickler-Elektronik-m-w-d-Neu-Ulm-NewTec-GmbH--13419878-inline.html"
    },
    {
        "title": "Embedded Softwareingenieur (m/w/d)",
        "url": "https://www.stepstone.de/stellenangebote--Embedded-Softwareingenieur-m-w-d-Ulm-NewTec-GmbH--13419872-inline.html"
    },
    {
        "title": "Informatiker als Fullstack Software-Entwickler (m/w/d)",
        "url": "https://www.stepstone.de/stellenangebote--Informatiker-als-Fullstack-Software-Entwickler-fuer-Web-Applikationen-m-w-d-Tuebingen-Koeln-DKMS-Group-gGmbH--13936971-inline.html"
    },
    {
        "title": "User Experience und User Interface Designer (w/m/d)",
        "url": "https://www.stepstone.de/stellenangebote--User-Experience-und-User-Interface-Designer-w-m-d-Ulm-HENSOLDT--13936627-inline.html"
    },
    {
        "title": "Programmierer E-Plan (m/w/d)",
        "url": "https://www.stepstone.de/stellenangebote--Programmierer-E-Plan-m-w-d-Techniker-in-Elektrotechnik-ohne-Schwerpunkt-Bachelor-Professional-in-Technik-Schelklingen-MSR-Gebaeudetechnik-GmbH--13933903-inline.html"
    },
    {
        "title": "SOFTWARE TEST ENGINEER (m/w/d)",
        "url": "https://www.stepstone.de/stellenangebote--SOFTWARE-TEST-ENGINEER-m-w-d-Ulm-Zuken-E3-GmbH--12587898-inline.html"
    }
]
    
    app = JobSentinelGUI(test_links, scraper, file_manager)
    app.mainloop()