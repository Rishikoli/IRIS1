import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Proxy request to backend API
    const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/api/companies`)

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching companies:', error)
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to fetch companies',
        companies: []
      },
      { status: 500 }
    )
  }
}
