# Secondaries Tracker

A web app for medical school applicants to track secondary essays. Work is saved in the applicant's browser and, if they connect it, in a hidden app folder in their own Google Drive. This site has no server, database or analytics, and never receives anyone's essays.

- **Schools:** date received, turnaround (default 14 days), optional school deadline, interest, submitted, fee paid.
- **Base essays:** one per prompt type, saved in versions. Each school's copy remembers which base version it came from. Saving a new base version flags every school copy still on an older one; "Review changes" applies base edits to a school copy, and "Compare with base" sends a school-copy fix back to the base.
- **Do next:** ranks schools by days until due × interest, with a boost for schools nearly done. The formula is explained in the app.
- **Suggestions panel:** a side panel (a collapsible bar on phones; a "Similar at your other schools" box on each essay page) groups prompts across schools that ask the same kind of thing (by prompt type, plus clinical/research/reapplicant/academic for "other"), offers to start a base, reuse an essay already written, or link prompts to an existing base; flags same-school duplicates and similar wording tagged as different types (TF-IDF cosine over the library). Dismissals are saved in `S.dismissed`.
- **Google Drive sync:** `public/config.js` holds the Google OAuth client ID (empty = Drive option hidden). Uses Google Identity Services (token model) with the `drive.appdata` scope only, and stores one file, `secondaries.json`, in the user's appDataFolder. Every record carries `u` (last-edit time) and deletions are kept in `del`; copies merge record by record (newest wins, deletions beat older edits). When an essay was edited on two computers since the last sync, the losing text is kept in `prev` and offered on the essay page. Syncs 3 s after changes, on return to the app, when back online and every minute. The ~1-hour Google token is renewed on the user's next click. Local sync state: localStorage `secondaries-sync-v1`.
- **One tab at a time:** a newer tab takes over and older tabs lock (BroadcastChannel). A visible banner appears if saving to the browser fails.
- **Backup:** download/restore a JSON file. A reminder appears if there's no backup in 7 days.
- **Prompt library:** `public/library.js` holds 2026–2027 prompts for 165 MD schools (prompts for 136), collected from each school's Student Doctor Network thread on Oct 31, 2026. Adding a school from the library, or typing a library school's name in Add school, brings in its prompts, limits, prompt types, optional flags and links to matching base essays. Regenerate the file each cycle; keep school names stable.

## Files
- `public/index.html` is the whole app. `public/sw.js` keeps an offline copy (bump `VERSION` when files change). Saved data lives under the localStorage key `secondaries-v1`; keep field names stable or migrate.
- Hosted on Cloudflare Workers (static assets), connected to this repo. `main` is live; other branches (like `dev`) get preview links.

Student-built. Not affiliated with AMCAS, the AAMC, or any medical school.
