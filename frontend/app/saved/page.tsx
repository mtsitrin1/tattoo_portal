"use client";

import { useEffect, useState } from "react";

type SavedItem = { id: string; image_url: string; style: string | null; subject: string | null };
const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function SavedPage() {
  const [items, setItems] = useState<SavedItem[]>([]);

  useEffect(() => {
    const userId = window.localStorage.getItem("tattoo-user-id");
    if (!userId) return;
    fetch(`${apiUrl}/saved/${userId}`).then((response) => response.json()).then((result) => setItems(result.items ?? []));
  }, []);

  return (
    <main>
      <h1>Saved tattoos</h1>
      <section aria-label="Saved tattoo collection">
        {items.map((item) => (
          <a key={item.id} href={`/tattoos/${item.id}`}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={item.image_url} alt={[item.style, item.subject].filter(Boolean).join(" ") || "Saved tattoo"} />
          </a>
        ))}
      </section>
    </main>
  );
}
