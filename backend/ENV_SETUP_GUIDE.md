# Environment Configuration Guide

## ⚠️ IMPORTANT: Fix Your .env File

Your `SUPABASE_URL` is currently set to a PostgreSQL connection string, but it should be the Supabase project URL.

### ❌ WRONG (Current):
```bash
SUPABASE_URL=postgresql://postgres.rsyyqooksgsdbnzjiusn:iris_password@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
```

### ✅ CORRECT (What it should be):

**Option 1: Use Direct Database URL (Recommended for IPv4 networks)**
```bash
SUPABASE_URL=https://rsyyqooksgsdbnzjiusn.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
DATABASE_URL=postgresql://postgres.rsyyqooksgsdbnzjiusn:iris_pd@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
```

**Option 2: Use Password-based Configuration**
```bash
SUPABASE_URL=https://rsyyqooksgsdbnzjiusn.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_DB_PASSWORD=iris_password
```

## Required Environment Variables

### 1. Supabase Configuration
- **SUPABASE_URL**: Your Supabase project URL (format: `https://PROJECT_REF.supabase.co`)
  - Find it in: Supabase Dashboard > Settings > API > Project URL
  
- **SUPABASE_KEY**: Your Supabase anon/public API key
  - Find it in: Supabase Dashboard > Settings > API > Project API keys > anon public
  
- **SUPABASE_DB_PASSWORD**: Your database password (NOT the API key)
  - Find it in: Supabase Dashboard > Settings > Database > Database password
  - This is the password you set when creating the project

### 2. API Keys
```bash
FMP_API_KEY=your_financial_modeling_prep_api_key
GEMINI_API_KEY=your_google_gemini_api_key
NSE_API_KEY=your_nse_api_key (optional)
BSE_API_KEY=your_bse_api_key (optional)
```

### 3. Other Configuration
```bash
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## How to Fix

1. Open your `.env` file:
   ```bash
   nano /home/aditya/I.R.I.S./backend/.env
   ```

2. Update the `SUPABASE_URL` line to:
   ```bash
   SUPABASE_URL=https://rsyyqooksgsdbnzjiusn.supabase.co
   ```

3. Ensure `SUPABASE_DB_PASSWORD` is set to your database password:
   ```bash
   SUPABASE_DB_PASSWORD=iris_password
   ```

4. Save and restart the application:
   ```bash
   python -m src.api.main
   ```

## Testing Your Configuration

Run the test script to verify your configuration:
```bash
python test_config.py
```

You should see:
- ✓ Supabase URL: https://rsyyqooksgsdbnzjiusn.supabase.co
- ✓ DB Password Set: Yes
- ✓ Database URL: postgresql://postgres:***@db.rsyyqooksgsdbnzjiusn.supabase.co:5432/postgres
