import { NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

export async function POST(request: Request) {
  try {
    const { analysisData, companySymbol } = await request.json();

    // Initialize Gemini API
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || '');
    const model = genAI.getGenerativeModel({ model: "gemini-2.0-flash" });

    // Prepare regulatory analysis prompt
    const prompt = `You are a senior SEBI regulatory compliance officer analyzing ${companySymbol} for potential regulatory actions and compliance monitoring requirements.

**Analysis Data:**
- Overall Risk Score: ${analysisData.risk_assessment?.overall_risk_score || 'N/A'}/100
- Risk Level: ${analysisData.risk_assessment?.risk_level || 'MODERATE'}
- Compliance Score: ${analysisData.compliance_assessment?.overall_compliance_score || 'N/A'}%
- Compliance Status: ${analysisData.compliance_assessment?.compliance_status || 'UNKNOWN'}
- Anomalies Detected: ${analysisData.anomaly_detection?.anomalies_detected || 0}
- Altman Z-Score: ${analysisData.altman_z_score?.altman_z_score?.z_score || 'N/A'}
- Beneish M-Score: ${analysisData.beneish_m_score?.beneish_m_score?.m_score || 'N/A'}
- Violations Found: ${analysisData.compliance_assessment?.violations?.length || 0}

**Regulatory Framework Context:**
- SEBI (Securities and Exchange Board of India) regulations
- Companies Act 2013 compliance
- Ind AS (Indian Accounting Standards)
- Corporate governance requirements

**Required Structure:**
1. **Immediate Enforcement Actions** - Assess if urgent regulatory intervention is needed
2. **Monitoring Requirements** - Specify surveillance frequency and focus areas
3. **Specific Compliance Checks** - Identify critical areas requiring verification in next quarter
4. **Early Warning Indicators** - Define triggers for enhanced scrutiny

**Guidelines:**
- Be conservative and prioritize investor protection
- Focus on material irregularities and systemic risks
- Recommend specific timeframes (Q1, Q2, Q3, Q4)
- Use formal regulatory language
- Provide clear escalation paths if risks increase

**Response Format:**
- Use bullet points for clarity
- Bold key terms and timeframes
- Include specific SEBI regulation references where applicable
- End with compliance officer contact recommendation if high risk`;

    // Generate content with Gemini
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const recommendations = response.text();

    return NextResponse.json({
      success: true,
      recommendations: recommendations,
      recommendationType: 'regulatory',
      companySymbol: companySymbol,
      timestamp: new Date().toISOString(),
      riskLevel: analysisData.risk_assessment?.risk_level || 'MODERATE',
      complianceScore: analysisData.compliance_assessment?.overall_compliance_score || 0
    });

  } catch (error: any) {
    console.error('Gemini Regulatory API Error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Failed to generate regulatory recommendations',
        fallback: true,
        defaultRecommendations: [
          "• No immediate enforcement action required.",
          "• Maintain quarterly forensic monitoring.",
          "• Cross-verify debt covenants in Q2 for early distress signals."
        ]
      },
      { status: 500 }
    );
  }
}
