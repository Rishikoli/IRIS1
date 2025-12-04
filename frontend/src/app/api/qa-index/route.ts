import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { company_symbol, company_data } = await request.json();

    // Forward request to backend Q&A indexing API
    const backendResponse = await fetch(`${process.env.BACKEND_URL || 'http://localhost:8000'}/api/v1/qa/index`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_symbol,
        company_data
      }),
    });

    if (!backendResponse.ok) {
      throw new Error(`Backend Q&A indexing failed: ${backendResponse.statusText}`);
    }

    const data = await backendResponse.json();

    return NextResponse.json({
      success: data.success,
      message: data.message,
      company_symbol: data.company_symbol,
      timestamp: data.timestamp
    });

  } catch (error: any) {
    console.error('Q&A Index API Error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Failed to index company data'
      },
      { status: 500 }
    );
  }
}
