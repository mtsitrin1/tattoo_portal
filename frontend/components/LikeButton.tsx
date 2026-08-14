"use client";

import { useState } from "react";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function LikeButton({ tattooId }: { tattooId: string }) {
  const [liked, setLiked] = useState(false);

  async function like() {
    const sessionId = window.localStorage.getItem("tattoo-session-id") ?? crypto.randomUUID();
    window.localStorage.setItem("tattoo-session-id", sessionId);
    const form = new FormData();
    form.set("session_id", sessionId);
    const response = await fetch(`${apiUrl}/tattoos/${tattooId}/like`, { method: "POST", body: form });
    if (response.ok) setLiked(true);
  }

  return <button type="button" onClick={like} disabled={liked}>{liked ? "Liked" : "Like"}</button>;
}
