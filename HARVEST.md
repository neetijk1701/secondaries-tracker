# Weekly prompt check

Each week from June through September, a scheduled task follows this guide. It refreshes the prompt library from Student Doctor Network (SDN) and from applicants' reports, puts any changes on the **dev** preview, and tells Neetij. **It never touches `main`**: Neetij says "make it live" first.

Repo: `neetijk1701/secondaries-tracker` (private). Live site: https://secondaries-tracker.wusm-tools.workers.dev · Preview: https://dev-secondaries-tracker.wusm-tools.workers.dev

## 0. Set up
- Attach the repo with push access (`add_repo` owner `neetijk1701`, repo `secondaries-tracker`), clone it, then `git checkout dev && git pull`. If `dev` is behind `main`, merge `main` into `dev` first.
- Read `data/cycle.json` and `data/harvest-state.json` (create the second one if it's missing: `{"cycle": "...", "last_run": null, "last_report_check": null, "schools": {}}`).

## 1. Is it a new cycle?
The cycle that starts in summer of year Y is `Y-(Y+1)`; for example, a run in June 2027 is in `2027-2028`.
- If `data/cycle.json`'s `cycle` is older than that and the run date is on or after May 1, run `python3 -I tools/new_cycle.py Y-(Y+1)`.
  - It creates empty data files with the same school names, and every school falls back to last cycle's prompts, labeled in the app.
- Then run `python3 -I tools/build_library.py` and commit "Start the Y-(Y+1) cycle" to `dev`.
- Reset `harvest-state.json` `schools` to `{}` and set its `cycle`.

## 2. Find each school's new thread
SDN has one thread per school per cycle, titled like `2027-2028 Baylor College of Medicine`. They are listed in SDN's allopathic and osteopathic school-specific discussion forums. Each data row has `prev_thread_url` (last cycle's thread) to help identify the school.
- Use WebSearch (`site:forums.studentdoctor.net "2027-2028" <school>`) or WebFetch the forum listing pages.
- Record the thread in the row's `school_thread_url`. For MD/PhD rows, use the same thread as the regular row.
- Save each school's thread and status in `harvest-state.json` so later weeks skip the search.

## 3. Read the threads (fan out)
Check these schools:
- (a) schools with no prompts yet for this cycle;
- (b) schools whose thread has new posts since `last_checked` that might correct prompts (for example "they changed the prompt", "the limit is actually…"). Stop doing (b) once a school's prompts have been stable for 3 weeks.

Split the schools into batches of about 25 and give each batch to a parallel subagent. Each subagent:
- reads the thread's first page (the first post usually collects the prompts), plus any pages newer than `last_page`;
- returns **only JSON**: one record per school in the schema below, with the prompts copied word for word.

Rules for subagents:
- Sources: SDN threads first, then Reddit r/premed, then the school's own website. Never invent or paraphrase a prompt.
- If a post shortens a prompt, set `abridged: true`.
- Set `source_url` to the exact page and post, and say in `source_note` which post it came from and its date.
- If a school says no written secondary, use `no_written_secondary_note`.
- MD/PhD prompts go in `data/mdphd-prompts-<cycle>.json`. Set `md_secondary` to `also` / `instead` / `unknown`, and `cycle` to the cycle the wording is from.
- **Keep `school` names exactly as they are in the file.** The build matches schools across cycles by name.

Record schema, regular file (`data/md-prompts-<cycle>.json`, `data/do-prompts-<cycle>.json`):
```json
{"school": "Name (ST)", "state": "ST", "cycle": "2027-2028", "school_thread_url": "...", "source_url": "...", "source_note": "SDN post #4, Jun 30 2027", "no_written_secondary_note": null,
 "prompts": [{"text": "...", "limit": 500, "unit": "words|characters", "required": true, "group": null, "type": "why_school", "abridged": false}]}
```
- Regular `type`: diversity, challenge, why_school, gap, team, anything_else, career, service, ethics, other.
- MD/PhD `type` adds: mdphd_why, research, research_interest.

## 4. Applicant reports
The app's "Report a prompt change" link opens the Tally form **rD5rjo** ("Secondaries Tracker: report a prompt change").
- Fetch its submissions since `last_report_check` with the Tally tools.
- Each report has the school, cycle, track (MD or MD/PhD), what changed, the prompt text and the limit.
- Apply a report only if you can confirm it on SDN, Reddit or the school's site, or if two or more separate reports agree word for word. Note "applicant report, confirmed by …" in `source_note`.
- List the rest in the summary as unconfirmed, for Neetij to decide on.
- Never copy a reporter's email or other details into the repo.

## 5. Build and check
- `python3 -I tools/build_library.py`, which must print no errors. Check that the school count didn't drop and that `node -e 'global.window={};require("./public/library.js")'` loads.
- `git show origin/main:public/library.js > /tmp/live.js && python3 -I tools/diff_library.py /tmp/live.js public/library.js > /tmp/changes.md`
- Spot-check 3 changed schools against their source posts.
- Bump `VERSION` in `public/sw.js` (for example `sec-v17` to `sec-v18`) so browsers pick up the new library.

## 6. Commit to dev
- Update `harvest-state.json` (`last_run`, `last_report_check`, per-school `last_checked` / `last_page` / `status`).
- Commit the data files, `public/library.js`, `public/sw.js` and the state file to **dev** only, with the message "Weekly prompt check <date>: N newly posted, M changed". Push.
- Wait for the Cloudflare preview build (a GitHub check run on the commit), then confirm that `https://dev-secondaries-tracker.wusm-tools.workers.dev/sw.js` shows the new VERSION.
- If nothing changed, don't commit; just report "no changes".

## 7. Tell Neetij
Send a short summary: how many schools have this cycle's prompts now, which were newly posted or changed, any unconfirmed reports, and anything odd. End with: "Check the preview, then say **make it live**."

Going live (only when Neetij says so): `git checkout main && git merge --no-ff origin/dev && git push`, then `git push origin main:dev`. A fast-forward won't deploy, because Cloudflare builds each commit once. Wait for the build whose link goes to `/production/builds/` and confirm that the live `sw.js` VERSION matches.

If the project notes doc `claude/secondary-tracker-status.md` is reachable, add a one-line entry under "Weekly prompt check".

# Invite timing (July to May)

The Cycle tab shows, per school, when applicants on SDN have reported interview invites and acceptances. The data is in `data/invites-<cycle>.json` and is built into `public/invites.js` by `python3 -I tools/build_invites.py`. These counts show timing, not anyone's chances.

What the Nov 2026 pilot of 5 schools taught us; follow it:
- **Fetch explicit page URLs with a cache-buster** (`<thread>page-N?r=<run date>`, e.g. `page-3?r=20261109`). Both the bare thread URL and plain `page-N` URLs sometimes serve stale copies with the wrong "Page X of Y" (Nov 2026: Indiana showed 4 pages when it had 6). The `?r=` suffix returned current pages every time. Record `pages_total` and `last_post`.
- Records harvested on Nov 5, 2026 for 30 of the schools (Albany–Case Western, Duke–Geisinger, Loma Linda–MUSC) used plain `page-N` URLs and may miss the last few days of posts. On the next weekly run, re-read their last page with `?r=` before adding new events.
- **Ask WebFetch for a table of every post**: post number, date, and whether the poster reports *receiving* an interview invite (II), a pre-interview rejection, an acceptance (A), a waitlist (WL), a post-interview rejection, or a hold. A short summary drops posts.
- **Count only first-person reports of something received.** Leave out questions, "I have my interview" with no invite, timelines where "II 9/29" might be the interview date, and quotes of other posts. Put left-out and ambiguous posts in `notes`. Never store usernames or post text.
- **Dates:** use the receipt date when a post states one ("got it yesterday", "II 7/20"), otherwise the post date. Posts from the last week show only "Monday" or "Yesterday"; work those out from the run date.
- Drop obvious outliers, such as one vague early post weeks before the first wave, by listing them in `exclude_posts` with a reason.
- School-specific steps (pre-interview "under consideration" emails, special tracks like WARM or MSTP) are `hold` or noted.

Weekly (incremental): for each school, read only pages newer than `last_post`, and append new events. Use parallel subagents in batches of about 25 schools, and give each the rules above. After building, spot-check 3 schools against their threads, then commit `data/invites-*.json` and `public/invites.js` to **dev** with the prompt changes, and include "N new invite reports at M schools" in the summary to Neetij.

Record schema:
```json
{"school": "<exact library name>", "thread_url": "...", "pages_total": 3, "last_post": 122, "checked": "YYYY-MM-DD",
 "events": [{"type": "II|preR|A|WL|R|hold", "date": "YYYY-MM-DD", "post": 27, "res": "IS|OOS|null"}],
 "exclude_posts": [20], "notes": "..."}
```
