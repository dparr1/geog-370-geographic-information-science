# Geographic Information Science (GEOG 370)

A working-draft textbook for **GEOG 370, Geographic Information Science**, at UNC-Chapel Hill,
written by David Parr from the course lectures. It is a [Quarto](https://quarto.org) book, set up
the same way as the [GEOG 215 textbook](https://github.com/dparr1/geog-215-spatial-data-science):
the same theme, sign-in, progress tracking, quizzes, questions, polls and admin page.

The book is published in two places from this repo:

| Site | Who can read it | Built by |
|---|---|---|
| **https://geog370.org** | Students on the class roster, after signing in with an emailed code. Their progress is recorded for the instructor. | Cloudflare Workers Builds (`wrangler.jsonc`, `scripts/cloudflare-build.sh`) |
| **https://daveparr.com/geographic-information-science/** | Anyone. No sign-in, and nothing is recorded. | GitHub Action (`.github/workflows/publish.yml`), which commits the rendered book into the `daveparr.com` repo once the `DAVEPARR_DEPLOY_KEY` secret is set |

Both rebuild automatically on every push to `main`.

## Site layout

Every page has a top menu: **Welcome**, **Syllabus**, **Course resources**, **About**, and
**Textbook**. In the sidebar these are two parts, *Course* and *Textbook*.

| Page | File | Sign-in on geog370.org |
|---|---|---|
| Welcome (home page) | `index.qmd` | Public |
| Syllabus | `syllabus.qmd` | Public |
| Course resources: staff and office hours, class meetings, modules, schedule, deadlines | `materials.qmd` | Students only |
| About the author | `about.qmd` | Public |
| Privacy policy (linked from the sign-in screen and page footer) | `privacy.qmd` | Public |
| Student services (linked from the syllabus) | `student-services.qmd` | Public |
| Textbook: preface, units, chapters, chapter quizzes, glossary | `preface.qmd`, `units/`, `chapters/`, `glossary.qmd` | Students only |

The public pages are listed in `PUBLIC_PAGES` in `assets/auth-gate.html`; keep that list in step with
the menu in `_quarto-site.yml`. The course pages are copied from the Fall 2026 GEOG 370 Syllabus
and Course Resources docs in Google Drive, so update them each semester.

daveparr.com/geographic-information-science/ and the PDF textbook get **only the textbook**: the
unit pages, chapters, and glossary, with the Preface as the first page, no top menu, and **no
quizzes** (those are only on geog370.org). Links to quiz pages on the unit pages and in the Preface
are wrapped in `::: {.content-hidden when-profile="textbook"}`. The `textbook` profile
(`_quarto-textbook.yml`) lists those chapters, and `_quarto-site.yml` lists the full site; one of the
two is always active, and `site` is the default. A new chapter goes in both files.

## What's in the book

The chapters are being written from the lecture slides. So far:

| Unit | Chapter | Quiz bank |
|:--|:--|:--|
| 1. Data Models and Projections (`units/unit-1.qmd`) | 1. What Is GIS? (`chapters/what-is-gis.qmd`, from lecture 02) | `quizzes/what-is-gis.json` |

To add more:

1. **A unit:** copy `_templates/unit.qmd` to `units/unit-<n>.qmd` and add it as a `part` in both
   `_quarto-site.yml` and `_quarto-textbook.yml` (each file has a commented example).
2. **A chapter:** copy `_templates/chapter.qmd` to `chapters/<chapter>.qmd` and list it under its unit
   in both files. Describe the unit in the Preface's *How this book is organized*, and link the chapter
   from the *Modules and the textbook* table on `materials.qmd`.
3. **Its quiz:** copy `_templates/chapter-quiz.qmd` to `chapters/<chapter>-quiz.qmd` (listed right
   after the chapter, in `_quarto-site.yml` only) and write `quizzes/<chapter>.json` from
   `_templates/quiz-bank.json`. Add the bank's `id` to `BOOK_ORDER` in `admin/index.html`. See
   `quizzes/README.md`.
4. **A unit quiz:** `_templates/unit-quiz.qmd` and a `quizzes/unit-<n>.json` that lists the unit's
   chapter banks.
5. **Key terms:** add them to `glossary.yml` (there's an example at the bottom). They get hover
   definitions in the chapters and appear on the Glossary page.

Readers get the same features as the GEOG 215 book:

- **Hover definitions for key terms** from `glossary.yml` (`filters/glossary/`).
- **Duolingo-style chapter quizzes** (`assets/quiz/`): multiple choice, true/false, fill in the
  blank, and put-the-tiles-in-order questions, with the instructor cartoon, sounds, and scores.
- **Self-check questions** inside chapters, from the
  [webexercises](https://psyteachr.github.io/webexercises/) package (`include/`), and **runnable R in
  the browser** with webR (`_extensions/coatless/webr`), if a chapter wants them. Both need R on the
  computer that renders the chapter; pages without R code don't.
- **Ask a question** on highlighted text, **polls and surveys**, and a reading settings menu ("Aa").

## How the site works

- **Rendering.** `_quarto.yml` defines the book. `freeze: auto` stores code results in `_freeze/`
  (commit it if chapters ever run code), so the GitHub Action and Cloudflare can render the book
  without R.
- **geog370.org profile.** `quarto render --profile geog370` (`_quarto-geog370.yml`) adds the sign-in
  gate (`assets/auth-gate.html`), questions and polls. Google Analytics is ready there but turned
  off until GEOG 370 has its own GA4 property.
- **Sign-in and progress.** The same [Supabase](https://supabase.com) project as geog215.org holds
  the roster and progress; every row is filed under course `geog370`. Students type their email and
  receive a one-time code or link, sent through Resend from `mail.geog215.org`. Only GEOG 370 roster
  and instructor emails can sign in.
- **Admin page.** https://geog370.org/admin/ (`admin/index.html`) is the same admin page as
  geog215.org/admin/; pick GEOG 370 in its Course picker. It is copied only into the geog370.org
  build, never the public copy.

See `supabase/README.md` for the one-time GEOG 370 setup in Supabase, and `quizzes/README.md` for
how to write a quiz bank.

## Repository layout

| Path | Contents |
|---|---|
| `index.qmd`, `syllabus.qmd`, `materials.qmd`, `about.qmd`, `privacy.qmd`, `student-services.qmd` | Course pages |
| `preface.qmd` | Textbook preface |
| `units/`, `chapters/` | Unit pages, and one `.qmd` per chapter plus its `-quiz.qmd` page (empty for now) |
| `_templates/` | Templates for a unit, chapter, chapter quiz, unit quiz and quiz bank, plus the PrettyPDF template (never rendered) |
| `quizzes/` | Chapter quiz question banks (JSON) and how to write them |
| `assets/quiz/` | The quiz engine (`quiz.js`, `quiz.css`), including the instructor cartoon |
| `assets/auth-gate.html` | The geog370.org sign-in screen and progress tracking |
| `admin/` | The instructor admin page |
| `supabase/` | How geog370.org uses the shared Supabase database |
| `images/` | Figures and screenshots |
| `glossary.yml`, `glossary.qmd` | Key terms and definitions, and the Glossary page built from them |
| `filters/glossary/` | Lua filter, script, and styles for the hover definitions |
| `include/` | webexercises CSS and JS |
| `_extensions/` | Quarto extensions (webR, PrettyPDF) |
| `scripts/cloudflare-build.sh` | Cloudflare build: installs Quarto and renders the gated book |

## Working on the book

```sh
quarto preview                      # full site without the sign-in gate, live reload
quarto render --profile geog370     # geog370.org version, with the sign-in gate
quarto preview --profile textbook   # daveparr.com version: textbook only, no quizzes (the
                                    # Action also copies preface.qmd over index.qmd first)
quarto render --to PrettyPDF-pdf --profile textbook   # the PDF textbook, no quizzes
```

The PDF needs a LaTeX install (TinyTeX: `quarto install tinytex`). To give it a full-page cover, add
`images/cover.jpg` and uncomment `assets/pdf-cover.tex` in `_quarto.yml`.

Changes go through a pull request into `main`; Cloudflare builds a preview of each branch, and
merging publishes both sites.

## History

**November 26, 2026: the site is set up.** The structure, styling, build and deploy setup, sign-in,
progress tracking, quizzes, questions, polls and admin page are copied from the GEOG 215 textbook,
with no units or chapters yet. The Welcome, Syllabus and Course resources pages are filled in from
the Fall 2026 GEOG 370 Syllabus and Course Resources docs.

**November 26, 2026: Chapter 1, *What Is GIS?*, is added** as the first chapter of Unit 1, written
from lecture 02, with its chapter quiz and the first glossary terms.
