# geog370.org sign-in, progress, questions and polls

geog370.org uses **the same Supabase project, Resend domain and database as
geog215.org**. The database was built for several classes ("Adding another
class" in the GEOG 215 repo's `supabase/README.md`): every roster row and
every progress row has a **course** and a **term**, and this site sends the
course code `geog370` (`SDS_COURSE` in `assets/auth-gate.html`), so GEOG 370
students only get into GEOG 370 and everything they do is filed under it.

**The database's source of truth is the GEOG 215 repo**
([`supabase/setup.sql`](https://github.com/dparr1/geog-215-spatial-data-science/blob/main/supabase/setup.sql)
and its [`supabase/README.md`](https://github.com/dparr1/geog-215-spatial-data-science/blob/main/supabase/README.md),
which covers the admin page, polls, questions, limits and troubleshooting).
This repo deliberately has no copy of `setup.sql`, so there is never a second,
older version that could be run against the shared database by mistake.

The files here that talk to Supabase are copies of the GEOG 215 ones, with
the course code and names changed:

| File | What it is |
| --- | --- |
| `assets/auth-gate.html` | The sign-in screen on every gated geog370.org page (`SDS_COURSE = "geog370"`). |
| `assets/questions.html` | "Ask a question" on highlighted text, and **My questions**. |
| `assets/polls.html` | Poll and survey banner, and the students' **Polls** list. |
| `assets/quiz/` | The chapter quiz engine (results go to `record_chapter_quiz_answer`). |
| `admin/index.html` | The admin page at https://geog370.org/admin/. It's the same page as geog215.org/admin/ (both show every course you teach); this copy shows GEOG 370's page titles and lists its quizzes in book order (`BOOK_ORDER`). |

If the database changes in the GEOG 215 repo (a new `record_*` or `admin_*`
function, say), copy the matching change to these files.

## One-time setup for GEOG 370

Nothing new is needed in Resend, and no new Supabase project. In the
**existing** Supabase project:

1. **Add the course** (SQL Editor):
   ```sql
   insert into public.courses (course, title, site_url)
   values ('geog370', 'GEOG 370: Geographic Information Science', 'https://geog370.org')
   on conflict (course) do nothing;
   ```
2. **Questions email:**
   ```sql
   update public.courses set questions_email = 'daveparr@unc.edu' where course = 'geog370';
   ```
3. **Authentication > URL Configuration > Redirect URLs:** add
   `https://geog370.org/**` (and, for Cloudflare preview builds, the
   `*.workers.dev` preview address if you want emailed links to work there).
   Without it the emailed link won't bring students back to geog370.org; the
   code in the email works either way.
4. **Email template:** the sign-in email says "GEOG 215" (subject and body).
   Supabase has one template per project, so reword both templates
   (**Confirm signup** and **Magic Link**) to something general, such as
   "Your course textbook sign-in code" / "Sign in to your course textbook".
   This also changes what GEOG 215 students see. The sender name in **SMTP
   Settings** (`GEOG 215`) is shared the same way; consider
   `Dr. Parr's textbooks` or similar.
5. **Instructors:** an instructor whose `courses` is empty already sees every
   course, GEOG 370 included. For a GEOG 370 TA only:
   ```sql
   insert into public.instructors (email, courses) values ('ta@unc.edu', '{geog370}');
   ```
6. **Add students** at https://geog370.org/admin/ (or geog215.org/admin/):
   pick **GEOG 370** in the Course picker, then **Add students** with the term.

### Test it

Add a test student with an address you can read, open https://geog370.org in
a private window, and sign in once with the code and once with the link. The
visit should appear on the admin page's **Activity** tab under GEOG 370 and
not under GEOG 215. Delete the test student afterwards.

## Things that stay GEOG 215-branded

- Sign-in emails come from `login@mail.geog215.org`, and question emails from
  `questions@mail.geog215.org` (the "From" name uses the course title, so it
  reads "GEOG 370 Questions"). Sending from `mail.geog370.org` would need a
  new Resend domain and, for sign-in email, a different SMTP sender for the
  whole Supabase project, so it isn't worth changing.
- The questions email's "Answer on the admin page" link points to
  geog215.org/admin/, which works for every course.
