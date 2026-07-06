import asyncio
from typing import List, Dict, Any
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class DevfolioScraper(BaseScraper):
    def __init__(self):
        super().__init__(base_url="https://devfolio.co/hackathons/past")

    async def fetch_raw_data(self) -> List[str]:
        raw_html_pages = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                await page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)
                for _ in range(1000):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                    await page.wait_for_timeout(1500)
                
                content = await page.content()
                raw_html_pages.append(content)
                
            except Exception as e:
                print(f"[Error] Failed to fetch data from Devfolio: {e}")
            finally:
                await browser.close()
                
        return raw_html_pages

    def parse_data(self, raw_elements: List[str]) -> List[Dict[str, Any]]:
        extracted_projects = []
        if not raw_elements:
            return extracted_projects

        soup = BeautifulSoup(raw_elements[0], "html.parser")
        cards = soup.select("div[class*='HackathonCard']") 
        
        for card in cards:
            try:
                title_el = card.select_one("h3, h2, .title")
                link_el = card.select_one("a")
                desc_el = card.select_one(".description, p")
                
                if title_el:
                    extracted_projects.append({
                        "title": title_el.get_text(strip=True),
                        "url": link_el["href"] if link_el and link_el.has_attr("href") else self.base_url,
                        "description": desc_el.get_text(strip=True) if desc_el else "",
                        "source": "devfolio"
                    })
            except Exception as e:
                print(f"[Warning] Error parsing a specific card item: {e}")
                continue
                
        return extracted_projects