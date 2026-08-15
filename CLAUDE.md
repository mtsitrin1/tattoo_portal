# Tattoo Portal

## Product

Wedge product, not the full vision. One sentence: **help someone who has a
vague tattoo preference discover a design they'd actually get, faster than
Instagram/Pinterest/Google.**

The spec that produced this backlog originally mixed three products
(inspiration search, AI design tool, artist marketplace). We deliberately cut
that to a single loop for MVP-0:

```
Describe / Explore -> Discover -> Refine (like/save/similar) -> Save
```

Personalization, body visualization, and artist matching are follow-on
products layered on top once discovery works — not built in parallel with it.

Primary success metric: % of users who save at least one tattoo they'd
seriously consider getting. Don't optimize for registrations.

## Explicitly deferred (do not build until their epic is un-blocked)

AI tattoo generation, 3D/AR body visualization, automatic booking, a
sophisticated preference-learning model, full Instagram ingestion, automatic
artist recommendation, an agent that does everything. See the `needs-spec`
issues (Epics 4-8) for what's deferred and why each one is blocked.

## Architecture principles

- **The LLM parses intent, it doesn't pick results.** Query -> LLM ->
  structured filters (subject/style/placement/size) -> combine with vector
  search over embeddings -> rank. Never let the LLM choose what tattoos to
  show directly.
- **Offline/online split.** Scraping, dedup, vision-model metadata
  extraction, embedding generation all run as async/offline jobs. Online path
  (query parse + vector search + ranking) targets <500ms p95, excluding
  synchronous LLM query parsing.
- **Boring stack.** Postgres + pgvector, S3-compatible object storage,
  Docker Compose. No Kubernetes, no microservices, no Kafka, no agent
  framework — this is a PoC-stage product, not infra for scale that doesn't
  exist yet.
- **Data is progressively enriched, not mandatory.** A Tattoo record can
  exist with just an image + source; style/subject/placement/embedding get
  filled in by the pipeline over time. Don't require complete metadata to
  ingest.

## Marketplace model

- **Artist contact is a direct redirect, not a lead system.** "Contact
  artist" opens the artist's own `contact_url` (Instagram/site/booking link)
  in a new tab. There is no internal Lead entity, form, or notification
  pipeline — the click is recorded as an `artist_click` interaction event
  (#24) and that's the only record kept. (#49 and #51, which originally
  covered lead creation and lead notification, were closed as superseded.)
- **No monetization yet.** Artists aren't charged for anything in MVP-0/1.
  Sponsored placement (#52) and billing (#54) are deliberately deferred —
  revisit both together once there's an actual reason to charge artists.
- **Artist dashboard (#50) is blocked on artist auth**, which doesn't exist
  anywhere in this backlog yet. Don't scope the dashboard until there's a
  decision on how an artist gets access to their own profile.

## Data model (see issue #2)

Core entities: `Tattoo`, `Artist`, `Source`, `Tag`, `Embedding`, `User`,
`UserInteraction`, `SavedTattoo`, `Search`. A Tattoo has metadata (subjects,
styles, placement, color, size, complexity, orientation), a semantic
description, and an embedding generated from that description.

## Taxonomy (see issue #10, starter list until that lands)

Styles: fine-line, minimalist, traditional, neo-traditional, realism,
blackwork, geometric, ornamental, watercolor, japanese, tribal, abstract.
Don't treat this as final or academically complete — it's a starting point,
stored as versioned config once #10 lands, not hardcoded across the codebase.

## Dataset / licensing risk

Scraping tattoo images is technically easy; **redistributing/commercializing
scraped Instagram content is a separate legal question.** Don't build the
business model on the assumption that scraped images are ours to use.
Long-term sourcing should favor artist opt-in, licensed sources, or
user-submitted tattoos. This blocks issue #36 (Artist ingestion) explicitly.

## Working the backlog

- Issues live at https://github.com/mtsitrin1/tattoo_portal/issues, grouped
  into 9 milestones (one per epic).
- Labels: `ready` (well-defined, implement directly) vs `needs-spec` (the
  issue body names the open question — resolve/comment it before writing
  code) — plus `priority:P0/P1/P2`.
- Work `ready` issues in dependency order (each body lists "Depends on:
  #N"). Don't start a `needs-spec` issue without first proposing an answer
  to its open question and getting it confirmed.
