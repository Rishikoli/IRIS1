import { NextResponse } from 'next/server'

export async function POST(
  request: Request,
  { params }: { params: Promise<{ symbol: string }> }
) {
  try {
    const { symbol } = await params

    if (!symbol) {
      return NextResponse.json(
        { success: false, error: 'Company symbol is required' },
        { status: 400 }
      )
    }

    // Proxy request to backend API
    const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/api/forensic/${symbol}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        {
          success: false,
          error: errorData.detail || `Backend API error: ${response.status}`,
          company_id: symbol,
          analysis_timestamp: new Date().toISOString()
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error in forensic analysis:', error)
    const resolvedParams = await params
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to run forensic analysis',
        company_id: resolvedParams.symbol,
        analysis_timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}
