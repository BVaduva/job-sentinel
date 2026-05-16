import customtkinter as ctk
from file_manager import FileManager
from scraper import ScraperEngine
from custom_input_dialog import CustomInputDialog
import threading
import queue
import os
import sys
import webbrowser
from typing import Any

class JobSentinelGUI(ctk.CTk):
    BATCH_SIZE = 10
    WINDOW_TITLE = "Stepstone Job Scraper"

    def __init__(self, scraper:ScraperEngine, file_manager:FileManager):
        super().__init__()
        self._init_state()
        self._build_ui()

        self.debug_btn = ctk.CTkButton(
            self, text="Reload", font=("Arial", 20), width=140, height=60, 
            fg_color="gray", command=self._restart_app
            )
        self.debug_btn.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)


    #region START FRAME
    def _create_start_frame(self) -> None:
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
            command=lambda: self._handle_start_click(start_frame, entry)
            )
        start_btn.pack(pady=40)


    def _handle_start_click(self, start_frame: ctk.CTkFrame, entry_widget: ctk.CTkEntry) -> None:
        self.page_amount = int(entry_widget.get())

        start_frame.destroy()
        self._create_jobs_frame()
        self.status_label.configure(text="Waiting for first page to be scraped...")
        self._run_scraping_thread()


    def _run_scraping_thread(self)-> None:
        self.thread = threading.Thread(target=scraper.run_scraper, args=(self.page_amount, self.job_queue))
        self.thread.start()
        self._check_queue()
    #endregion


    #region JOB FRAME
    def _create_jobs_frame(self) -> None:
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 32, "bold"))
        self.status_label.pack()

        self.jobs_container = ctk.CTkFrame(self, fg_color="transparent")
        self.jobs_container.pack(fill="both", expand=True, padx=40)

        exit_btn = ctk.CTkButton(
            self, text="Exit & Save", font=("Arial", 28), 
            fg_color="#8B0000", hover_color="#5c0000", command=self._exit_app
            )
        exit_btn.pack(pady=20)


    def _create_job_row(self, job_data: dict[str, Any]) -> None:
        job_card = ctk.CTkFrame(self.jobs_container, corner_radius=15)
        job_card.pack(fill="x", pady=10, padx=10, ipady=10) 

        title_label = ctk.CTkLabel(
            job_card, 
            text=job_data["title"], 
            font=("Arial", 36, "bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=25, pady=(10, 10))

        button_row = ctk.CTkFrame(job_card, fg_color="transparent")
        button_row.pack(fill="x", padx=15)

        button_font = ("Arial", 20, "bold")

        open_btn = ctk.CTkButton(
            button_row, text="Open", fg_color="#219150", hover_color="#186b3b",
            width=160, height=45, font=button_font,
            command=lambda frame=job_card, data=job_data: 
            self._open_job(frame, data)
        )
        open_btn.pack(side="left", padx=10)

        skip_btn = ctk.CTkButton(
            button_row, text="Skip", fg_color="#634118", hover_color="#452d11",
            width=160, height=45, font=button_font,
            command=lambda frame=job_card, data=job_data: 
            self._skip_job(frame, data)
        )
        skip_btn.pack(side="left", padx=10)

        filter_btn = ctk.CTkButton(
            button_row, text="Filter Word", fg_color="#545454", hover_color="#3b3b3b", 
            width=160, height=45, font=button_font,
            command=lambda frame=job_card, data=job_data: 
            self._filter_word(frame, data)
        )
        filter_btn.pack(side="left", padx=10)


    def _finalize_job(self, row_frame: ctk.CTkFrame, job_data: dict[str, Any]) -> None:
        if job_data not in self.current_batch:
            return
        
        self.file_manager.populate_seen_file(job_data["url"])
        self.current_batch.remove(job_data)
        row_frame.destroy()
        self.active_jobs_in_batch -= 1
        self._update_status_text()

        if self.active_jobs_in_batch == 0:
            self._load_batch()

    
    def _open_job(self, frame: ctk.CTkFrame, job_data: dict[str, Any]) -> None:
        webbrowser.open(job_data["url"])
        self._finalize_job(frame, job_data)


    def _skip_job(self, frame: ctk.CTkFrame, job_data: dict[str, Any]) -> None:
        self._finalize_job(frame, job_data)


    def _filter_word(self, frame: ctk.CTkFrame, job_data: dict[str, Any]) -> None:
        filter_input = self._ask_user_for_filter_word(job_data["title"])
        if filter_input is None:
            return
        elif filter_input.strip() == "":
            return
        clean_words = [word.strip() for word in filter_input.split(",")]
        self.file_manager.populate_filter_file(clean_words)
        self._show_toast(f"Added to filter: {', '.join(clean_words)}")
        self._finalize_job(frame, job_data)


    def _ask_user_for_filter_word(self, job_title: str) -> str:
        instruction = "\n\n(You can add multiple words: senior, lead ...)"
        input_window = CustomInputDialog(title="Filter Word", text=job_title + instruction)
        filter_input = input_window.get_input()
        return filter_input
    

    def _show_toast(self, message:str) -> None:
        toast_label = ctk.CTkLabel(
            self, text=message, fg_color="#219150", text_color="white",
            font=("Arial", 30, "bold"), corner_radius=10, padx=25, pady=12
        )
        toast_label.place(relx=0.5, rely=0.9, anchor="center")
        self.after(5000, toast_label.destroy)
    #endregion


    #region PROCESS FRAME
    def _create_scraping_status_frame(self) -> None:
        scraping_container = ctk.CTkFrame(self)
        scraping_container.pack(anchor="w")

        label_font = ("Arial", 24) 
        seperator_color = "gray"

        self.page_progress_label = ctk.CTkLabel(scraping_container, text="", font=label_font)
        self.page_progress_label.pack(side="left", padx=(20, 10), pady=15)
        ctk.CTkLabel(scraping_container, text="|", font=label_font, text_color=seperator_color).pack(side="left")

        self.total_jobs_scraped_label = ctk.CTkLabel(scraping_container, text="", font=label_font)
        self.total_jobs_scraped_label.pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(scraping_container, text="|", font=label_font, text_color=seperator_color).pack(side="left")

        self.total_jobs_filtered_label = ctk.CTkLabel(scraping_container, text="", font=label_font)
        self.total_jobs_filtered_label.pack(side="left", padx=10, pady=10)
        ctk.CTkLabel(scraping_container, text="|", font=label_font, text_color=seperator_color).pack(side="left")

        self.total_jobs_seen_label = ctk.CTkLabel(scraping_container, text="", font=label_font)
        self.total_jobs_seen_label.pack(side="left", padx=(10, 20), pady=10)
    #endregion


    #region UPDATES
    def _load_batch(self) -> None:
        batch_size = min(self.BATCH_SIZE, len(self.job_pool))
        self.active_jobs_in_batch = batch_size

        if batch_size == 0:
            self.status_label.configure(text="Done! No more jobs to check.")
            return

        for _ in range(batch_size):
            job_data = self.job_pool.pop(0)
            self.current_batch.append(job_data)
            self._update_status_text()
            self._create_job_row(job_data)


    def _update_status_text(self) -> None:
        total_jobs_left = len(self.job_pool) + self.active_jobs_in_batch
        self.status_label.configure(text=f"Jobs left: {total_jobs_left}")


    def _update_scraping_status(self, queue_package: dict[str, Any]) -> None:
        scraping_status_scraped= queue_package["scraped_jobs_amount"]
        scraping_status_filtered = queue_package["filtered_jobs_amount"]
        scraping_status_current_page = queue_package["current_page"]
        scraping_status_seen_jobs = queue_package["seen_jobs_amount"]

        self.page_progress_label.configure(
            text=f"Pages checked: {scraping_status_current_page}/{self.page_amount}")
        self.total_jobs_scraped_label.configure(
            text=f"Jobs found: {scraping_status_scraped}")
        self.total_jobs_filtered_label.configure(
            text=f"Jobs filtered: {scraping_status_filtered}")
        self.total_jobs_seen_label.configure(
            text=f"Jobs already seen: {scraping_status_seen_jobs}")
    

    def _check_queue(self) -> None:
        while not self.job_queue.empty():
            queue_package = self.job_queue.get()
            self.job_pool.extend(queue_package["jobs"])
            self._update_status_text()
            self._update_scraping_status(queue_package)
            if self.active_jobs_in_batch == 0:
                self._load_batch()
        
        if self.thread.is_alive():
            self.after(500, self._check_queue)
    #endregion


    #region HELPERS
    def _init_state(self) -> None:
        # Class objects
        self.job_queue = queue.Queue()
        self.scraper = scraper
        self.file_manager = file_manager

        # UI-Elements
        self.total_jobs_filtered_label = None
        self.total_jobs_scraped_label = None
        self.total_jobs_seen_label = None
        self.page_progress_label = None
        self.jobs_container = None
        self.status_label = None

        # Data
        self.job_pool = []
        self.active_jobs_in_batch = 0
        self.cache_exists = self.file_manager.check_cache()
        self.thread = None
        self.page_amount = 1
        self.current_batch = []


    def _build_ui(self) -> None:
        self.title(self.WINDOW_TITLE)
        self.attributes("-fullscreen", "True")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        if not self.cache_exists:
            self._create_start_frame()
            self._create_scraping_status_frame()
        else:
            self.job_pool = self.file_manager.get_cache_data()
            self._create_jobs_frame()
            self._load_batch()
            self._update_status_text()
    #endregion


    #region UTILITY
    def _exit_app(self) -> None:
        self.scraper.stop_signal = True
        self._handle_scraper_shutdown()


    def _handle_scraper_shutdown(self) -> None:
        if self.thread is None or not self.thread.is_alive():
            cache_data = self.current_batch + self.job_pool
            self.file_manager.create_cache_file(cache_data)
            self.destroy()
        else: self.after(500, self._handle_scraper_shutdown)
    

    def _restart_app(self) -> None:
        print("############## RESTARTING ##############")
        os.execl(sys.executable, sys.executable, *sys.argv)
    #endregion


if __name__ == "__main__":
    file_manager = FileManager()
    scraper = ScraperEngine()
    
    app = JobSentinelGUI(scraper, file_manager)
    app.mainloop()