# Book Parser

A scraper for books.toscrape.com.

## Versions

- **v0** — a draft built to verify that scraping is possible. It scrapes only
  the first book it finds on the page. Its output is pretty-printed JSON
  printed to the terminal; it does not write any file. Stays in the repo
  as-is.
- **v1** — the main working version. Takes the number of books to scrape as a
  CLI argument, calculates how many catalogue pages are needed, scrapes them
  synchronously, and saves the result to `output.json`. It prints progress to
  the terminal.

## How v1 works

1. `v1.py` is run from the terminal with a single required argument — the
   number of books to scrape.
2. That number is divided by the number of books per page (20) and rounded up
   to determine how many catalogue pages need to be fetched.
3. For each page the pipeline runs `scrape_page` → `parse_books`
   (synchronously, page by page). Each page request has a 15-second timeout
   and is retried up to 3 times on timeout or connection error.
4. At the end all parsed books are written to `output.json` in the project
   root. If fewer books were parsed than requested, the script reports the
   actual count and still writes the file.

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
python v1.py <number_of_books> [--delay SECONDS] [-g]
```

Arguments:

- `<number_of_books>` — how many books to scrape (required, integer).
- `--delay SECONDS` — delay in seconds used between retries and (with `-g`)
  between page requests. Default: `5`.
- `-g` — "gentle" mode: sleep `--delay` seconds after each successfully
  scraped page to avoid hitting the server too hard.

Examples:

```bash
# Scrape 40 books with default settings
python v1.py 40

# Scrape 100 books, 2-second delay, gentle mode
python v1.py 100 --delay 2 -g

# Show help
python v1.py --help
```

The result is written to `output.json` in the project root.

`v0.py` is kept for reference — it just grabs the first book on the page and
prints it to the terminal as indented JSON:

```bash
python v0.py
```

## Output format

`output.json` is a JSON array of objects. `url` and `title` are always
present and non-null (books without them are skipped during parsing).
`rating`, `price` and `availability` may be `null` if the corresponding
element was not found on the page:

```json
[
    {
        "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "rating": "Three",
        "title": "A Light in the Attic",
        "price": "£51.77",
        "availability": "In stock"
    }
]
```

## Limitations

- The script is synchronous: pages are fetched one after another, so a large
  `number_of_books` value means a proportionally longer runtime.
- books.toscrape.com contains 1000 books in total. Requesting more than that
  will return fewer entries than asked; the script reports the actual count.
- Each page request is retried up to 3 times on timeout or connection error. If a page fails with a 404 error, the script stops,
  assuming there are no further pages, and saves whatever has already been collected. As a result, output.json may contain fewer books than requested even though the script completes successfully.

## License

MIT
