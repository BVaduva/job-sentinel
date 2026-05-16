# Job Sentinel (Stepstone Job Scraper)

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blue)
![Clean Architecture](https://img.shields.io/badge/Focus-Clean_Architecture-success)

> **Project Goal:**
> I started this project because Stepstone's own filter didn't work the way I wanted to use it. </br>
> Example: Adding -senior to your query may also filter out jobs mentioning tutoring by a senior.</br>
> Ain't looking fancy, but it works.

## System Architecture & Features

The app is designed to allow checking jobs while the actual scraping happens quietly in the background. Here is a look under the hood:

* **Asynchronous Multi-Threading:** I used Python's `threading` and a thread-safe `queue.Queue` to ensure the CustomTkinter GUI stays fully responsive while the scraper fetches data.
* **Robust State Management:** The app smoothly manages the flow between the background data pool (`job_pool`), the active UI cards (`current_batch`), and local file storage.
* **Graceful Shutdown & Caching:** The exit sequence safely spins down active threads and saves your current queue to a local JSON cache, so you can pick up exactly where you left off on your next launch.
* **Dynamic Filtering & Memory:** The core feature. You can define custom keywords to permanently banish irrelevant job postings. The app also remembers previously seen URLs to ensure you never have to look at the same job twice.
* **Clean Code Focus:** This is a WIP with the goal being:
  * Strict separation between UI rendering and underlying data logic.
  * Extensive use of **Guard Clauses (Early Exits)** to prevent race conditions (like those annoying UI double-click bugs).
  * Implementation of modern Python Type Hinting (`dict[str, Any]`, `-> None`) so the IDE and possible contributors know exactly what's going on.

## Tech Stack

* **Language:** Python 3
* **GUI Framework:** CustomTkinter
* **Concepts:** Asynchronous Programming, Thread-Safe Queues, JSON Persistence, Object-Oriented Programming (OOP), Graceful Degradation

## How to Run

### 1. Prerequisites
Have Python 3 installed. Clone the repository and install the required dependencies:
```bash
pip install customtkinter
# Add other dependencies like requests or bs4 if you use them in your scraper
```


### 2. Configuration (Search URL)

Note: Due to the dynamic nature of job portals, you must provide your own Stepstone search URL.

- Go to Stepstone and perform your desired job search.
- At at the bottom of the page, check how many pages are available.
- Copy the resulting URL from your browser.
- Replace the URL in the `get_query_url` method.
- Start the program and enter the amount of pages to scrape up to a maximum of the pages your search lead to.


### 3. Execute

Open your terminal in the project directory and run:
```bash
python main.py
```
