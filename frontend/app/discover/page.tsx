"use client";

import { useMemo, useRef, useState } from "react";
import styles from "./discover.module.css";
import { inter, plexMono } from "./fonts";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Screen = "idea" | "describe" | "explore" | "refine" | "visualize";

type Candidate = {
  id: string;
  image_url: string;
  style: string | null;
  subject: string | null;
  placement: string | null;
  semantic_description: string | null;
};

type Filters = { subject?: string | null; style?: string | null; placement?: string | null; size?: string | null };

type Detail = {
  id: string;
  metadata: {
    style: string | null;
    color: string | null;
    size: string | null;
    complexity: string | null;
    placement: string | null;
  };
};

type Decision = { item: Candidate; action: "keep" | "skip" };

type Facet = { label: string; hint: string; chosen: string; options: string[] };

const PROMPTS = ["something about my grandmother", "ocean but not literal", "a tiny first tattoo", "flowers, not girly"];
const TEMPLATES = ["Inner forearm", "Upper arm", "Back", "Ribs", "Ankle"];
const SIZE_BUCKETS: Array<[string, number]> = [["Coin-sized", 20], ["Palm-sized", 45], ["Half forearm", 70], ["Full forearm", 100]];
const FACET_FIELDS: Array<[keyof Detail["metadata"], string, string]> = [
  ["style", "Style", "how it's drawn"],
  ["color", "Colour", "ink used"],
  ["size", "Size", "on your arm"],
  ["complexity", "How busy", "detail level"],
];
// ponytail: 9 kept tattoos is a narrative threshold for the "reading your taste" copy,
// not a real model confidence score — the backend doesn't expose one.
const TASTE_TARGET = 9;

function getOrCreateId(key: string): string {
  const existing = window.localStorage.getItem(key);
  if (existing) return existing;
  const created = crypto.randomUUID();
  window.localStorage.setItem(key, created);
  return created;
}

function sizeLabelFor(size: number): string {
  return (SIZE_BUCKETS.find(([, max]) => size <= max) ?? SIZE_BUCKETS[SIZE_BUCKETS.length - 1])[0];
}

function mode(values: Array<string | null>): string | null {
  const counts = new Map<string, number>();
  for (const value of values) {
    if (value) counts.set(value, (counts.get(value) ?? 0) + 1);
  }
  let best: string | null = null;
  let bestCount = 0;
  for (const [value, count] of counts) {
    if (count > bestCount) {
      best = value;
      bestCount = count;
    }
  }
  return best;
}

function buildFacets(details: Detail[]): Facet[] {
  const facets: Facet[] = [];
  for (const [key, label, hint] of FACET_FIELDS) {
    const counts = new Map<string, number>();
    for (const detail of details) {
      const value = detail.metadata[key];
      if (value) counts.set(value, (counts.get(value) ?? 0) + 1);
    }
    if (counts.size === 0) continue;
    const sorted = [...counts.entries()].sort((a, b) => b[1] - a[1]);
    facets.push({ label, hint, chosen: sorted[0][0], options: sorted.slice(1, 4).map(([value]) => value) });
  }
  return facets;
}

function StepBar({ step }: { step: 1 | 2 | 3 | 4 }) {
  return (
    <div className={styles.stepBar}>
      <span className={styles.stepLabel}>STEP {step} OF 4</span>
      <div className={styles.stepTrack}>
        <div className={styles.stepFill} style={{ width: `${step * 25}%` }} />
      </div>
    </div>
  );
}

export default function DiscoverPage() {
  const [screen, setScreen] = useState<Screen>("idea");
  const historyRef = useRef<Screen[]>([]);
  const [describeText, setDescribeText] = useState("");
  const [filters, setFilters] = useState<Filters | null>(null);
  const [queue, setQueue] = useState<Candidate[]>([]);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [details, setDetails] = useState<Detail[]>([]);
  const [template, setTemplate] = useState(TEMPLATES[0]);
  const [size, setSize] = useState(45);
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const kept = useMemo(() => decisions.filter((d) => d.action === "keep").map((d) => d.item), [decisions]);
  const current = queue[decisions.length];
  const tastePct = Math.min(100, Math.round((kept.length / TASTE_TARGET) * 100));
  const facets = useMemo(() => buildFacets(details), [details]);

  function goTo(next: Screen) {
    historyRef.current.push(screen);
    setError(null);
    setScreen(next);
  }

  function goBack() {
    const previous = historyRef.current.pop();
    if (previous) setScreen(previous);
  }

  function startOver() {
    setScreen("idea");
    historyRef.current = [];
    setDescribeText("");
    setFilters(null);
    setQueue([]);
    setDecisions([]);
    setDetails([]);
    setSaved(false);
    setError(null);
  }

  async function startNoIdea() {
    setLoading(true);
    setError(null);
    try {
      const sessionId = getOrCreateId("tattoo-session-id");
      const response = await fetch(`${apiUrl}/tattoos?page=1&page_size=24&session_id=${sessionId}`);
      if (!response.ok) throw new Error();
      const data = await response.json();
      setQueue(data.items ?? []);
      setDecisions([]);
      setFilters(null);
      goTo("explore");
    } catch {
      setError("Could not load tattoos. Try again.");
    } finally {
      setLoading(false);
    }
  }

  async function submitDescribe() {
    if (!describeText.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/search/hybrid?q=${encodeURIComponent(describeText)}&limit=24`);
      if (!response.ok) throw new Error();
      const data = await response.json();
      setQueue(data.items ?? []);
      setDecisions([]);
      setFilters(data.filters ?? null);
      goTo("explore");
    } catch {
      setError("Could not parse that yet. Try describing it differently, or browse instead.");
    } finally {
      setLoading(false);
    }
  }

  async function decide(action: "keep" | "skip") {
    if (!current) return;
    const sessionId = getOrCreateId("tattoo-session-id");
    const form = new FormData();
    form.set("session_id", sessionId);
    try {
      const response = await fetch(`${apiUrl}/tattoos/${current.id}/${action}`, { method: "POST", body: form });
      if (!response.ok) throw new Error();
      setDecisions((prev) => [...prev, { item: current, action }]);
    } catch {
      setError("Could not save that — check your connection and try again.");
    }
  }

  function undo() {
    // ponytail: local-only undo. There's no unlike/unskip endpoint, so the prior
    // like/skip record stays server-side; re-deciding just records the new choice too.
    setDecisions((prev) => prev.slice(0, -1));
  }

  async function goToRefine() {
    setLoading(true);
    setError(null);
    try {
      const results = await Promise.all(
        kept.map((item) => fetch(`${apiUrl}/tattoos/${item.id}`).then((r) => r.json())),
      );
      setDetails(results);
    } catch {
      setDetails([]);
    } finally {
      setLoading(false);
      goTo("refine");
    }
  }

  async function showMoreLikeThese() {
    if (kept.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiUrl}/tattoos/${kept[0].id}/similar?limit=24`);
      if (!response.ok) throw new Error();
      const data = await response.json();
      const seen = new Set(queue.map((item) => item.id));
      const fresh = (data.items ?? []).filter((item: Candidate) => !seen.has(item.id));
      setQueue((prev) => [...prev, ...fresh]);
      goTo("explore");
    } catch {
      setError("Could not load more right now.");
    } finally {
      setLoading(false);
    }
  }

  async function saveDesign() {
    if (!kept[0]) return;
    setError(null);
    try {
      const userId = getOrCreateId("tattoo-user-id");
      const form = new FormData();
      form.set("user_id", userId);
      const response = await fetch(`${apiUrl}/tattoos/${kept[0].id}/save`, { method: "POST", body: form });
      if (!response.ok) throw new Error();
      setSaved(true);
    } catch {
      setError("Could not save — try again.");
    }
  }

  const topStyle = mode(kept.map((item) => item.style));

  return (
    <main className={`${styles.page} ${inter.variable} ${plexMono.variable}`} style={{ fontFamily: "var(--font-inter), system-ui, sans-serif" }}>
      <div className={styles.shell}>
        {error && <p className={styles.error}>{error}</p>}

        {screen === "idea" && (
          <>
            <h1 className={styles.heading}>
              I want a<span className={styles.accentDot}>…</span>
            </h1>
            <p className={styles.subcopy}>Start anywhere. You don&apos;t need the right words, a style name, or a plan.</p>
            <div className={styles.cardStack}>
              <button type="button" className={styles.optionCard} onClick={() => goTo("describe")}>
                <span className={styles.optionCardTitle}>I have an idea</span>
                <span className={styles.optionCardBody}>Describe it in your own words — even badly. No tattoo words needed.</span>
              </button>
              <button type="button" className={styles.optionCard} onClick={startNoIdea} disabled={loading}>
                <span className={styles.optionCardTitle}>I have no idea</span>
                <span className={styles.optionCardBody}>Look at tattoos. Keep the ones you like. We&apos;ll work it out from there.</span>
              </button>
            </div>
            <p className={styles.footNote}>Nothing is booked, bought, or permanent yet.</p>
          </>
        )}

        {screen === "describe" && (
          <>
            <button type="button" className={styles.backButton} onClick={goBack}>← Back</button>
            <StepBar step={1} />
            <h2 className={styles.heading}>In your own words</h2>
            <textarea
              className={styles.textarea}
              placeholder="a small moth on my forearm…"
              value={describeText}
              onChange={(event) => setDescribeText(event.target.value)}
            />
            <div>
              <div className={styles.label}>NOT SURE? TRY</div>
              <div className={styles.chipRow} style={{ marginTop: 10 }}>
                {PROMPTS.map((prompt) => (
                  <button key={prompt} type="button" className={styles.chip} onClick={() => setDescribeText(prompt)}>
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
            <button type="button" className={styles.btnPrimary} onClick={submitDescribe} disabled={loading || !describeText.trim()}>
              {loading ? "Looking…" : "Show me tattoos like this"}
            </button>
          </>
        )}

        {screen === "explore" && (
          <>
            <button type="button" className={styles.backButton} onClick={goBack}>← Back</button>
            <StepBar step={2} />
            {filters && Object.values(filters).some(Boolean) && (
              <div className={styles.chipRow}>
                {Object.entries(filters)
                  .filter(([, value]) => value)
                  .map(([key, value]) => (
                    <span key={key} className={styles.chipActive}>
                      <span className={styles.chipActiveKey}>{key}</span>
                      <span className={styles.chipActiveValue}>{value}</span>
                    </span>
                  ))}
              </div>
            )}

            {current ? (
              <div className={styles.exploreCard}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img className={styles.exploreImage} src={current.image_url} alt={current.semantic_description ?? "Tattoo design"} />
                <div className={styles.exploreMeta}>
                  <div className={styles.exploreTitleRow}>
                    <span className={styles.exploreTitle}>{current.semantic_description ?? current.subject ?? "Tattoo design"}</span>
                    {current.placement && <span className={styles.exploreSub}>{current.placement}</span>}
                  </div>
                  <div className={styles.chipRow}>
                    {current.style && <span className={styles.chip}>{current.style}</span>}
                    {current.subject && <span className={styles.chip}>{current.subject}</span>}
                  </div>
                </div>
              </div>
            ) : (
              <div className={styles.emptyState}>
                {kept.length > 0 ? (
                  <>
                    <p>That&apos;s everything for now.</p>
                    <button type="button" className={styles.btnPrimary} onClick={goToRefine} disabled={loading}>
                      See what you kept ({kept.length})
                    </button>
                  </>
                ) : (
                  <>
                    <p>No matches yet.</p>
                    <button type="button" className={styles.btnPrimary} onClick={() => goTo("describe")}>
                      Try describing it differently
                    </button>
                  </>
                )}
              </div>
            )}

            {current && (
              <div className={styles.actionRow}>
                <button type="button" className={styles.actionSecondary} onClick={() => decide("skip")}>Not for me</button>
                <button type="button" className={styles.actionUndo} onClick={undo} disabled={decisions.length === 0} aria-label="Undo last choice">↺</button>
                <button type="button" className={styles.actionPrimary} onClick={() => decide("keep")}>Keep</button>
              </div>
            )}

            <div className={styles.tasteBlock}>
              <div className={styles.tasteRow}>
                <span>Reading your taste</span>
                <span className={styles.chipActiveValue}>{tastePct}%</span>
              </div>
              <div className={styles.tasteTrack}>
                <div className={styles.tasteFill} style={{ width: `${tastePct}%` }} />
              </div>
              <p className={styles.footNote} style={{ textAlign: "left" }}>
                {kept.length === 0
                  ? "Keep a few you like — we'll start noticing patterns."
                  : topStyle
                    ? `You're leaning ${topStyle}. Keep going and we'll show you the pattern.`
                    : "Keep going and we'll show you the pattern."}
              </p>
            </div>

            {kept.length > 0 && (
              <button type="button" className={styles.keptLink} onClick={goToRefine} disabled={loading}>
                See what you kept ({kept.length})
              </button>
            )}
          </>
        )}

        {screen === "refine" && (
          <>
            <button type="button" className={styles.backButton} onClick={goBack}>← Back</button>
            <StepBar step={3} />
            <h2 className={styles.heading}>What you kept</h2>
            <p className={styles.subcopy}>
              From {kept.length} you kept, these are the things they have in common.
            </p>
            <div className={styles.thumbRow}>
              {kept.slice(0, 3).map((item) => (
                // eslint-disable-next-line @next/next/no-img-element
                <img key={item.id} className={styles.thumb} src={item.image_url} alt={item.semantic_description ?? "Kept tattoo"} />
              ))}
              {kept.length > 3 && <div className={styles.thumbMore}>+{kept.length - 3}</div>}
            </div>
            {facets.length > 0 && (
              <div className={styles.facetList}>
                {facets.map((facet) => (
                  <div key={facet.label} className={styles.facet}>
                    <div className={styles.facetHeader}>
                      <span className={styles.facetLabel}>{facet.label}</span>
                      <span className={styles.facetHint}>{facet.hint}</span>
                    </div>
                    <div className={styles.chipRow}>
                      <span className={styles.chipActive}>
                        <span className={styles.chipActiveValue}>{facet.chosen}</span>
                      </span>
                      {facet.options.map((option) => (
                        <span key={option} className={styles.chip}>{option}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
            <button type="button" className={styles.btnPrimary} onClick={() => goTo("visualize")}>See it on my body</button>
            <button type="button" className={styles.btnGhost} onClick={showMoreLikeThese} disabled={loading}>
              Show more like these first
            </button>
          </>
        )}

        {screen === "visualize" && (
          <>
            <button type="button" className={styles.backButton} onClick={goBack}>← Back</button>
            <StepBar step={4} />
            <div>
              <h2 className={styles.heading}>On your {template.toLowerCase()}</h2>
              <span className={styles.footNote}>a model, not your photo</span>
            </div>
            <div className={styles.previewBox}>
              <div className={styles.previewSilhouette} />
              {kept[0] && (
                // eslint-disable-next-line @next/next/no-img-element
                <img className={styles.previewDesign} src={kept[0].image_url} alt={kept[0].semantic_description ?? "Your design"} />
              )}
              <span className={styles.previewCaption}>PREVIEW ONLY · DRAG &amp; RESIZE NOT AVAILABLE YET</span>
            </div>
            <div className={styles.templateRow}>
              {TEMPLATES.map((option) => (
                <button
                  key={option}
                  type="button"
                  className={option === template ? styles.templateChipActive : styles.templateChip}
                  onClick={() => setTemplate(option)}
                >
                  {option}
                </button>
              ))}
            </div>
            <div className={styles.sizeRow}>
              <div className={styles.sizeLabelRow}>
                <span>Size</span>
                <span className={styles.chipActiveValue}>{sizeLabelFor(size)}</span>
              </div>
              <input
                type="range"
                className={styles.sizeSlider}
                min={10}
                max={100}
                step={5}
                value={size}
                onChange={(event) => setSize(Number(event.target.value))}
                aria-label="Design size"
              />
            </div>
            {saved ? (
              <div className={styles.savedBlock}>
                <p className={styles.subcopy}>Saved to your ideas. Still nothing booked.</p>
                <button type="button" className={styles.btnGhost} onClick={startOver}>Start a new idea →</button>
              </div>
            ) : (
              <>
                <button type="button" className={styles.btnPrimary} onClick={saveDesign} disabled={!kept[0]}>Save this design</button>
                <p className={styles.footNote}>Saves to your ideas. Still nothing booked.</p>
              </>
            )}
          </>
        )}
      </div>
    </main>
  );
}
