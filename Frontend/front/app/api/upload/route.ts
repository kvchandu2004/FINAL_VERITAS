import { type NextRequest, NextResponse } from "next/server"

export async function POST(req: NextRequest) {
  // Simulate upload handling and processing delay
  await new Promise((r) => setTimeout(r, 800))
  return NextResponse.json({ ok: true })
}
