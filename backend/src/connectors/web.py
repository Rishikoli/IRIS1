import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
from .base import BaseConnector

class WebConnector(BaseConnector):
    """Connector for ingesting Web pages"""

    def ingest(self, source: str) -> List[Dict[str, Any]]:
        """
        Extract text from a URL.
        
        Args:
            source: URL to scrape
            
        Returns:
            List of documents (usually one per page)
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(source, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
                
            # Get text
            text = soup.get_text(separator='\n')
            
            # Clean text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            title = soup.title.string if soup.title else source
            
            return [{
                'text': text,
                'metadata': {
                    'source': source,
                    'title': title,
                    'access_date': datetime.now().isoformat(),
                    'type': 'web'
                }
            }]
            
        except Exception as e:
            raise Exception(f"Failed to process URL {source}: {str(e)}")
