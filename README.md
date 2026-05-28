# Job Sentinel (Stepstone Job Scraper)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blue)
![Clean Architecture](https://img.shields.io/badge/Focus-Clean_Architecture-success)

> **Project Goal:**
> I started this project because Stepstone's own filter didn't work the way I wanted to use it.</br>
> Example: Adding `-senior` to your query may also filter out jobs mentioning tutoring by a senior.
> Ain't looking fancy, but it works.

---

## Features

### Scraping
- Scrapes job listings from Stepstone based on a fully customizable search URL
- Configurable page depth: enter how many pages to scrape at launch
- Anti-bot measures: randomized sleep intervals between requests and simulated reading pauses to mimic human browsing behavior
- Automatic retry logic with exponential backoff on failed requests (up to 3 attempts per page)

### Job Review Board
- Jobs are presented as interactive cards showing the **job title**, **company name**, and action buttons
- **Open** - opens the job listing in your browser directly from the card
- **Skip** - marks the job as seen and removes it from the board
- **Unavailable** - removes the job without marking it as seen (for listings that have already expired)
- **To Backlog** - saves the job to a separate backlog for later review
- **Note** - attach a persistent, per-company self-reminder note that is saved across sessions
- Click any **job title** to instantly copy it to your clipboard

### Smart Filtering
- Add custom filter words at any time via the **Add Filter Word** button (supports multiple comma-separated words at once, e.g. `senior, lead, head of`)
- Filters use whole-word regex matching so e.g. `senior` won't accidentally filter out `backend developer` but does `senior backend developer`
- Filter words are applied retroactively to the current `job_pool` the moment you add them
- Filter list is deduplicated and alphabetically sorted on every save

### Backlog View
- Switch between the live scrape view and your saved backlog at any time using the **Switch to Backlog** button
- Backlog jobs persist across sessions in a local JSON file

### Session Persistence & Caching
- On exit, the remaining `job_pool` and active `current_batch` are merged and saved to a local JSON cache
- On the next launch, the app detects the cache and picks up exactly where you left off. No need to re-scrape
- Previously seen job URLs are stored permanently so they are never shown again across sessions

### UI Feedback
- A non-blocking toast notification confirms clipboard copies and filter additions
- The status bar always shows the accurate number of remaining jobs across both the pool and the active batch
- A live scraping status bar tracks: pages checked, total jobs found, jobs filtered, and jobs already seen

---

## System Architecture

The app is designed to allow reviewing jobs while scraping happens quietly in the background. Here is a look under the hood:

- **Asynchronous Multi-Threading:** Python's `threading` and a thread-safe `queue.Queue` keep the CustomTkinter GUI fully responsive while the scraper fetches data.
- **Robust State Management:** Smooth flow between the background data pool (`job_pool`), the active UI cards (`current_batch`), and local file storage.
- **Graceful Shutdown & Caching:** The exit sequence safely spins down active threads before saving state, preventing data loss or corruption.
- **Clean Code Focus:**
  - Strict separation between UI rendering and underlying data logic
  - Extensive use of **Guard Clauses (Early Exits)** to prevent race conditions (e.g. double-click bugs)
  - Modern Python Type Hinting (`dict[str, Any]`, `-> None`) throughout

---

## Tech Stack

| Area | Technology |
|---|---|
| Language | Python 3 |
| GUI Framework | CustomTkinter |
| HTTP Client | curl-cffi (browser impersonation) |
| HTML Parsing | BeautifulSoup4 + lxml |
| Concepts | Multi-threading, Thread-Safe Queues, JSON Persistence, OOP, Regex |

---

## How to Run

### 1. Prerequisites

Clone the repository and install the required dependencies:

```bash
pip install customtkinter curl-cffi beautifulsoup4 lxml
```

### 2. Configuration (Search URL)

Due to the dynamic nature of job portals, you need to provide your own Stepstone search URL:

1. Go to Stepstone and perform your desired job search
2. Check the bottom of the results page for the total number of available pages
3. Copy the URL from your browser
4. Replace the URL in the `get_query_url` method in `scraper.py`
5. At launch, enter the number of pages to scrape (up to the maximum your search returns)

### 3. Run

```bash
python main.py
```

---

## File Structure

```
├── main.py                  # GUI, app logic, state management
├── scraper.py               # Scraping engine, filtering, anti-bot logic
├── file_manager.py          # All file I/O (JSON, plaintext)
├── custom_input_dialog.py   # Reusable modal dialogs (filter words, notes)
└── files/
    ├── unseen_jobs.json         # Jobs not yet reviewed
    ├── seen_links.txt           # Permanently seen URLs
    ├── words_to_filter.txt      # Your custom filter word list
    ├── company_notes.json       # Per-company notes
    ├── backlog.json             # Saved-for-later jobs
    ├── unfiltered_jobdata.json  # Raw scrape output (for analysis)
    └── cached_jobs.json         # Session resume cache
```