import asyncio
from src.scrapers.devfolio import DevfolioScraper

async def main():
    print(">_ Starting OpenSpark Bot Engine...")
    devfolio = DevfolioScraper()
    
    print(f">_ Fetching live data from {devfolio.base_url}...")
    raw_html = await devfolio.fetch_raw_data()
    
    print(">_ Parsing items...")
    parsed_items = devfolio.parse_data(raw_html)
    
    print(f"\n>_ Successfully extracted {len(parsed_items)} items from Devfolio:")
    for item in parsed_items[:3]:
        print(f" - {item['title']} | {item['url']}")

if __name__ == "__main__":
    asyncio.run(main())