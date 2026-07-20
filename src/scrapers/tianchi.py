import asyncio
from typing import List, Dict, Any
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class TianchiScraper(BaseScraper):
    def __init__(self):
        super().__init__(base_url="https://tianchi.aliyun.com/competition/")
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
                await page.wait_for_timeout(4000)
                for _ in range(15):
                    html = await page.content()
                    html_list.append(html)
                    next_btn = page.locator("li.ant-pagination-next")
                    if await next_btn.is_visible() and not "ant-pagination-disabled" in (await next_btn.get_attribute("class") or ""):
                        await next_btn.click()
                        await page.wait_for_timeout(2500)
                    else:
                        print("[*] Reached last page or next indicator is disabled.")
                        break
            except Exception as err:
                print(f"[Error] Failed parsing raw stream from Tianchi: {err}")
            finally:
                await browser.close()
        return html_list

    def parse_data(self, raw_elements: List[str]) -> List[Dict[str, Any]]:
        items = []
        if not raw_elements:
            return items

        for html in raw_elements:
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select("a._23a3f979aea8674bba6bbe15966fac4e_card")
            for card in cards:
                try:
                    title_el = card.select_one("h1._23a3f979aea8674bba6bbe15966fac4e_text_title")
                    if not title_el:
                        continue
                    title_text = title_el.get_text(" ", strip=True)
                    href = card.get("href", "")
                    if not href:
                        continue
                    full_url = href if href.startswith("http") else f"https://tianchi.aliyun.com{href}"
                    desc_el = card.select_one("p._23a3f979aea8674bba6bbe15966fac4e_text_content")
                    desc_text = desc_el.get_text(strip=True) if desc_el else ""
                    bonus_el = card.select_one("div._23a3f979aea8674bba6bbe15966fac4e_bonus")
                    bonus_text = bonus_el.get_text(" ", strip=True) if bonus_el else "Standard Recognition"
                    final_desc = desc_text if desc_text else f"Pool Details: {bonus_text}"
                    if not any(x["url"] == full_url for x in items):
                        items.append({
                            "title": title_text,
                            "url": full_url,
                            "description": final_desc,
                            "source": "tianchi"
                        })
                except Exception as parse_err:
                    print(f"[Warning] Error localized inside inner layout template loop: {parse_err}")
                    continue
                    
        return items