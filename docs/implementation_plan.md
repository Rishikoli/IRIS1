# Update Gemini Model Implementation Plan

## Goal Description
The user wants to switch the Gemini model to the one confirmed to be working (`gemini-2.5-flash`) across the entire backend.
Currently, various files might be using `gemini-pro`, `gemini-1.5-flash`, or other versions. We will standardize this to `gemini-2.5-flash`.

## Proposed Changes

### Backend - Agents
All of the following files instantiate `genai.GenerativeModel`. I will update the model name string to `"gemini-2.5-flash"`.

#### [MODIFY] [agent7_qa_rag.py](file:///home/aditya/Downloads/IRIS/backend/src/agents/agent7_qa_rag.py)
- Update `model_name` in `_initialize_gemini` and `generate_answer`.

#### [MODIFY] [agent8_market_sentiment.py](file:///home/aditya/Downloads/IRIS/backend/src/agents/agent8_market_sentiment.py)
- Update `model_name` in initialization.

#### [MODIFY] [agent5_reporting.py](file:///home/aditya/Downloads/IRIS/backend/src/agents/forensic/agent5_reporting.py)
- Update `model_name`.

#### [MODIFY] [agent9_network_analysis.py](file:///home/aditya/Downloads/IRIS/backend/src/agents/forensic/agent9_network_analysis.py)
- Update `model_name`.

#### [MODIFY] [agent10_auditor.py](file:///home/aditya/Downloads/IRIS/backend/src/agents/forensic/agent10_auditor.py)
- Update `model_name`.

#### [MODIFY] [agent12_cartographer.py](file:///home/aditya/Downloads/IRIS/backend/src/agents/forensic/agent12_cartographer.py)
- Update `model_name`.

## Verification Plan

### Automated Verification
1.  Run the previously created `verify_gemini.py` (it already uses `gemini-2.5-flash` in my manual test, but good to keep).
2.  I will create a new script `verify_agents_config.py` that imports these agents (if possible) or regex checks the files to ensure no other model names remain. (Regex is safer to avoid instantiation side effects).

### Manual Verification
- None needed beyond the script.
