"use client";

import { useEffect, useState } from "react";

type QualityStats = {
  total_tattoos: number;
  artist_percent: number;
  style_percent: number;
  placement_percent: number;
  description_percent: number;
  embedding_percent: number;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function QualityPage() {
  const [stats, setStats] = useState<QualityStats | null>(null);

  useEffect(() => {
    fetch(`${apiUrl}/quality`)
      .then((response) => response.json())
      .then(setStats);
  }, []);

  return (
    <main>
      <h1>Dataset quality</h1>
      {!stats ? (
        <p>Loading live dataset metrics…</p>
      ) : (
        <dl>
          <div><dt>Total tattoos</dt><dd>{stats.total_tattoos}</dd></div>
          <div><dt>With artist</dt><dd>{stats.artist_percent}%</dd></div>
          <div><dt>With style</dt><dd>{stats.style_percent}%</dd></div>
          <div><dt>With placement</dt><dd>{stats.placement_percent}%</dd></div>
          <div><dt>With description</dt><dd>{stats.description_percent}%</dd></div>
          <div><dt>With embedding</dt><dd>{stats.embedding_percent}%</dd></div>
        </dl>
      )}
    </main>
  );
}
