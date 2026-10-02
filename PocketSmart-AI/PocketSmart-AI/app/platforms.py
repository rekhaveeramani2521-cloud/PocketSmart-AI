from urllib.parse import quote_plus


def search_url(platform: str, query: str) -> str:
    q = quote_plus(query.strip())
    key = platform.lower()
    if key == "amazon":
        return f"https://www.amazon.in/s?k={q}"
    if key == "flipkart":
        return f"https://www.flipkart.com/search?q={q}"
    if key == "ikea":
        return f"https://www.ikea.com/in/en/search/?q={q}"
    if key == "swiggy":
        return f"https://www.swiggy.com/search?query={q}"
    if key == "zomato":
        return "https://www.zomato.com/"
    if key == "oyo":
        return "https://www.oyorooms.com/"
    return f"https://www.google.com/search?q={quote_plus(platform + ' ' + query)}"
