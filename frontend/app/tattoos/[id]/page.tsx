"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

type Detail = {
  image_url: string;
  artist: { name: string; profile_url: string | null } | null;
  source: { name: string; url: string | null } | null;
  metadata: Record<string, string | null>;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function TattooDetailPage() {
  const params = useParams<{ id: string }>();
  const [detail, setDetail] = useState<Detail | null>(null);

  useEffect(() => {
    fetch(`${apiUrl}/tattoos/${params.id}`)
      .then((response) => response.json())
      .then(setDetail);
  }, [params.id]);

  if (!detail) return <main><p>Loading tattoo…</p></main>;

  return (
    <main>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={detail.image_url} alt={detail.metadata.semantic_description ?? "Tattoo design"} />
      <h1>{detail.metadata.semantic_description ?? "Tattoo design"}</h1>
      {detail.artist && <p>Artist: {detail.artist.name}</p>}
      {detail.source?.url && <p><a href={detail.source.url}>View source: {detail.source.name}</a></p>}
      <dl>
        {Object.entries(detail.metadata).filter(([, value]) => value).map(([key, value]) => (
          <div key={key}><dt>{key}</dt><dd>{value}</dd></div>
        ))}
      </dl>
    </main>
  );
}
