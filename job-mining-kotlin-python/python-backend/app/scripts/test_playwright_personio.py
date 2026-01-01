import asyncio
from app.infrastructure.io.js_scraper import scrape_with_rendering

URLS = [
    "https://escape.jobs.personio.com/job/742758?language=de&display=de",
    "https://escape.jobs.personio.com/job/1118877?language=de&display=de",
]

async def main():
    for url in URLS:
        print(f"=== TEST JS RENDER: {url} ===")
        try:
            text = await scrape_with_rendering(url)
            print(f"Text length: {len(text)}")
            print(text[:500])
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
