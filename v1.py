import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import argparse
import time
from typing import TypedDict

BOOKS_PER_PAGE = 20


class Book(TypedDict):
    url: str
    rating: str | None
    title: str
    price: str | None
    availability: str | None


def parse_books(html: str) -> list[Book]:
    def skip(book_index: int, reason: str | None = None) -> None:
        print(f"Book No. {book_index} was not processed")
        if reason:
            print(reason)

    soup = BeautifulSoup(html, "html.parser")

    parsed_books = []
    books = soup.find_all(class_="product_pod")

    for book_index, book in enumerate(books, 1):
        heading = book.select_one("h3 > a")
        if not heading:
            skip(book_index, "Heading was not found")
            continue

        relative_url = heading.get("href")
        if not relative_url:
            skip(book_index, "Relative_url was not found")
            continue
        url = urljoin("https://books.toscrape.com/", relative_url)

        title = heading.get("title")
        if not title:
            skip(book_index, "Title was not found")
            continue

        rating = None
        price = None
        availability = None

        rating_element = book.find(class_="star-rating")
        if rating_element:
            rating = next(
                (x for x in rating_element.get("class", []) if x != "star-rating"), None
            )

        price_element = book.find(class_="price_color")
        if price_element:
            price = price_element.get_text(strip=True)

        availability_element = book.find(class_="availability")
        if availability_element:
            availability = availability_element.get_text(strip=True)

        print(f"Book No. {book_index} has been processed")

        result: Book = {
            "url": url,
            "rating": rating,
            "title": title,
            "price": price,
            "availability": availability,
        }

        parsed_books.append(result)

    return parsed_books


def scrape_page(index: int, delay: int) -> tuple[str | None, int | None]:
    inner_html = None
    status = None

    for attempt in range(1, 4):
        try:
            response = requests.get(
                f"https://books.toscrape.com/catalogue/page-{index}.html", timeout=15
            )
            response.raise_for_status()

            inner_html = response.text

            print(f"[{attempt}/3] The page was scraped")

            break
        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ) as exc:
            print(f"[{attempt}/3] Request not fulfilled\n{exc}")
            if attempt < 3:
                time.sleep(delay)
        except requests.exceptions.HTTPError as exc:
            print(f"[{attempt}/3] {exc}")
            status = exc.response.status_code if exc.response is not None else None
            break

    return inner_html, status


def pipeline(quantity: int, delay: int, gentle: bool) -> None:
    output = []

    pages = (quantity + BOOKS_PER_PAGE - 1) // BOOKS_PER_PAGE
    pages_indices = range(1, pages + 1)

    for page_index in pages_indices:
        inner_html, status = scrape_page(page_index, delay)

        if status == 404:
            break
        if not inner_html:
            continue

        parsed_books = parse_books(inner_html)

        output.extend(parsed_books)

        print(f"Already parsed: {len(output)}/{quantity}")

        if gentle:
            print(f"Delay between requests: {delay} seconds")
            time.sleep(delay)

    output = output[:quantity]

    if not output:
        print("The program failed to parse anything")

        return
    elif len(output) < quantity:
        print("The program cannot parse any more")

    print(f"Was parsed: {len(output)}/{quantity}")

    with open("output.json", "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=4)

    print("Saved to output.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrapes the site books.toscrape.com")

    parser.add_argument("quantity", type=int, help="The number of books to scrape")
    parser.add_argument(
        "--delay", type=int, default=5, help="Delay between page scraping and timeouts"
    )
    parser.add_argument(
        "-g",
        action="store_true",
        default=False,
        help="Gentle scraping: adding delays between requests to pages (the delay can be configured using the --delay argument)",
    )

    args = parser.parse_args()

    pipeline(args.quantity, args.delay, args.g)
