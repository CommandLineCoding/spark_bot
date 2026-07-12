import asyncio
from src.scrapers.devfolio import DevfolioScraper
from src.scrapers.dorahacks import DoraHacksScraper

async def main():
    print("[*] Starting OpenSpark Bot Engine...")
    
    devfolio = DevfolioScraper()
    dorahacks = DoraHacksScraper()
        
    print("[*] Fetching live data from Devfolio and DoraHacks...")
    dev_raw, dora_raw = await asyncio.gather(
        devfolio.fetch_raw_data(),
        dorahacks.fetch_raw_data()
    )
    
    dev_items = devfolio.parse_data(dev_raw)
    dora_items = dorahacks.parse_data(dora_raw)
    
    print(f"\n[+] Extracted {len(dev_items)} items from Devfolio")
    print(f"[+] Extracted {len(dora_items)} items from DoraHacks")

if __name__ == "__main__":
    asyncio.run(main())