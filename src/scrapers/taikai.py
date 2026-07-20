import asyncio
from typing import List, Dict, Any
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class TaikaiScraper(BaseScraper):
    def __init__(self):
        super().__init__(base_url="https://taikai.network/hackathons")

    async def fetch_raw_data(self) -> List[str]:
        html_list = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            ctx = await browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await ctx.new_page()
            
            try:
                await page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3500)

                for _ in range(15):
                    html = await page.content()
                    html_list.append(html)

                    next_btn = page.locator("li.next:not(.disabled) a")
                    if await next_btn.is_visible():
                        await next_btn.click()
                        await page.wait_for_timeout(2500)
                    else:
                        print("[*] Reached index boundary list cap or page is flat.")
                        break
                        
            except Exception as err:
                print(f"[Error] Failed to fetch TAIKAI network stream: {err}")
            finally:
                await browser.close()
                
        return html_list

    def parse_data(self, raw_elements: List[str]) -> List[Dict[str, Any]]:
        items = []
        if not raw_elements:
            return items

        for html in raw_elements:
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select("div.styles-module__Yh3-Za__wrapper")
            
            for card in cards:
                try:
                    status_el = card.select_one("div.styles-module__Yh3-Za__state")
                    if not status_el or "Finished" not in status_el.get_text():
                        continue
                    
                    anchor = card.select_one("a")
                    if not anchor:
                        continue
                        
                    href = anchor.get("href", "")
                    if not href:
                        continue
                    full_url = href if href.startswith("http") else f"https://taikai.network{href}"
                    
                    title_el = card.select_one("div.styles-module__Yh3-Za__content h3")
                    title_text = title_el.get_text(strip=True) if title_el else "Unnamed Hackathon"
                    
                    desc_el = card.select_one("div.styles-module__Yh3-Za__content span")
                    desc_text = desc_el.get_text(strip=True) if desc_el else ""
                    
                    prize_el = card.select_one("div.styles-module__Yh3-Za__prize div")
                    prize_text = prize_el.get_text(" ", strip=True) if prize_el else "Recognition Only"

                    tag_nodes = card.select("div.styles-module__Yh3-Za__tags span")
                    tags = [t.get_text(strip=True) for t in tag_nodes if t.get_text(strip=True)]
                    
                    final_desc = f"{desc_text} | Pool: {prize_text}"
                    if tags:
                        final_desc += f" | Tags: {', '.join(tags)}"
                    
                    if not any(x["url"] == full_url for x in items):
                        items.append({
                            "title": title_text,
                            "url": full_url,
                            "description": final_desc,
                            "source": "taikai"
                        })
                except Exception as parse_err:
                    print(f"[Warning] Localized parsing skip inside individual layout node: {parse_err}")
                    continue
                    
        return items