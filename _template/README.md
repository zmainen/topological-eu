# Site Template

`page.html` is the canonical style template for topological.eu. Copy it to start any new page.

## Placeholders

Replace these HTML comments with actual content:

| Placeholder | Where | What |
|:--|:--|:--|
| `<!-- TITLE -->` | `<title>` tag | Page title (appears before " — Topological Transmission Theory") |
| `<!-- DESCRIPTION -->` | `<meta>` tag | One-line summary for search engines / link previews |
| `<!-- NAV -->` | Inside `.nav-links` | Navigation links (`<a>` elements, uppercase mono style applied automatically) |
| `<!-- CONTENT -->` | Between `</nav>` and `<footer>` | Page body — use `.content` (700px prose), `.content-wide` (1100px layouts), or custom |
| `<!-- FOOTER -->` | Right side of footer | Optional secondary footer text (left side is always "topological.eu") |

## Typography quick reference

| Role | Family | Usage |
|:--|:--|:--|
| Headings | Gloock | `h1`, `h2`, `h3` |
| Body text | Crimson Pro 300 | `p`, `.card-body`, prose |
| Epigraphs | Instrument Serif italic | `.subtitle`, `.epigraph` |
| Labels / UI | IBM Plex Mono 9-11px | `.label`, `.mono`, nav, badges, pills, buttons |

## Available components

- **`.content`** / **`.content-wide`** — centered containers (700px / 1100px)
- **`.card`** / **`.card-grid`** — dark cards on bg2, auto-fill grid
- **`.badge`** — uppercase mono pill with gold border
- **`.pill`** — small rounded link tag
- **`.callout`** — left-bordered highlight block
- **`.btn`** — bordered uppercase link (landing-page style)
- **`section`** — top-bordered content section

## Rules

- All CSS is inline in `<style>`. No external stylesheets, no frameworks.
- Only external dependency: Google Fonts (four families, preconnected).
- Dark palette only. Colors via CSS custom properties in `:root`.
- Responsive breakpoint at 700px.
