import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import sys

BOOKS_PER_PAGE = 20


def parse_books(html: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")

    parsed_books = []
    books = soup.find_all(class_="product_pod")

    for book in books:
        heading = book.select_one("h3 > a")
        if not heading:
            print(f"Book No. {len(parsed_books)} was not processed")
            continue

        relative_url = heading.get("href")
        url = urljoin("https://books.toscrape.com/", relative_url)

        title = heading.get("title")

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

        print(f"Book No. {len(parsed_books)+1} has been processed")

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
    response = requests.get(f"https://books.toscrape.com/catalogue/page-{index}.html")
    if response.status_code == 404:
        print(f"404 Not Found. Page #{index}")
        return None
    response.raise_for_status()

    print("The page was scraped")

    return response.text


def pipeline(quantity: int) -> None:
    output = []

    pages = (quantity + BOOKS_PER_PAGE - 1) // BOOKS_PER_PAGE
    indexs = range(1, pages + 1)

    for index in indexs:
        html = scrape_page(index)
        if not html:
            break

        parsed_books = parse_books(html)

        output.extend(parsed_books)

    output = output[:quantity]

    print("Saved to output.json")
    with open("output.json", "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4)


if __name__ == "__main__":
    try:
        pipeline(int(sys.argv[1]))
    except ValueError:
        print("The quantity must be an integer")
    except Exception:
        print(r"Usage: python v1.py {quantity}")
