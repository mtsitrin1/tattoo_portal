"use client";

import { FormEvent, useMemo, useState } from "react";
import { LikeButton } from "../../components/LikeButton";
import { SkipButton } from "../../components/SkipButton";

type SearchItem = {
  id: string;
  image_url: string;
  style: string | null;
  subject: string | null;
  placement: string | null;
  semantic_description: string | null;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [items, setItems] = useState<SearchItem[]>([]);
  const [searched, setSearched] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const response = await fetch(`${apiUrl}/search?q=${encodeURIComponent(query)}`);
    const result = await response.json();
    setItems(result.items ?? []);
    setSearched(true);
  }

  const styles = useMemo(
    () => [...new Set(items.map((item) => item.style).filter(Boolean))],
    [items],
  );
  const subjects = useMemo(
    () => [...new Set(items.map((item) => item.subject).filter(Boolean))],
    [items],
  );

  return (
    <main>
      <h1>Discover tattoos</h1>
      <form onSubmit={submit}>
        <label htmlFor="query">What are you looking for?</label>
        <input
          id="query"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="A small blackwork bird on my forearm"
        />
        <button type="submit">Search</button>
      </form>
      {searched && (
        <>
          <aside aria-label="Search facets">
            <h2>Filters</h2>
            <p>Styles: {styles.length ? styles.join(", ") : "None"}</p>
            <p>Subjects: {subjects.length ? subjects.join(", ") : "None"}</p>
          </aside>
          <section aria-label="Search results">
            {items.length ? (
              items.map((item) => (
                <article key={item.id}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={item.image_url} alt={item.semantic_description ?? "Tattoo design"} />
                  <p>{[item.style, item.subject, item.placement].filter(Boolean).join(" · ")}</p>
                  <LikeButton tattooId={item.id} />
                  <SkipButton tattooId={item.id} />
                </article>
              ))
            ) : (
              <p>No tattoos found.</p>
            )}
          </section>
        </>
      )}
    </main>
  );
}
