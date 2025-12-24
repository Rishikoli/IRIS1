
import sys
import os
import logging
from pprint import pprint

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Mock settings and DB
from unittest.mock import MagicMock
sys.modules['src.config'] = MagicMock()
sys.modules['src.database.connection'] = MagicMock()
sys.modules['src.config.settings'] = MagicMock()

# Import Agent
try:
    from src.agents.forensic.agent4_compliance import ComplianceValidationAgent, ComplianceFramework
    print("Agent imported successfully.")
    
    agent = ComplianceValidationAgent()
    print("Agent instantiated.")
    
    print("\n--- Loaded Rules ---")
    for framework in ComplianceFramework:
        rules = agent.compliance_rules.get(framework, {})
        print(f"\nFramework: {framework.value}")
        print(f"Rule Count: {len(rules)}")
        if len(rules) > 0:
            pprint(list(rules.keys()))
            
    # Simple check
    if len(agent.compliance_rules.get(ComplianceFramework.SEBI, {})) > 0:
        print("\nSUCCESS: SEBI rules loaded from JSON.")
    else:
        print("\nFAILURE: SEBI rules NOT loaded.")
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
