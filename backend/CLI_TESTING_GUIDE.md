# IRIS CLI and API Testing Guide

## Overview

Two powerful command-line tools for testing and validating IRIS forensic analysis agents without a frontend:

1. **`iris_cli.py`** - Interactive CLI for running forensic analyses
2. **`test_iris_api.py`** - Comprehensive API endpoint testing suite

## Prerequisites

```bash
cd /home/aditya/I.R.I.S./backend
source iris_venv/bin/activate

# Optional: Set custom API port (default is 8000)
export API_PORT=8000
```

## 1. IRIS CLI Tool (`iris_cli.py`)

### Available Commands

#### Ingest Company Data
```bash
python iris_cli.py ingest RELIANCE.BO
```
Fetches and stores financial statements from data sources.

#### Run Forensic Analysis
```bash
python iris_cli.py analyze RELIANCE.BO
```
Performs comprehensive forensic analysis including:
- Vertical analysis (common-size statements)
- Horizontal analysis (trend analysis)
- Financial ratios
- Benford's Law analysis
- Anomaly detection

#### Calculate Risk Score
```bash
python iris_cli.py risk-score RELIANCE.BO
```
Generates risk assessment and scoring.

#### Comprehensive Analysis (All Agents)
```bash
python iris_cli.py comprehensive RELIANCE.BO
```
Runs all three agents in sequence:
1. Data Ingestion
2. Forensic Analysis
3. Risk Scoring

#### Real-time Analysis with Progress
```bash
python iris_cli.py realtime RELIANCE.BO
```
Streams analysis progress in real-time.

#### List Companies in Database
```bash
python iris_cli.py list-companies
```
Shows all companies currently in the database.

### Example Output

```
🚀 IRIS Forensic Analysis CLI Tool
==================================================
🔍 Running forensic analysis for RELIANCE.BO...
✅ Forensic analysis completed!
📊 Key Metrics:
  • Risk Score: 45.2
  • Financial Health: B+
  • Anomalies Detected: 2
    - REVENUE_DECLINE: Revenue declined by 12.3%
    - RECEIVABLES_BUILDUP: Accounts receivable is 28.5% of revenue
  • Analysis Types: vertical_analysis, horizontal_analysis, financial_ratios, benford_analysis, anomaly_detection
```

## 2. API Testing Suite (`test_iris_api.py`)

### Test All Endpoints for a Company

```bash
python test_iris_api.py --company RELIANCE.BO --test-all
```

This runs comprehensive tests including:
- ✅ Health check
- ✅ Companies list endpoint
- ✅ Data ingestion
- ✅ Forensic analysis
- ✅ Risk scoring
- ✅ Real-time analysis
- ✅ Error handling

### Test Specific Endpoint

```bash
# Test ingestion endpoint
python test_iris_api.py --endpoint /api/ingestion/RELIANCE.BO

# Test forensic analysis endpoint
python test_iris_api.py --endpoint /api/forensic/RELIANCE.BO

# Test risk scoring endpoint
python test_iris_api.py --endpoint /api/risk-score/RELIANCE.BO
```

### Test Basic Functionality

```bash
python test_iris_api.py --company RELIANCE.BO
```
Runs basic health checks and data ingestion tests.

### Example Output

```
🧪 Running comprehensive API test suite for RELIANCE.BO
======================================================================

[✅ PASS] Health Check (0.12s)
[✅ PASS] Companies List (0.23s)

📥 Testing data ingestion for RELIANCE.BO...
[✅ PASS] Data Ingestion (2.45s)
[✅ PASS] Statement Structure (0.01s)

🔍 Testing forensic analysis for RELIANCE.BO...
[✅ PASS] Forensic Analysis (5.67s)
[✅ PASS] Analysis Components (0.02s)
[✅ PASS] Anomaly Detection (0.01s)

⚡ Testing risk scoring for RELIANCE.BO...
[✅ PASS] Risk Scoring (1.23s)
[✅ PASS] Risk Score Structure (0.01s)
[✅ PASS] Score Range (0.01s)

📊 TEST SUMMARY
==================================================
Total Tests: 10
Passed: 10
Failed: 0
Success Rate: 100.0%
Total Time: 9.76s

🎉 ALL TESTS PASSED! IRIS API is fully functional.
```

## Configuration

### Environment Variables

Both tools read configuration from environment variables:

```bash
# API server port (default: 8000)
export API_PORT=8000

# For the API server itself (if running locally)
export FMP_API_KEY="your_fmp_key"
export GEMINI_API_KEY="your_gemini_key"
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"
```

### Custom API Server

If your API server is running on a different host/port:

```bash
# For CLI (modify base_url in code or use API_PORT env var)
export API_PORT=8001

# For API tests (same)
export API_PORT=8001
```

## Testing Workflow

### 1. Start API Server

```bash
cd /home/aditya/I.R.I.S./backend
source iris_venv/bin/activate
python -m src.api.main
```

### 2. Run Tests in Another Terminal

```bash
cd /home/aditya/I.R.I.S./backend
source iris_venv/bin/activate

# Quick test
python iris_cli.py analyze RELIANCE.BO

# Comprehensive validation
python test_iris_api.py --company RELIANCE.BO --test-all
```

## Troubleshooting

### Connection Refused

```
❌ Request failed: HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded
```

**Solution**: Ensure the API server is running on the correct port.

### Import Errors

```
ImportError: cannot import name 'Config'
```

**Solution**: Both tools now use environment variables instead of Config. Ensure you're using the latest versions.

### Timeout Errors

```
❌ Request failed: ReadTimeout
```

**Solution**: Increase timeout in the code or ensure the API server is responding.

## Advanced Usage

### Testing Multiple Companies

```bash
#!/bin/bash
companies=("RELIANCE.BO" "TCS.BO" "INFY.BO" "HDFCBANK.BO")

for company in "${companies[@]}"; do
    echo "Testing $company..."
    python iris_cli.py comprehensive "$company"
    echo "---"
done
```

### Automated Testing in CI/CD

```bash
# Run all tests and exit with proper code
python test_iris_api.py --company RELIANCE.BO --test-all
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✅ All tests passed"
else
    echo "❌ Tests failed"
    exit 1
fi
```

## Benefits

### ✅ Backend-First Development
- Test all core functionality before frontend development
- Validate business logic independently
- Catch bugs early in the development cycle

### ✅ API Documentation
- Tools serve as living documentation
- Examples of how to use each endpoint
- Clear expected inputs and outputs

### ✅ Debugging Aid
- Easy way to test individual components
- Isolate issues to specific agents
- Reproduce bugs with specific test cases

### ✅ Demo Tool
- Perfect for showcasing IRIS capabilities
- No frontend required for demonstrations
- Quick proof-of-concept validation

### ✅ CI/CD Integration
- Ready for automated testing pipelines
- Exit codes for pass/fail detection
- Detailed test reports

## Next Steps

1. **Start your API server** (if not already running)
2. **Test basic functionality**: `python iris_cli.py analyze RELIANCE.BO`
3. **Run comprehensive tests**: `python test_iris_api.py --company RELIANCE.BO --test-all`
4. **Integrate into your workflow**: Use these tools during development

## Support

For issues or questions:
- Check that the API server is running
- Verify environment variables are set correctly
- Ensure you're in the activated virtual environment (`iris_venv`)
- Check API server logs for errors

---

**🎉 You now have professional-grade CLI and testing tools for IRIS!**
