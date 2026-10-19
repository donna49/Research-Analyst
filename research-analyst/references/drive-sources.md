# Drive Sources folder: documents the plugin cannot fetch itself

Some sources are closed to the plugin: SEDAR+ (captcha), Intelligize, Law360 and FT.com (paid), and
PACER documents not in RECAP. For these, Andrew saves the document to Drive and the plugin reads it from there
with the Google Drive connector. Paid sources are never bypassed.

## Folders

- **Research Memos** (`1YUitDDaH27i-mff9V16Lt6axwcdzQG3_`): finished memos (memo-writer §5).
- **Research Memos / Sources** (`1z1Idktsn2NArNJpsPi8hL64IvFDV5PLd`): one subfolder per case, named
  `<TICKER> <drop date>` (e.g. `GLO 2025-01-24`).

## At the start of a case (first-review, before step 1)

1. Search for the case subfolder: `parentId = '1z1Idktsn2NArNJpsPi8hL64IvFDV5PLd' and title contains
   '<TICKER>'`. If none exists, create it (`create_file`, `contentMimeType`
   `application/vnd.google-apps.folder`, `parentId` the Sources id).
2. List its files (`parentId = '<case folder id>'`), following the page token until none comes back.
3. Read each one with `read_file_content` (PDF, Word, Google Doc and images are supported). Save the text
   to `runs/<date>/<TICKER>/sources/drive_<file id>.txt`. Record a `search` record listing the files
   read, with their Drive ids and modified times.

## When a document is needed and cannot be fetched

Do not stop. Record a `gap`, carry on with what can be reached, and add a line to
`runs/<date>/<TICKER>/to_save.md`:

| # | Source | What to save | Exact search or path | Why (memo section) |
|---|---|---|---|---|
| 1 | SEDAR+ | Q3 2024 MD&A | SEDAR+ › «issuer» › Documents › 2024-11-12 | Total Mix, language table |
| 2 | Intelligize | Q3 2024 call transcript | «exact query» | first-review step 6 |

At each checkpoint, show `to_save.md` with the link to the case subfolder. When Andrew says the files
are saved, repeat steps 2–3 and close each `gap` the new documents settle.

## How saved documents are cited

Cite the document itself, not Drive: a SEDAR+ MD&A saved to Drive is the MD&A (tier 1), footnoted as
in his style. Law360 and FT.com articles are media (tier 3, "reported by"). Intelligize transcripts
are tier 2. The Drive file id goes in `memo_trace.json` and `memo_annex.md` only, never in the memo.

## Limits

- Read only the case subfolder and the Research Memos corpus listed in `corpus.md`. Never search
  the rest of the Drive for case documents.
- Never move, rename or trash a file Andrew saved.
