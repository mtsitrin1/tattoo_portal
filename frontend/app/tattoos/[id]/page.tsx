"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { LikeButton } from "../../../components/LikeButton";

type Detail = {
  image_url: string;
  artist: { name: string; profile_url: string | null } | null;
  source: { name: string; url: string | null } | null;
  metadata: Record<string, string | null>;
};

type Similar = { id: string; image_url: string; semantic_description: string | null };

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function TattooDetailPage() {
  const params = useParams<{ id: string }>();
  const [detail, setDetail] = useState<Detail | null>(null);
  const [similar, setSimilar] = useState<Similar[]>([]);

  useEffect(() => {
    fetch(`${apiUrl}/tattoos/${params.id}`)
      .then((response) => response.json())
      .then(setDetail);
    fetch(`${apiUrl}/tattoos/${params.id}/similar`)
      .then((response) => response.json())
      .then((result) => setSimilar(result.items ?? []));
  }, [params.id]);

  if (!detail) return <main><p>Loading tattoo…</p></main>;

  return (
    <main>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={detail.image_url} alt={detail.metadata.semantic_description ?? "Tattoo design"} />
      <h1>{detail.metadata.semantic_description ?? "Tattoo design"}</h1>
      <LikeButton tattooId={params.id} />
      {detail.artist && <p>Artist: {detail.artist.name}</p>}
      {detail.source?.url && <p><a href={detail.source.url}>View source: {detail.source.name}</a></p>}
      <dl>
        {Object.entries(detail.metadata).filter(([, value]) => value).map(([key, value]) => (
          <div key={key}><dt>{key}</dt><dd>{value}</dd></div>
        ))}
      </dl>
      <section aria-label="More like this">
        <h2>More like this</h2>
        {similar.map((item) => (
          <a key={item.id} href={`/tattoos/${item.id}`}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={item.image_url} alt={item.semantic_description ?? "Similar tattoo"} />
          </a>
        ))}
      </section>
    </main>
  );
}
