import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { symbol, formats = ['pdf', 'excel'], includeSummary = true } = body;

    if (!symbol) {
      return NextResponse.json(
        { error: 'Company symbol is required' },
        { status: 400 }
      );
    }

    console.log(`Generating reports for: ${symbol} with formats: ${formats.join(', ')}`);

    // Call backend report generation endpoint
    const response = await fetch(`${BACKEND_URL}/api/reports/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_symbol: symbol,
        export_formats: formats,
        include_summary: includeSummary
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('Backend error:', errorData);
      return NextResponse.json(
        { error: errorData.detail || 'Failed to generate reports' },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Reports generated successfully');

    return NextResponse.json(data);
  } catch (error: any) {
    console.error('Report generation error:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  return NextResponse.json(
    { message: 'Use POST method to generate reports' },
    { status: 405 }
  );
}
