# Environment Setup for Gemini AI Integration

## Required Environment Variable

Add the following to your `.env.local` file in the frontend directory:

```bash
# Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here
```

## How to Get Your Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Add it to `.env.local` file

## Model Used

- **Model**: `gemini-2.0-flash-exp`
- **Purpose**: Real-time AI summary generation
- **Features**: 
  - Forensic analysis summaries
  - Risk intelligence summaries
  - Context-aware recommendations

## API Endpoint

The integration uses:
- **Route**: `/api/gemini-summary`
- **Method**: POST
- **Payload**: `{ analysisData, summaryType, companySymbol }`

## Testing

After adding the API key:
1. Restart the development server
2. Analyze a company
3. Navigate to Forensic or Risk tabs
4. AI summaries will generate automatically

