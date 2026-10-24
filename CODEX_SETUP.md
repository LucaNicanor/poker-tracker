# ClubWPT Gold and GTO Wizard hand-history setup

This is a new project; no hand histories or import parser existed before setup.
The private data folders and a working local file inbox are ready. Run
`npm start` and open http://127.0.0.1:3316. No dependencies need installing.
It preserves original files, identifies their source, skips duplicate files,
and provides original-file downloads. Tests verify exact byte preservation,
restart persistence, source-specific deduplication, and invalid-input handling.
The inbox was also checked in Codex's browser. Its archive currently has zero
real files. Data folders and the local catalog are excluded from Git.

## Source compatibility

- ClubWPT Gold's official help describes reviewing past hands through its Hand
  History interface. A documented bulk downloadable history format was not found
  in the official material checked. Do not assume that every historical hand can
  be exported or recovered through a public API.
- GTO Wizard documents uploading a single hand or files/folders of supported
  English-language hand histories. Its published supported-site list does not
  establish direct ClubWPT Gold compatibility. Verify with a real sample.
- GTO Wizard's help says general spreadsheet/text exports of action-frequency
  data are unavailable. This is separate from importing poker hand histories.

## Next step

Obtain a real history export, copied history, or saved hand from your account.
Import the original through the inbox, then ask Codex to inspect it and implement
the matching per-hand parser. A site name alone is not enough to test that format.
No login credentials, hands, screenshots, or session cookies were copied from
your accounts during setup. No bulk export or account API was invented.

Official sources checked October 23, 2026:
- https://support.clubwptgold.com/portal/en/kb/articles/what-is-hand-analysis
- https://help.gtowizard.com/how-to-upload-your-hand-histories/
- https://help.gtowizard.com/troubleshooting/
