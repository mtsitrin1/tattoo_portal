"use client";

import { useState } from "react";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function SaveButton({ tattooId }: { tattooId: string }) {
  const [saved, setSaved] = useState(false);

  async function save() {
    const userId = window.localStorage.getItem("tattoo-user-id") ?? crypto.randomUUID();
    window.localStorage.setItem("tattoo-user-id", userId);
    const form = new FormData();
    form.set("user_id", userId);
    const response = await fetch(`${apiUrl}/tattoos/${tattooId}/save`, { method: "POST", body: form });
    if (response.ok) setSaved(true);
  }

  return <button type="button" onClick={save} disabled={saved}>{saved ? "Saved" : "Save"}</button>;
}
