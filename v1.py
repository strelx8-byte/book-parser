import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import argparse
import time

BOOKS_PER_PAGE = 20


def parse_books(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")

    parsed_books = []
    processed_books = 0
    books = soup.find_all(class_="product_pod")

    for book in books:
        heading = book.select_one("h3 > a")
        if not heading:
            print(f"Book No. {processed_books+1} was not processed")
            print("Heading was not found")
            processed_books += 1
            continue

        relative_url = heading.get("href")
        if not relative_url:
            print(f"Book No. {processed_books+1} was not processed")
            print("Relative_url was not found")
            processed_books += 1
            continue
        url = urljoin("https://books.toscrape.com/", relative_url)

        title = heading.get("title")
        if not title:
            print(f"Book No. {processed_books+1} was not processed")
            print("Title was not found")
            processed_books += 1
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

        print(f"Book No. {processed_books+1} has been processed")
        processed_books += 1

        result = {
            "url": url,
            "rating": rating,
            "title": title,
            "price": price,
            "availability": availability,
        }

        parsed_books.append(result)

    return parsed_books


def scrape_page(index: int) -> str | None:
    inner_html = None

    for attempt in range(1, 4):
        try:
            response = requests.get(
                f"https://books.toscrape.com/catalogue/page-{index}.html", timeout=15
            )
            response.raise_for_status()

            inner_html = response.text

            print(f"[{attempt}/3] The page was scraped")

            break
        except requests.exceptions.Timeout:
            print(f"[{attempt}/3] Request timeout exceeded")

            time.sleep(DELAY)
        except requests.exceptions.HTTPError as exception:
            print(f"[{attempt}/3] {exception}")

            break

    return inner_html


def pipeline(quantity: int) -> None:
    output = []

    pages = (quantity + BOOKS_PER_PAGE - 1) // BOOKS_PER_PAGE
    pages_indexs = range(1, pages + 1)

    for page_index in pages_indexs:
        inner_html = scrape_page(page_index)
        if not inner_html:
            continue

        parsed_books = parse_books(inner_html)

        output.extend(parsed_books)

        if GENTLE:
            print(f"Delay between requests: {DELAY} seconds") 
            time.sleep(DELAY)

    output = output[:quantity]

    if not output:
        print("The program failed to parse anything")

        return None
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

    DELAY = args.delay
    GENTLE = args.g

    pipeline(args.quantity)
