# Secondaries Tracker

A web app for medical school applicants to track secondary essays. Everything is saved only in each applicant's browser; there is no server, sign-in, or analytics.

- **Schools:** date received, turnaround (default 14 days), optional school deadline, interest, submitted, fee paid.
- **Base essays:** one per prompt type, saved in versions. Each school's copy remembers which base version it came from. Saving a new base version flags every school copy still on an older one; "Review changes" applies base edits to a school copy, and "Compare with base" sends a school-copy fix back to the base.
- **Do next:** ranks schools by days until due × interest, with a boost for schools nearly done. The formula is explained in the app.
- **Backup:** download/restore a JSON file. A reminder appears if there's no backup in 7 days.
- **Prompt library:** built but hidden (`SHOW_LIBRARY` in `public/index.html`) until there is a shared sheet of real prompts.

## Files
- `public/index.html` is the whole app. `public/sw.js` keeps an offline copy (bump `VERSION` when files change). Saved data lives under the localStorage key `secondaries-v1`; keep field names stable or migrate.
- Hosted on Cloudflare Workers (static assets), connected to this repo. `main` is live; other branches (like `dev`) get preview links.

Student-built. Not affiliated with AMCAS, the AAMC, or any medical school.
