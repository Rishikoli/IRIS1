from src.agents.forensic.agent12_cartographer import CartographerAgent
from src.agents.forensic.agent13_time_traveler import TimeTravelerAgent
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_agents():
    # Test Agent 12: The Cartographer
    print("\n--- Testing Agent 12: The Cartographer ---")
    cartographer = CartographerAgent()
    entities = [
        {"name": "Reliance Jio Infocomm Limited"},
        {"name": "Jio Platforms Limited"},
        {"name": "Reliance Industrial Investments and Holdings Limited (Mauritius)"}
    ]
    enriched_entities = cartographer.analyze_locations(entities)
    print(json.dumps(enriched_entities, indent=2))

    # Test Agent 13: The Time Traveler
    print("\n--- Testing Agent 13: The Time Traveler ---")
    time_traveler = TimeTravelerAgent()
    historical_data = {
        "revenue": [
            {"year": 2021, "value": 5000},
            {"year": 2022, "value": 5500},
            {"year": 2023, "value": 6200},
            {"year": 2024, "value": 7000}
        ],
        "net_income": [
            {"year": 2021, "value": 500},
            {"year": 2022, "value": 600},
            {"year": 2023, "value": 750},
            {"year": 2024, "value": 900}
        ]
    }
    predictions = time_traveler.predict_future_performance(historical_data)
    print(json.dumps(predictions, indent=2))

if __name__ == "__main__":
    test_agents()
