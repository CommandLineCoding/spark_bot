import asyncio
from typing import List, Dict, Any
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class DoraHacksScraper(BaseScraper):
    def __init__(self):
        super().__init__(base_url="https://dorahacks.io/hackathon")

    async def fetch_raw_data(self) -> List[str]:
        pages = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            ctx = await browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await ctx.new_page()
            
            try:
                await page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)

                view_more_selector = "button:has-text('View More')"

                for i in range(10):
                    try:
                        button = page.locator(view_more_selector)
                        if await button.is_visible():
                            await button.click()
                            await page.wait_for_timeout(2000)
                        else:
                            print(f"[*] 'View More' button hidden or reached end of list at iteration {i}.")
                            break
                    except Exception as click_err:
                        print(f"[*] No more load actions possible: {click_err}")
                        break
                
                html = await page.content()
                pages.append(html)
                
            except Exception as e:
                print(f"[Error] Failed to fetch data from DoraHacks: {e}")
            finally:
                await browser.close()
                
        return pages

    def parse_data(self, raw_elements: List[str]) -> List[Dict[str, Any]]:
        items = []
        if not raw_elements:
            return items

        soup = BeautifulSoup(raw_elements[0], "html.parser")

        cards = soup.select("ul.hackathon-list li a")
        
        for card in cards:
            try:
                title_el = card.select_one("span[class*='font-semibold'][class*='line-clamp-2']")
                if not title_el:
                    continue

                href = card.get("href", "")
                if not href:
                    continue
                full_url = href if href.startswith("http") else f"https://dorahacks.io{href}"

                tag_elements = card.select("div[class*='bg-accent-bg']")
                tags = [tag.get_text(strip=True) for tag in tag_elements if tag.get_text(strip=True)]

                org_el = card.select_one("span[class*='text-ink-secondary'].truncate")
                org_name = org_el.get_text(strip=True) if org_el else "Unknown Organizer"
                
                description = f"Organized by: {org_name}. Focus Categories: {', '.join(tags)}." if tags else f"Organized by: {org_name}."
                
                items.append({
                    "title": title_el.get_text(strip=True),
                    "url": full_url,
                    "description": description,
                    "source": "dorahacks"
                })
            except Exception as e:
                print(f"[Warning] Error parsing a specific DoraHacks item card: {e}")
                continue
                
        return items