"use client";

import { useState } from "react";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function SkipButton({ tattooId }: { tattooId: string }) {
  const [skipped, setSkipped] = useState(false);

  async function skip() {
    const sessionId = window.localStorage.getItem("tattoo-session-id") ?? crypto.randomUUID();
    window.localStorage.setItem("tattoo-session-id", sessionId);
    const form = new FormData();
    form.set("session_id", sessionId);
    const response = await fetch(`${apiUrl}/tattoos/${tattooId}/skip`, { method: "POST", body: form });
    if (response.ok) setSkipped(true);
  }

  return <button type="button" onClick={skip} disabled={skipped}>{skipped ? "Skipped" : "Skip"}</button>;
}
