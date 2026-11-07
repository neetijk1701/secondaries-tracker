# Med App Workspace

(Formerly Secondaries Tracker; the URL and repo name stay `secondaries-tracker`.)

A web app for medical school applicants to track secondary essays. Work is saved in the applicant's browser and, if they connect it, in a hidden app folder in their own Google Drive. This site has no server, database or analytics, and never receives anyone's essays.

- **Schools:** date received, turnaround (default 14 days), optional school deadline, interest, submitted, fee paid.
- **Base essays:** one per prompt type, saved in versions. Each school's copy remembers which base version it came from. Saving a new base version flags every school copy still on an older one; "Review changes" applies base edits to a school copy, and "Compare with base" sends a school-copy fix back to the base.
- **Do next:** ranks schools by days until due × interest, with a boost for schools nearly done. The formula is explained in the app.
- **Suggestions panel:** a side panel (a collapsible bar on phones; a "Similar at your other schools" box on each essay page) groups prompts across schools that ask the same kind of thing (by prompt type, plus clinical/research/reapplicant/academic for "other"), offers to start a base, reuse an essay already written, or link prompts to an existing base; flags same-school duplicates and similar wording tagged as different types (TF-IDF cosine over the library). Dismissals are saved in `S.dismissed`.
- **MD/PhD and DO/PhD:** library entries can carry `mdphd` ({prog, md: also|instead|unknown, prompts}). Add school shows an "Applying as: MD | MD/PhD" switch (default from the "I'm applying MD/PhD or DO/PhD" setting on the Secondaries tab, `S.prefs.dual`); each school stores `track` (single|dual) and dual-only essays carry `dual:true`. Prompt types: mdphd (Why MD/PhD), research (Research experience), resint (Research interests). `tools/build_library.py` merges `data/mdphd-prompts-2026-2027.json` when present, matching schools by `school_thread_url`. Optional `mdphd.cycle` (prompts from an earlier cycle) and `mdphd.srcType` (school_website | compilation) drive a "check the portal" note; a dual prompt with `rep: i` replaces regular prompt i for dual applicants (same box, reworded). `data/mdphd-broad-search-2026-11.json` is the raw deeper search (2023-2024 onward, any source) that filled 16 more programs.
- **Wrong-school-name check:** each essay is scanned for names and nicknames of the *other* schools on the applicant's list (curated nicknames in `NICK`, plus generated short names, eponyms and abbreviations; ambiguous one-word names like "Brown" or state names only count as part of a longer name). Shown as a banner under the editor, a chip in the school's essay list, a note in the Do next summary, and a warning when marking Ready / In portal or copying. "It's meant to be there" saves `okNames` on the essay.
- **Copy for portal:** copies the essay with straight quotes, plain spaces and no extra blank lines, then reports words and characters (with spaces) against that school's limit.
- **Fees:** per school `feeAmt`, `fee` (paid) and `waiver`; totals on the Secondaries tab and unpaid total in the Do next summary.
- **Calendar:** "Add due dates to calendar" downloads an .ics file with an all-day event per open school on its due date (stable UIDs, reminder the day before).
- **Google Drive sync:** `public/config.js` holds the Google OAuth client ID (empty = Drive option hidden). Uses Google Identity Services (token model) with the `drive.appdata` scope only, and stores one file, `secondaries.json`, in the user's appDataFolder. Every record carries `u` (last-edit time) and deletions are kept in `del`; copies merge record by record (newest wins, deletions beat older edits). When an essay was edited on two computers since the last sync, the losing text is kept in `prev` and offered on the essay page. Syncs 3 s after changes, on return to the app, when back online and every minute. The ~1-hour Google token is renewed on the user's next click. Local sync state: localStorage `secondaries-sync-v1`.
- **One tab at a time:** a newer tab takes over and older tabs lock (BroadcastChannel). A visible banner appears if saving to the browser fails.
- **Backup:** download/restore a JSON file. A reminder appears if there's no backup in 7 days.
- **Prompt library:** `public/library.js` holds 2026–2027 prompts for 238 schools: 165 MD (prompts for 136, collected Oct 31, 2026) and 73 DO campuses (prompts for 28, collected Nov 1, 2026), from each school's Student Doctor Network thread. Each entry has `deg` (MD/DO). DO prompts asking why osteopathic medicine are typed `osteo` ("Why osteopathic medicine") so one base can cover them. Rebuild with `python3 tools/build_library.py` from `data/md-prompts-2026-2027.json` and `data/do-prompts-2026-2027.json` (the raw catalogue: exact wording, limits, sources). `data/` isn't published (only `public/` is). Adding a school from the library, or typing a library school's name in Add school, brings in its prompts, limits, prompt types, optional flags and links to matching base essays. Regenerate the file each cycle; keep school names stable.

## Files
- `public/index.html` is the whole app. `public/sw.js` keeps an offline copy (bump `VERSION` when files change). Saved data lives under the localStorage key `secondaries-v1`; keep field names stable or migrate.
- Hosted on Cloudflare Workers (static assets), connected to this repo. `main` is live; other branches (like `dev`) get preview links.

Student-built. Not affiliated with AMCAS, the AAMC, or any medical school.

## New cycles and prompt updates
- `data/cycle.json` names the cycle being built (and `prev`). `tools/new_cycle.py YYYY-YYYY` starts a new cycle with empty data files and the same school names; until a school's new prompts are harvested, the library shows last cycle's prompts for it (`pc` on the school, `mdphd.cycle` for MD/PhD) and the app labels them.
- `tools/diff_library.py OLD NEW` summarizes changes between two builds.
- `HARVEST.md` is the weekly procedure (June to September) that a scheduled task follows: find threads, read them with parallel agents, check applicant reports from the Tally form (rD5rjo), build, commit to `dev`, and report. `data/harvest-state.json` tracks progress.
- In the app: essays remember the library wording they came from (`lib`, `libLimit`); when the library's wording or limit changes, the essay and school are flagged with a diff and "Use the new wording / Keep mine". Last-cycle prompts carry `pc` and are flagged if the school's new prompts don't include them.
- Rollover: data is stamped with `prefs.cycle`. When the library moves to a newer cycle, a banner offers "Start a fresh list" (current schools/essays go to an `archives` record, synced like other records; base essays stay) or "Keep this list". Past cycles appear at the bottom of Base essays, and an empty essay offers "Start from it" when the same school had a similar prompt in a past cycle.
- "Report a prompt change" links (school page, essay page, library, add-school form) open the Tally form with school, cycle and track filled in.

## Whole-cycle tracking
- Each school carries post-secondary fields: `submittedAt`, `complete`, `ii` (invite date), `iv` (interview date), `ivTime`, `ivMode`, `thanks`, `outcome` (hold | wl | acc | rej | wd), `outcomeDate`, `hist` (outcome history), `notes` (interview prep) and `reflect` (how it went). `stage(s)` turns them into a label and a board column.
- **Cycle tab:** a summary line, a "Coming up" list (interviews in the next 3 weeks, thank-you notes owed, letters to send, invites to schedule), and a board: Secondaries · Waiting · Interviews · After interview · Decisions. Do next shows the same "Interviews and letters" list.
- **Letters** are essays with family `update`, `loi` or `thanks` (`isLetter`). They're excluded from secondary progress, ranking and suggestions, but get bases, versions, Copy for portal, the wrong-school-name check, a "Send by" date (`e.due`), and "Sent" in place of "In portal".
- **Calendar file** now also has interviews (timed if a time is entered), next-day thank-you reminders, and letter send-by dates.
- **Invite timing:** `public/invites.js` (built from `data/invites-<cycle>.json` by `tools/build_invites.py`) holds per-school first/latest invite dates, report counts and first acceptance from SDN threads. It's shown on the school page and on Waiting cards; small counts are labeled. The harvest procedure is in `HARVEST.md`.

## Experiences (story bank) and letter writers
- Two synced collections that stay across cycles: `experiences` ({kind: research | clinical | activity | strength | reflection, title, org, dates, summary, items: [{id, head, text, tags}]}) and `recommenders` ({name, role, kind, asked, agreed, due, received, together, highlight, shared, expIds, notes}).
- **Experiences tab:** three sub-tabs.
  - **Experiences:** research, clinical and activities.
  - **Strengths & weaknesses:** strengths with an evidence count, which nudges below 2. Weaknesses (kind `weakness`) are framed as growth: How it shows up (`summary`), What I'm doing about it (`doing`), Signs of progress (items plus lessons tagged via `it.grow`), and a "Tell me about a weakness" practice outline. About me holds the reflections.
  - **Letter writers.**
- Lessons are tagged "Shows:" (strengths, `it.tags`) and "Working on:" (weaknesses, `it.grow`); renaming a strength or weakness carries its tags along. Weaknesses stay private: they're never auto-picked, are labeled in the writer checklist, and are left out of "Download all".
- **Import:** paste a document or choose a .txt/.json file. `parseProfile()` reads numbered sections, lettered entries, Summary / What I learned / Description / Reflection labels and "Headline: story" bullets, with a preview before import.
- **Letter writers:** tracking (asked, agreed, due, submitted; due dates show in Coming up, on Do next and in the calendar file) and a tailored summary for each writer: "Our work together", "What I'd love you to highlight", the shared experience first, then the chosen experiences, strengths and reflections. Download as a .doc (HTML), print or save as PDF, or copy as text.
- **Essays:** a "Stories that fit" panel ranks stories by shared rare words plus the kind of story that usually answers that prompt type.
- **Interviews:** each school's "After you submit" panel has "Stories to have ready" (`s.stories`, keys "expId|itemId").

## Primary application tab
- Services: AMCAS, TMDSAS and AACOMAS (`prefs.services`; AMCAS is on by default). MD/PhD essays appear when `prefs.dual` is on.
- Limits (2026-2027, chars with spaces), in `SVC`:
  - AMCAS: personal comments 5,300; MD-PhD 3,000; significant research 10,000; W&A 15 × 700, with 3 most meaningful × 1,325.
  - TMDSAS: personal statement 5,000; personal characteristics 5,000; optional 2,500; MD/PhD A and B 5,000 each; activities 500, with 3 meaningful × 500. Sources disagree on the activity length.
  - AACOMAS: personal statement 5,300; experiences and achievements 600.
- Each service is an `apps` record (`app-<svc>`) that `school()` also resolves, so primary essays use the normal essay editor, bases and versions.
  - Primary essays carry `pkey` and family `ps`, `mdphd`, `research`, `diversity` or `anything`, so personal statements share one base and MD/PhD secondaries can start from the primary MD/PhD base.
  - They're excluded from secondary progress and suggestions (`isPrimaryE`).
- Activities (`acts`): {svc, expId, title, type, org, dates, hours, desc, mm, mmText}. They can start from an Experiences entry (type guessed from its kind), have live character meters, and show that experience's lessons as material for the most meaningful text.
- Start a fresh list archives `apps` and `acts` with the cycle; bases stay.

## Writing tools
Everything runs in the browser; nothing is sent anywhere and no AI rewrites text.
- **Focus view** (`ui.focus`, `vFocus`): a full-screen editor with the prompt, a side rail (Stories, Base, Notes in `e.scratch`, Checks, History), a meter, status and "Copy for portal". Esc or Done exits.
- **Version history** (`e.hist`, synced with the essay):
  - Saved automatically every 15 minutes while writing (keeps the last 8) and before a cut of more than 15% of an essay over 200 characters.
  - Named versions keep the last 10.
  - Compare shows a diff against the current text; Restore saves the current text first ("Before restoring"). Starting from a base also saves first.
- **Writing checks** (`essayChecks`): common phrases, wording repeated from another essay for the same school or service (shared 8-word runs ≥ 15%), overused words, many sentences starting with "I", sentences over 35 words, passive voice, paragraph balance. "Show" selects the passage in the editor.

## Sample data
"Explore with sample data" (footer, and the empty Do next page) loads a fictional applicant, Jordan, applying to 9 real library schools at every stage: secondaries in progress (Baylor with clichés for the checks, UT Southwestern with repeated wording and an out-of-date base copy), interviews coming up and done, an acceptance, a waitlist with a letter of intent, a hold with an update letter, a rejection; 7 base essays with versions; AMCAS and TMDSAS essays and activities; 10 experiences with strengths and a weakness; 3 letter writers. `seed()` builds it with the same helpers the app uses.
- Your own data is set aside in `secondaries-stash-v1` and restored by "Back to my data". In sample mode nothing syncs to Drive (`S.demo`), and connecting Drive restores your data first.

## Experience log
Each experience is written up when it ends: what I did (summary) and what I learned (lessons), like a letter-writer profile. Long-running ones keep one write-up that gets revised.
- **Dates:** `start` and `end` months (`YYYY-MM`) plus `ongoing` ("Still doing this", which clears `end`). `expDates()` formats them, falling back to imported free text in `dates`. **Hours:** one total in `hours` (`expHours`), used when starting an activity.
- **Timeline:** the Experiences sub-tab groups story experiences under Ongoing, then "Ended in <year>", newest first.
- **Write-ups to do** (`writeupNudge`): something that ended without a summary and at least one lesson; something ongoing that has no write-up, or whose write-up (`wu`, set when the summary or a lesson changes) is more than six months old.
- **Contact** (`contact`, `contactRole`, `contactEmail`) → "Add as a letter writer" creates a recommender linked to the experience.
- **About me starters** (`ABOUT_STARTERS`): why medicine, career goals in medicine and research, group vs individual work, what letter writers should know.
- **Log-only mode:** opening `#log` with nothing else saved sets `prefs.applying=false`: the app is titled "Experience Log", shows only Experiences (log, strengths & weaknesses, letter writers), and skips the tour. "I'm applying this cycle" (`applying-on`) shows everything; "Not applying yet? Show only the log" goes back. Same storage and Drive file either way. The About page links to it.
- Older records may have `log` entries from a short-lived day-by-day version; they're ignored except that their hours count toward the total until `hours` is set.

## Numbered versions
Every essay (secondaries, primary, letters) has numbered versions (`e.vers`: [{n, text, at, note}]); the working draft is v(n+1).
- "Mark vN done" freezes the text with an optional note; the strip above the editor shows v1 · v2 · v3 (working). Clicking a version shows it read-only, compares it with the draft, copies it, or starts the draft over from it (the unfinished draft goes to Recovery copies as "Abandoned vN draft").
- Setting an essay to In portal (Sent, for letters) or ticking a school's Submitted freezes a "Submitted" version, so what each school received is always kept.
- Autosaves (`e.hist`: every 15 minutes, before a big cut, before restoring or starting over) are a recovery net under "Recovery copies". Older named saves were converted to numbered versions on first load (`migrateVers`).
- Base essays keep their own numbered versions (Save as vN), as before.

## Readable copy in Drive (opt-in)
"Readable copy in your Drive" (footer, when Drive is connected) writes Google Docs into a visible `Med App Workspace` folder. One-way: the hidden `secondaries.json` stays the source of truth.
- **Permission:** adds `drive.file` (only files this app creates), requested when the user turns it on (`prefs.mirror`). Add `drive.file` under Data access on the Google Cloud consent screen.
- **Layout** (`mirrorDocs()`): **Start here** (links to the latest file for each essay, written last); Experience log; Strengths and reflections (weaknesses only with "Include weaknesses", `prefs.mirrorWeak`); Base essays; Letter writers/Summary for <name> (no header line, so it can be shared); `<2026–27> Primary/` and `<2026–27> Secondaries/<School>/`, where each essay's files are named by version: `Diversity – v1 (First draft)`, `Diversity – v2 (Submitted)`, `Diversity – v3 (working)`. The working file exists only while the text differs from the last finished version; when that version is finished, the same file is renamed to it and frozen (`wn` on the file entry), so no two files hold the same text. Prompts not started have no file. Plus `<Service> – Activities` and a school Notes Doc if any. Each essay page has "Open in Drive". The folder path is part of each Doc's hash, so changing the layout moves Docs instead of duplicating them; folders left empty are not deleted (they could hold the user's own files).
- **Bookkeeping** (`S.mirror`: root, folders, files {key: id, hash, modifiedTime, folder, cyc}) syncs with the data (`mergeMirror`), and every file carries `appProperties.maw = key` (folders: a hash of their path), so a lost map finds existing files instead of duplicating them.
- **Updates:** 2 minutes after changes or "Update now"; only Docs whose content hash changed are rewritten (same file, so shared links keep working); renames follow; Docs for things deleted in the app go to Drive's Trash, except earlier cycles' folders, which stay as an archive.
- **Edited in Drive:** if a Doc's modifiedTime is newer than the app's last write, it's skipped and listed with See the Drive text / Replace with the app's version / Keep my Drive edits (stop updating).
- Sample mode never writes to Drive. Turning it off leaves the folder alone.
