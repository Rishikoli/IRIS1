
import os
import re
from pathlib import Path

def verify_agent_configs():
    backend_src = Path("/home/aditya/Downloads/IRIS/backend/src")
    target_model = "gemini-2.5-flash"
    
    print(f"🔍 Verifying all agents are using: {target_model}")
    
    files_to_check = [
        "agents/agent7_qa_rag.py",
        "agents/agent8_market_sentiment.py",
        "agents/forensic/agent5_reporting.py",
        "agents/forensic/agent9_network_analysis.py",
        "agents/forensic/agent10_auditor.py",
        "agents/forensic/agent12_cartographer.py"
    ]
    
    all_good = True
    
    for relative_path in files_to_check:
        file_path = backend_src / relative_path
        if not file_path.exists():
            print(f"⚠️ File not found: {relative_path}")
            continue
            
        try:
            content = file_path.read_text()
            # Look for GenerativeModel instantiations
            # Regex to capture what's inside GenerativeModel(...)
            matches = re.finditer(r"GenerativeModel\s*\(\s*['\"]([^'\"]+)['\"]\s*", content)
            
            found = False
            file_ok = True
            
            for match in matches:
                found = True
                model_name = match.group(1)
                
                # Check for model_name argument format too
                # e.g. model_name="gemini-2.5-flash"
                
                if model_name != target_model:
                     print(f"❌ {relative_path}: Found incorrect model '{model_name}'")
                     file_ok = False
                     all_good = False
                else:
                     print(f"✅ {relative_path}: Found correct model '{model_name}'")
                     
            # Also check for named arguments like model_name="..."
            matches_named = re.finditer(r"model_name\s*=\s*['\"]([^'\"]+)['\"]", content)
            for match in matches_named:
                 found = True
                 model_name = match.group(1)
                 if model_name != target_model:
                     print(f"❌ {relative_path}: Found incorrect model_name arg '{model_name}'")
                     file_ok = False
                     all_good = False
                 else:
                     print(f"✅ {relative_path}: Found correct model_name arg '{model_name}'")
            
            if not found:
                print(f"⚠️ {relative_path}: No GenerativeModel instantiation found (might use inheritance or differnt pattern)")
            
        except Exception as e:
            print(f"❌ Error reading {relative_path}: {e}")
            all_good = False

    if all_good:
        print("\n✨ All agents configured correctly!")
    else:
        print("\n🚫 Some agents have incorrect configurations.")

if __name__ == "__main__":
    verify_agent_configs()
