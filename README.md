# Book Parser

A scraper for books.toscrape.com.

## Versions

- **v0** — a draft built to verify that scraping is possible. It scrapes only
  the first book it finds on the page. Its output is pretty-printed JSON
  printed to the terminal; it does not write any file. Stays in the repo
  as-is.
- **v1** — the main working version. Takes the number of books to scrape as a
  CLI argument, calculates how many catalogue pages are needed, scrapes them
  synchronously, and saves the result to `output.json`. It does not print to
  the terminal.

## How v1 works

1. `v1.py` is run from the terminal with a single argument — the number of
   books to scrape.
2. That number is divided by the number of books per page and rounded up to
   determine how many catalogue pages need to be fetched.
3. For each page the pipeline runs `scrape_page` → `parse_books`
   (synchronously, page by page).
4. At the end all parsed books are written to `output.json`.

## Installation

Run the following commands **from the project root directory**.

```bash
# 1. Create a virtual environment
python -m venv venv

# 2. Activate it
# Linux / macOS:
source venv/bin/activate
# Windows (cmd/PowerShell):
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python v1.py <number_of_books>
```

Example — scrape 40 books:

```bash
python v1.py 40
```

The result is written to `output.json` in the project root.

`v0.py` is kept for reference — it just grabs the first book on the page and
prints it to the terminal as indented JSON:

```bash
python v0.py
```

## License

MIT
