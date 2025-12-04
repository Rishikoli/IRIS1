import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { symbol } = body;

    if (!symbol) {
      return NextResponse.json(
        { error: 'Company symbol is required' },
        { status: 400 }
      );
    }

    console.log(`Starting forensic analysis for: ${symbol}`);

    // Call backend forensic analysis endpoint
    const response = await fetch(`${BACKEND_URL}/api/forensic/${encodeURIComponent(symbol)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('Backend error:', errorData);
      return NextResponse.json(
        { error: errorData.detail || 'Failed to analyze company' },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log('Analysis completed successfully');

    return NextResponse.json(data);
  } catch (error: any) {
    console.error('Forensic analysis error:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  return NextResponse.json(
    { message: 'Use POST method to analyze a company' },
    { status: 405 }
  );
}
