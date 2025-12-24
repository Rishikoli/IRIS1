import logging
import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CartographerAgent:
    """Agent 12: The Cartographer - Geo-Spatial Intelligence for RPTs"""

    def __init__(self):
        self._initialize_gemini()
        # List of known tax havens/offshore jurisdictions
        self.tax_havens = [
            "Cayman Islands", "Mauritius", "British Virgin Islands", "BVI", 
            "Bermuda", "Panama", "Jersey", "Guernsey", "Isle of Man", 
            "Luxembourg", "Cyprus", "Seychelles", "Bahamas", "Ireland", 
            "Singapore", "Hong Kong", "Switzerland", "Netherlands", "Delaware"
        ]

    def _initialize_gemini(self):
        """Initialize Gemini model"""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.error("GEMINI_API_KEY not found")
                return
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Gemini model initialized for Cartographer Agent")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")

    def analyze_locations(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes a list of entities (names) and infers their physical location.
        Returns the list with added 'location' and 'is_tax_haven' fields.
        """
        if not entities:
            return []

        entity_names = [e.get('name') for e in entities if e.get('name')]
        if not entity_names:
            return entities

        try:
            import time
            max_retries = 3
            retry_delay = 10
            
            # Batch process with Gemini
            prompt = f"""
            I have a list of corporate entities related to Indian companies.
            Your task is to:
            1. Infer the likely Country and City of incorporation/operation for each entity based on its name and common corporate structures.
            2. Provide approximate Latitude and Longitude for that city/country.
            3. Determine if it is a known Tax Haven or Offshore Jurisdiction.

            Entities:
            {json.dumps(entity_names)}

            Return JSON format ONLY:
            {{
                "locations": [
                    {{
                        "name": "Entity Name",
                        "city": "City",
                        "country": "Country",
                        "lat": 0.0,
                        "lng": 0.0,
                        "is_tax_haven": boolean,
                        "reason": "Why tax haven?"
                    }}
                ]
            }}
            """
            
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content(prompt)
                    text_resp = response.text.strip()
                    
                    # Clean markdown
                    if text_resp.startswith("```json"):
                        text_resp = text_resp[7:-3]
                    elif text_resp.startswith("```"):
                        text_resp = text_resp[3:-3]
                    
                    location_data = json.loads(text_resp).get("locations", [])
                    break # Success
                except Exception as e:
                    if "429" in str(e) and attempt < max_retries - 1:
                        logger.warning(f"Rate limit hit, retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        raise e # Re-raise if not rate limit or max retries reached
            
            # Map back to original entities
            location_map = {item['name']: item for item in location_data}
            
            enriched_entities = []
            for entity in entities:
                name = entity.get('name')
                loc_info = location_map.get(name)
                
                if loc_info:
                    entity['location'] = {
                        "city": loc_info.get('city', 'Unknown'),
                        "country": loc_info.get('country', 'Unknown'),
                        "lat": loc_info.get('lat'),
                        "lng": loc_info.get('lng')
                    }
                    entity['is_tax_haven'] = loc_info.get('is_tax_haven', False)
                    entity['tax_haven_reason'] = loc_info.get('reason', "")
                else:
                    # Fallback for unknown
                    entity['location'] = {"city": "Unknown", "country": "Unknown", "lat": 0, "lng": 0}
                    entity['is_tax_haven'] = False
                
                enriched_entities.append(entity)
                
            return enriched_entities

        except Exception as e:
            logger.error(f"Cartographer analysis failed: {e}")
            return entities
