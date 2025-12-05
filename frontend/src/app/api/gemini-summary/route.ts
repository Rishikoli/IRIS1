import { NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

export async function POST(request: Request) {
  try {
    const { analysisData, summaryType, companySymbol } = await request.json();

    // Initialize Gemini API
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || '');
    const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

    let prompt = '';

    if (summaryType === 'forensic') {
      // Forensic Analysis Prompt
      prompt = `You are a financial forensics expert analyzing ${companySymbol}. Based on the following forensic analysis data, provide a comprehensive 4-paragraph summary focusing on fraud detection and financial integrity:

**Analysis Data:**
- Altman Z-Score: ${analysisData.altman_z_score?.altman_z_score?.z_score || 'N/A'} (Classification: ${analysisData.altman_z_score?.altman_z_score?.classification || 'Unknown'}, Risk Level: ${analysisData.altman_z_score?.altman_z_score?.risk_level || 'Unknown'})
- Beneish M-Score: ${analysisData.beneish_m_score?.beneish_m_score?.m_score || 'N/A'} (Likely Manipulator: ${analysisData.beneish_m_score?.beneish_m_score?.is_likely_manipulator ? 'Yes' : 'No'})
- Benford's Law Compliance: ${analysisData.benford_analysis?.benford_analysis?.compliance_score || 'N/A'}% (Anomalous: ${analysisData.benford_analysis?.benford_analysis?.is_anomalous ? 'Yes' : 'No'})
- Anomalies Detected: ${analysisData.anomaly_detection?.anomalies_detected || 0}

**Required Structure:**
1. **Financial Health Assessment** - Interpret Altman Z-Score and bankruptcy risk
2. **Earnings Quality Analysis** - Evaluate Beneish M-Score and manipulation indicators
3. **Statistical Fraud Detection** - Analyze Benford's Law compliance
4. **Key Forensic Insights** - Summarize anomalies and overall verdict

Write in professional, analytical tone. Use HTML tags for emphasis: <strong> for key metrics, <span style="color: #22c55e; font-weight: 600;"> for positive findings, <span style="color: #ef4444; font-weight: 600;"> for red flags.`;

    } else if (summaryType === 'risk') {
      // Risk Assessment Prompt
      prompt = `You are an investment risk analyst evaluating ${companySymbol}. Based on the following risk assessment data, provide a comprehensive 4-paragraph summary focusing on investment decisions and portfolio management:

**Risk Data:**
- Overall Risk Score: ${analysisData.risk_assessment?.overall_risk_score || 'N/A'}/100
- Risk Level: ${analysisData.risk_assessment?.risk_level || 'MODERATE'}
- Confidence Score: ${analysisData.risk_assessment?.confidence_score || 'N/A'}%
- Category Scores: ${JSON.stringify(analysisData.risk_assessment?.category_scores || {})}
- Risk Factors: ${JSON.stringify(analysisData.risk_assessment?.risk_factors || [])}

**Required Structure:**
1. **Overall Risk Profile** - Interpret risk score (0-100) and classification
2. **Investment Recommendation** - Provide risk-adjusted investment advice based on score: <40 (conservative/low risk), 40-70 (moderate risk), >70 (high risk/aggressive only)
3. **Key Risk Drivers** - Identify top 3 risk categories and their implications
4. **Monitoring Frequency** - Recommend review schedule: >70 (WEEKLY), 40-70 (BI-WEEKLY), <40 (MONTHLY)

Write in professional, advisory tone. Use HTML tags: <strong> for key metrics, <span style="color: #22c55e; font-weight: 600;"> for low risk, <span style="color: #f59e0b; font-weight: 600;"> for moderate risk, <span style="color: #ef4444; font-weight: 600;"> for high risk.`;
    }

    // Generate content with Gemini
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const summary = response.text();

    return NextResponse.json({
      success: true,
      summary: summary,
      summaryType: summaryType,
      companySymbol: companySymbol,
      timestamp: new Date().toISOString()
    });

  } catch (error: any) {
    console.error('Gemini API Error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Failed to generate summary',
        fallback: true
      },
      { status: 500 }
    );
  }
}
