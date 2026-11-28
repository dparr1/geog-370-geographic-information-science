# Chapter quiz question banks

Each chapter has a quiz page right after it (`chapters/<chapter>-quiz.qmd`), and each quiz page
draws its questions from a bank in this folder (`quizzes/<chapter>.json`). The quiz itself is
`assets/quiz/quiz.js` and `assets/quiz/quiz.css`.

A session asks `perSession` questions (default 10), chosen at random. Students answer one at a time. Any they miss come
back at the end, again and again, until every question is right. Each new quiz is a fresh random set.
On a right answer, a cartoon of the instructor pops up with a speech bubble ("Good job!", "Way to go!",
...), and again on the end-of-quiz screen with a message that depends on how it went. On a wrong
answer it frowns and says something kind ("Oops! So close."). The drawing (`coachSvg`, with the two
faces in `COACH_FACES`) and the phrases (`CHEERS`, `CONSOLES`, `FINISH_CHEERS`) are near the top of
`quiz.js`.

Right answers play a short happy chime, wrong answers a buzzer, and finishing a quiz a little
fanfare. They are made in the browser with the Web Audio API (`SOUNDS` in `quiz.js`), so there are
no sound files. A speaker button next to the progress bar turns sound on and off, and the browser
remembers the choice.

Each quiz keeps score. Every answer, re-asks included, is +100 if right and -100 if wrong, and a right
answer earns a streak bonus of 10 for each right answer in a row just before it, so a run of right
answers scores 100, 110, 120, 130, ... A wrong answer resets the streak, and every new quiz starts from
0. The score and streak sit next to the progress bar, each answer's points show after Check, and the
end-of-quiz screen gives the quiz's points and best streak. On geog370.org the official score is worked
out by Supabase as answers are saved (`record_chapter_quiz_answer` in `supabase/setup.sql`), and each
student's total is on the admin page's **Quiz scores** tab. `QUIZ_POINTS` in `quiz.js` only drives
what students see, so change it and the SQL together.

## Weekly leaderboard

On geog370.org, the end-of-quiz screen (every chapter and unit quiz) shows **this week's top ten** quiz
scores in the student's class (course and term), from `quiz_week_leaderboard` in `supabase/setup.sql`
in the GEOG 215 repo. A week runs Saturday to Friday, Chapel Hill time, and a quiz counts in the week it
was started; a student's weekly score adds up the points from every quiz they started that week. If the
student isn't in the top ten, their own row is added below it, with their place ("You're 14th of 31").

Classmates are listed by a made-up **leaderboard name** such as "Swift Meridian", never by real name,
because quiz scores are education records under FERPA. The name comes from a hash of the student's
account, course and term, so it stays the same all term and nobody else can work out whose it is. The
student's own row says "You". The admin page's **Weekly quizzes** tab shows every student's scores for
any week with both their real and leaderboard names, and exports to CSV. On daveparr.com, with no
sign-in, the leaderboard isn't shown.

On geog370.org every answer is saved for the admin page's **Chapter quizzes** tab (see
`supabase/README.md`). On daveparr.com the quiz works the same way but nothing is saved.

## Unit quizzes

A unit can end with a unit quiz page (`units/unit-<n>-quiz.qmd`, from `_templates/unit-quiz.qmd`,
listed last in the unit in `_quarto-site.yml` only). Its bank, `quizzes/unit-<n>.json`, has no
questions of its own. It lists the unit's chapter banks, and `quiz.js` loads their questions from
those files, so editing a chapter bank changes the unit quiz too:

```json
{
  "id": "unit-1",
  "title": "Unit 1 quiz: Data Models and Projections",
  "perSession": 20,
  "chapters": ["what-is-gis", "chapter-two-id"]
}
```

A unit quiz spreads its `perSession` questions evenly across the chapters and shows which chapter
each question comes from. It is scored and saved like a chapter quiz, with the unit's `id` (`unit-1`)
in place of a chapter's, so the admin page lists it as its own row and leaderboard column. Add the
unit's `id` to `BOOK_ORDER` in `admin/index.html` right after its last chapter. Its question ids are
the chapter's id and the question's id (`what-is-gis/raster-vs-vector`), so unit results never mix
with chapter results.

If you add a chapter to a unit, add its bank's `id` to the unit bank's `chapters` too. Don't change a
unit bank's `id` once students have used it.

## Adding a chapter quiz

1. Write `quizzes/<chapter>.json`. Copy `_templates/quiz-bank.json` as a starting point.
2. Make `chapters/<chapter>-quiz.qmd` by copying `_templates/chapter-quiz.qmd` and changing the title,
   the link, and the `data-bank` path.
3. In `_quarto-site.yml` only, list the quiz page right after its chapter (quizzes are never in the
   textbook-only copy).
4. In `admin/index.html`, add the bank's `id` to `BOOK_ORDER` so the admin page lists chapters in
   book order.
5. Add the bank's `id` to its unit's bank (`quizzes/unit-<n>.json`), if the unit has a unit quiz.

## Bank format

```json
{
  "id": "what-is-gis",
  "title": "What Is GIS?",
  "perSession": 10,
  "questions": [ ... ]
}
```

`id` is how results are stored, so **don't change a bank's `id` or a question's `id` once students
have used them**. Changing a question's wording is fine. Use 20–30 questions per bank.

Text in `prompt`, `choices` and `explain` can use `` `code` ``, `**bold**` and `*italic*`. Every
question should have an `explain`, which is shown after the student answers.

### Question types

**Multiple choice.** Choices are shuffled each time, so `answer` is the index (from 0) of the
right choice in the list as written. `code` is optional and is shown above the choices (for
example, a field calculator expression or a coordinate string).

```json
{ "id": "raster-vs-vector", "type": "choice",
  "prompt": "Which data model stores the world as a grid of cells?",
  "choices": ["Raster", "Vector", "Topology", "Attribute table"],
  "answer": 0,
  "explain": "A raster is a grid of cells, each with a value. Vector data stores points, lines, and polygons." }
```

**True or false.**

```json
{ "id": "wgs84-is-datum", "type": "truefalse",
  "prompt": "WGS84 is a datum.",
  "answer": true, "explain": "..." }
```

**Fill in the blank.** If `code` contains `___`, the answer box goes there; otherwise it goes
below the prompt. Spaces are ignored and `'` and `"` count as the same. Case matters unless you add
`"ignoreCase": true`. For numbers, add `"numeric": true` and optionally `"tolerance": 0.01`. List
every spelling you'll accept in `answers`.

```json
{ "id": "fill-epsg", "type": "fill",
  "prompt": "The EPSG code for WGS84 latitude and longitude is ___.",
  "answers": ["4326"], "numeric": true, "explain": "..." }
```

**Put the tiles in order.** The student taps tiles to build the answer. `extra` adds tiles that
don't belong.

```json
{ "id": "order-georeference", "type": "order",
  "prompt": "Put the georeferencing steps in order.",
  "answer": ["Add control points", "Choose a transformation", "Check the residuals", "Save the raster"],
  "extra": ["Dissolve boundaries"], "explain": "..." }
```

The correct answer to a fill-in or tile question is shown as code only when the question has a
`code` snippet; otherwise it's shown as plain text.
