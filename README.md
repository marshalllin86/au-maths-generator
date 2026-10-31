# Daily Practice Worksheet Generator

A small desktop app for creating English math practice worksheets as PDFs.

## Try it online

Generate a worksheet in your browser at **[mathsgenerator.flow-ai.top](https://mathsgenerator.flow-ai.top/)**. Choose a main practice topic to create a fresh 30-question worksheet: 20 questions on your selected topic and 10 mixed questions. You can show the answers on screen, print the student worksheet, or save it as a PDF. The answer key is not included in the printed worksheet.

The web generator runs on Cloudflare Workers. You can also run the desktop app locally to generate batches of worksheets and use the weekly print workflow described below.

## First version

- The GUI creates five A4 worksheets in one batch under the same settings. Each worksheet contains 30 questions: 20 questions of the selected operation and 10 mixed questions.
- Mixed questions use one operation per question and draw from integer, fraction, percentage, and decimal arithmetic.
- The PDF has a student worksheet followed by a separate answer key.
- The student page is titled **Daily Practice** and has Name, Date, Time, and Score fields on one line.
- Subtraction questions do not produce negative answers. Integer division uses a one- or two-digit dividend. Decimal division has a terminating answer with at most three decimal places.
- Integer multiplication uses two-digit factors (10–99).
- Percentage multiplication includes percentage × percentage and percentage × whole number.
- Fraction practice includes the four operations with two fractions and chained multiplication/division with three fractions; answers are shown in simplest form.
- Unit conversion practice covers adjacent length units (km, m, cm, mm), capacity (L, ml), time (hours, minutes, seconds), and area units (km², m², cm², mm²).
- The web version supports manual progress tracking after signing in. Question-by-question answer tracking and error review are future work.

## Weekly print pack

The weekly print section has five independent topic selectors. Choose any supported single-operation topic for each worksheet; topics can be repeated. The initial selection is 3 integer addition/subtraction worksheets, 1 integer multiplication/division worksheet, and 1 fraction addition worksheet. The app remembers the selection in `Math\weekly_selection.json`.

The five original PDFs, including answer keys, are saved under the configured output folder's `Generated\YYYY-MM-DD` directory. The app also makes student-only two-page PDFs, sends pages 1–2 to the selected printer, and moves successfully submitted print copies under `Printed\YYYY-MM-DD`. If a print job fails, its two-page PDF stays in `Print Queue\YYYY-MM-DD` for retry. The app does not print automatically on a weekly schedule; click the button when you are ready. Only the five topics currently selected in the GUI are generated and submitted for printing.

The app uses the printer named by optional `PREFERRED_PRINTER` in `.env` when Windows reports it as available; otherwise, it uses the first available printer. Printing uses SumatraPDF. An installed `SumatraPDF.exe` on `PATH` is used automatically. Alternatively, download the portable 64-bit SumatraPDF and place it at `tools\sumatra\SumatraPDF-3.6.1-64.exe`; this local executable is ignored by Git. See [SumatraPDF installation](https://www.sumatrapdfreader.org/docs/Installation).

## Run

Install Python 3.11 or later, create a local virtual environment, then install the PDF dependency:

```powershell
python -m venv .venv --without-pip
python -m pip install --target .venv\Lib\site-packages "fpdf2==2.7.4"
```

Copy `.env.example` to a local `.env` beside `app.py` and set `MATH_OUTPUT_DIR` to the output folder. Relative paths are resolved from the project directory. For example:

```dotenv
MATH_OUTPUT_DIR=./Math
```

The `.env` file is ignored by Git so machine-specific paths are not uploaded.

Launch the GUI:

```powershell
.\.venv\Scripts\python.exe app.py
```

Choose the operation for the 20 single-operation questions, then choose an output folder. Five distinct worksheets are generated with the remaining 10 questions mixed automatically. Each file includes its own answer key.

Files are named like `Daily Practice - integer-add - 30 Questions - Set 01 of 05.pdf`; the selected operation, question count, and batch position are included. If a name already exists, a revision suffix is added so earlier exports are kept.

## Web preview (Cloudflare Workers)

The web preview reuses `worksheet.py` and presents the worksheet in an English-language browser page. It generates 20 questions for the selected topic and 10 mixed questions. The browser print layout puts 15 questions on each page, with a continued worksheet header; the answer key is screen-only. The existing desktop PDF and printer workflow remains separate.

The static page is in `public/`, and `cloudflare_worker.py` provides the FastAPI endpoints. Cloudflare serves both through a Python Worker. Install the Cloudflare tooling and run a local preview with:

```powershell
uv sync
uv run pywrangler dev
```

Deploy after authenticating Wrangler with your Cloudflare account:

```powershell
uv run pywrangler deploy
```

The first deployment should use the generated `workers.dev` URL. Add `mathsgenerator.flow-ai.top` in the Cloudflare Worker custom-domain settings only after the preview works and after checking what currently serves that hostname.

## Web progress tracking

The web page uses Supabase Auth for email/password sign-in and `public.practice_sessions` to store a user's practice date, main topic, and manually entered score out of 30. Signed-in users can see their latest 30 records. Row Level Security restricts reads and inserts to the signed-in user's own records. The schema is recorded in `supabase/migrations/20261018001023_create_practice_sessions.sql`.

The Cloudflare Worker returns `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` from `wrangler.jsonc` at `/api/config`. The publishable key is intended for browser use; database access is protected by RLS. Never put a Supabase secret or service-role key in the browser or this public repository. Supabase JS is loaded from a version-pinned CDN URL.

In Supabase Auth settings, allow the app's origin as a redirect URL, including `https://mathsgenerator.flow-ai.top` and `http://localhost:8787` for local development. If email confirmation is enabled, users must confirm the signup email before signing in.

## Operation choices

The GUI offers integer, fraction, percentage, and decimal addition, subtraction, multiplication, and division. Fraction practice also includes all four operations with two fractions and chained multiplication/division with three fractions. Percentage multiplication randomly includes both supported forms. Fraction answers are reduced to simplest form. Apply the migration in `supabase/migrations/20261027001024_add_fraction_practice_topics.sql` to allow saving results under the new topics.

## Original project

This project builds on [januschung/math-worksheet-generator](https://github.com/januschung/math-worksheet-generator), licensed under GPL-2.0. Its original command-line generator remains in `run.py`; the new desktop workflow starts from `app.py`.
For Cloudflare Workers Builds, use this branch (`cloudflare-web-preview`), root directory `/`, build command `uv sync`, and deploy command `uv run pywrangler deploy`. Push a new commit to this branch to trigger a fresh build after changing the branch settings.
