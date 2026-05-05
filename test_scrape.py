import requests

def test_scrape():
    url = "https://dir.indiamart.com/search.mp?ss=shoes"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {res.status_code}")
        with open("indiamart_dump.html", "wb") as f:
            f.write(res.content)
        print("Wrote HTML to indiamart_dump.html")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_scrape()
