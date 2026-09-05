import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def collect_job_description(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove elements that usually contain navigation/noise
    for element in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header"
    ]):
        element.decompose()

    text = soup.get_text(
        separator="\n",
        strip=True
    )

    # Remove excessive blank lines
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    cleaned_text = "\n".join(lines)

    return cleaned_text


if __name__ == "__main__":

    test_url = input("Enter job URL: ").strip()

    try:
        text = collect_job_description(test_url)

        print("\n=== COLLECTED PAGE TEXT ===")
        print(text[:10000])

        print("\n=== COLLECTION COMPLETE ===")
        print(f"Characters collected: {len(text)}")

    except Exception as e:
        print(f"\nERROR: {e}")