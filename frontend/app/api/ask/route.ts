import { NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8001";

export async function POST(request: Request) {
  const body = await request.json();

  const response = await fetch(`${API_BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const text = await response.text();

  return new NextResponse(text, {
    status: response.status,
    headers: { "Content-Type": response.headers.get("Content-Type") ?? "text/plain" },
  });
}
