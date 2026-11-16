import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

if __name__ == "__main__":
    response = requests.get("https://books.toscrape.com/", timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    book = soup.find(class_="product_pod")
    if not book:
        raise RuntimeError("book is not found")

    heading = book.select_one("h3 > a")
    if not heading:
        raise RuntimeError("heading is not found")

    relative_url = heading.get("href")
    url = urljoin("https://books.toscrape.com/", relative_url)

    title = heading.get("title")

    rating_element = book.find(class_="star-rating")
    if not rating_element:
        raise RuntimeError("rating_element is not found")
    rating = next(
        (x for x in rating_element.get("class", []) if x != "star-rating"), None
    )

    price_element = book.find(class_="price_color")
    if not price_element:
        raise RuntimeError("price_element is not found")
    price = price_element.get_text(strip=True)

    availability_element = book.find(class_="availability")
    if not availability_element:
        raise RuntimeError("availability_element is not found")
    availability = availability_element.get_text(strip=True)

    result = {
        "url": url,
        "rating": rating,
        "title": title,
        "price": price,
        "availability": availability,
    }

    print(json.dumps(result, indent=2))
