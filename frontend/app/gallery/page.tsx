"use client";

import { useEffect, useState } from "react";
import { LikeButton } from "../../components/LikeButton";

type Tattoo = {
  id: string;
  image_url: string;
  style: string | null;
  subject: string | null;
};

type GalleryResponse = {
  items: Tattoo[];
  page: number;
  page_size: number;
  total: number;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function GalleryPage() {
  const [gallery, setGallery] = useState<GalleryResponse | null>(null);

  useEffect(() => {
    fetch(`${apiUrl}/tattoos?page=1&page_size=24`)
      .then((response) => response.json())
      .then(setGallery);
  }, []);

  return (
    <main>
      <h1>Tattoo gallery</h1>
      {!gallery ? (
        <p>Loading tattoos…</p>
      ) : (
        <>
          <p>{gallery.total} tattoos</p>
          <section aria-label="Tattoo designs">
            {gallery.items.map((tattoo) => (
              <article key={tattoo.id}>
                {/* S3/MinIO URLs become browser-ready in the storage integration issue. */}
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={tattoo.image_url} alt={tattoo.subject ?? "Tattoo design"} />
                <p>{[tattoo.style, tattoo.subject].filter(Boolean).join(" · ")}</p>
                <LikeButton tattooId={tattoo.id} />
              </article>
            ))}
          </section>
        </>
      )}
    </main>
  );
}
