import asyncio
from typing import List, Dict, Any
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class TopcoderScraper(BaseScraper):
    def __init__(self):
        super().__init__(base_url="https://www.topcoder.com/challenges")

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
                await page.wait_for_timeout(4000)
                past_tab = page.locator('li:has-text("Past Challenges")')
                if await past_tab.is_visible():
                    await past_tab.click()
                    await page.wait_for_timeout(3000)
                view_more_selector = "a._2UekLS:has-text('View more challenges')"
                for i in range(15):
                    try:
                        view_more_btn = page.locator(view_more_selector)
                        if await view_more_btn.is_visible():
                            await view_more_btn.click()
                            await page.wait_for_timeout(2000)
                        else:
                            print(f"[*] 'View more challenges' button no longer visible at iteration {i}.")
                            break
                    except Exception as click_err:
                        print(f"[*] Pagination boundary met or element trace lost: {click_err}")
                        break
                
                html = await page.content()
                pages.append(html)
                
            except Exception as e:
                print(f"[Error] Failed to capture raw stream from Topcoder: {e}")
            finally:
                await browser.close()
                
        return pages

    def parse_data(self, raw_elements: List[str]) -> List[Dict[str, Any]]:
        items = []
        if not raw_elements:
            return items

        soup = BeautifulSoup(raw_elements[0], "html.parser")
        card_rows = soup.select("div._1TmHFU")
        
        for row in card_rows:
            try:
                anchor = row.select_one("a.vir_2D")
                if not anchor:
                    continue
                href = anchor.get("href", "")
                if not href:
                    continue
                full_url = href if href.startswith("http") else f"https://www.topcoder.com{href}"

                title_text = anchor.get_text(strip=True)

                tag_buttons = row.select("div.YQ-XDy button, div._3oucuU button")
                tags = [btn.get_text(strip=True) for btn in tag_buttons if btn.get_text(strip=True)]

                purse_el = row.select_one("div._3U9-m3, div._3Ms6oa")
                purse_text = purse_el.get_text(strip=True) if purse_el else "Fun/Recognition Only"
                
                description = f"Purse: {purse_text}. Tags/Skills: {', '.join(tags)}." if tags else f"Purse: {purse_text}."
                
                if not any(x["url"] == full_url for x in items):
                    items.append({
                        "title": title_text,
                        "url": full_url,
                        "description": description,
                        "source": "topcoder"
                    })
            except Exception as e:
                print(f"[Warning] Error isolated parsing single Topcoder listing row: {e}")
                continue
                
        return items