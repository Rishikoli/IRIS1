import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { query, companySymbol, maxContext } = await request.json();

    // Forward request to backend Q&A API
    const backendResponse = await fetch(`${process.env.BACKEND_URL || 'http://localhost:8000'}/api/v1/qa/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        company_symbol: companySymbol,
        max_context: maxContext || 5
      }),
    });

    if (!backendResponse.ok) {
      throw new Error(`Backend Q&A API failed: ${backendResponse.statusText}`);
    }

    const data = await backendResponse.json();

    return NextResponse.json({
      success: data.success,
      answer: data.answer,
      confidence: data.confidence,
      contextUsed: data.context_used,
      sources: data.sources,
      companySymbol: data.company_symbol,
      timestamp: data.timestamp,
      query: query
    });

  } catch (error: any) {
    console.error('Q&A API Error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Failed to process question',
        answer: 'I apologize, but I encountered an error while processing your question. Please try again.',
        confidence: 'Low'
      },
      { status: 500 }
    );
  }
}
