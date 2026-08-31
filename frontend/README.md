# Front end

Vite + React + TypeScript. Upload a PDF, then ask questions about it side by side
with the document itself.

```bash
npm install
npm run dev      # http://localhost:5173
```

The backend must be running on `http://127.0.0.1:8000`. To point somewhere else,
copy `.env.example` to `.env` and set `VITE_API_URL`.

## Notes

- **Citations are verifiable.** Every answer lists the pages it used; clicking one
  opens that page in the viewer beside the chat. A citation you can check beats a
  citation you have to trust.
- **Direction is decided per message.** `src/lang.ts` compares Arabic and Latin
  character counts rather than looking for the first Arabic character, so each
  question, answer and snippet is rendered in its own direction and an English
  sentence quoting one Arabic word still reads left to right.
- **The viewer is code-split.** pdf.js is about a megabyte, so it is loaded only
  once a document is open; the upload screen ships ~64 kB gzipped.
- **Upload reports two phases.** Bytes in flight are real transfer progress from
  XHR; after that the server is embedding on CPU, which is the slow part, so the
  UI switches to an elapsed counter rather than faking a percentage.
- Theme follows the system preference and can be overridden; the choice is kept
  in `localStorage`.
