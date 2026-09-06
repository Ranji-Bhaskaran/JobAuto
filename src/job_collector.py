from playwright.sync_api import sync_playwright


def collect_job_description(url):
    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 900
            }
        )

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # Give JavaScript-rendered content time to appear
        page.wait_for_timeout(3000)

        text = page.locator("body").inner_text()

        browser.close()

        return text.strip()


if __name__ == "__main__":

    test_url = input("Enter job URL: ").strip()

    try:
        text = collect_job_description(test_url)

        print("\n=== COLLECTED PAGE TEXT ===")
        print(text[:15000])

        print("\n=== COLLECTION COMPLETE ===")
        print(f"Characters collected: {len(text)}")

    except Exception as e:
        print(f"\nERROR: {e}")