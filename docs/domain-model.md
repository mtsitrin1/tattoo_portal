# Initial domain model

The model supports progressive enrichment: ingestion may create a `Tattoo` with only an image and source, while later jobs add metadata, descriptions, and embeddings.

## Entities

### Tattoo

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | yes | Stable identifier |
| `image_url` | string | yes | Object-storage URL or key |
| `source_id` | UUID | yes | Origin of the image |
| `artist_id` | UUID | no | Attribution when known |
| `semantic_description` | text | no | Generated searchable description |
| `subject` | string | no | Taxonomy value |
| `style` | string | no | Taxonomy value |
| `placement` | string | no | Taxonomy value |
| `color` | string | no | Taxonomy value |
| `size` | string | no | Taxonomy value |
| `complexity` | string | no | Taxonomy value |
| `orientation` | string | no | Taxonomy value |
| `embedding` | vector | no | Generated from the semantic description |
| `created_at` / `updated_at` | timestamp | yes | Audit timestamps |

### Artist

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | yes | Stable identifier |
| `name` | string | yes | Display name |
| `profile_url` | string | no | External profile |
| `created_at` / `updated_at` | timestamp | yes | Audit timestamps |

### Source

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | yes | Stable identifier |
| `name` | string | yes | Source name |
| `url` | string | no | Source homepage or collection |
| `license_notes` | text | no | Provenance and usage notes |

### User

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | yes | Stable identifier |
| `email` | string | no | Optional until authentication is added |
| `created_at` | timestamp | yes | Account creation time |

### UserInteraction

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | yes | Stable identifier |
| `user_id` | UUID | no | Null for anonymous sessions |
| `session_id` | string | yes | Supports pre-auth interactions |
| `tattoo_id` | UUID | yes | Tattoo acted on |
| `event_type` | string | yes | Impression, view, like, skip, save, similar-click, search, or artist-click |
| `created_at` | timestamp | yes | Event time |

## Relationships

- A `Source` has many `Tattoo` records.
- An `Artist` has many `Tattoo` records; artist attribution is optional.
- A `User` has many `UserInteraction` records; anonymous interactions use `session_id`.
- A `Tattoo` has many `UserInteraction` records.
- Search results read `Tattoo.embedding` and optional taxonomy fields; embeddings and metadata are never required for initial ingestion.

## Design notes

- Taxonomy values are defined in versioned configuration, not duplicated in entity code.
- Provenance is retained through `Source` and `source_id` because image licensing must remain explicit.
- The event model is append-oriented so later ranking and personalization work can replay interaction history.
