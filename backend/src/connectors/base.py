from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseConnector(ABC):
    """Abstract base class for all data connectors"""

    @abstractmethod
    def ingest(self, source: str) -> List[Dict[str, Any]]:
        """
        Ingest data from a source and return a list of documents.
        
        Args:
            source: The source identifier (file path, URL, etc.)
            
        Returns:
            List of dictionaries containing 'text' and 'metadata'
        """
        pass
