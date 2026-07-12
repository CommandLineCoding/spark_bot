import asyncio
from src.scrapers.devfolio import DevfolioScraper
from src.scrapers.dorahacks import DoraHacksScraper
from src.scrapers.tianchi import TianchiScraper
from src.scrapers.topcoder import TopcoderScraper

async def main():
    print("[*] Launching OpenSpark Bot Core execution context...")
    
    scrapers = [
        DevfolioScraper(),
        DoraHacksScraper(),
        TianchiScraper(),
        TopcoderScraper()
    ]

    print(f"[*] Initializing asynchronous processing for {len(scrapers)} active sweep engines...")
    raw_results = await asyncio.gather(*[s.fetch_raw_data() for s in scrapers])
    
    for scraper, raw_html in zip(scrapers, raw_results):
        parsed = scraper.parse_data(raw_html)
        print(f"[+] Engine Result -> Source: {scraper.__class__.__name__} | Extracted Items Count: {len(parsed)}")

if __name__ == "__main__":
    asyncio.run(main())