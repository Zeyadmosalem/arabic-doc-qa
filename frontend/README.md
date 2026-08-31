# Front end

Vite + React + TypeScript. Two screens: upload a PDF, then ask questions about it.

```bash
npm install
npm run dev      # http://localhost:5173
```

The backend must be running on `http://127.0.0.1:8000`. To point somewhere else,
copy `.env.example` to `.env` and set `VITE_API_URL`.

## Notes

- `src/lang.ts` decides text direction by comparing Arabic and Latin character
  counts, so each question, answer and citation is rendered in its own
  direction. An English sentence quoting one Arabic word still reads left to
  right.
- No UI framework and no state library — two screens do not need either.
