from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScraper(ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url

    @abstractmethod
    async def fetch_raw_data(self) -> List[Dict[str, Any]]:
        """
        Fetches raw data (HTML or JSON) from the targeted data source.
        Must be implemented by every platform scraper.
        """
        pass

    @abstractmethod
    def parse_data(self, raw_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts specific fields (title, date, description, links) 
        and prepares them for the data cleaning pipeline.
        """
        pass