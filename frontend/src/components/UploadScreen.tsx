import { useRef, useState } from "react"
import { ApiError, uploadDocument, type UploadedDocument } from "../api"

interface Props {
  onUploaded: (document: UploadedDocument) => void
}

export default function UploadScreen({ onUploaded }: Props) {
  const [busy, setBusy] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [dragging, setDragging] = useState(false)
  const fileInput = useRef<HTMLInputElement>(null)

  async function send(file: File) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are supported.")
      return
    }

    setError(null)
    setBusy(true)
    setElapsed(0)
    const startedAt = Date.now()
    const ticker = window.setInterval(
      () => setElapsed(Math.round((Date.now() - startedAt) / 1000)),
      1000,
    )

    try {
      onUploaded(await uploadDocument(file))
    } catch (problem) {
      setError(
        problem instanceof ApiError
          ? problem.message
          : "Could not reach the server. Is the backend running?",
      )
    } finally {
      window.clearInterval(ticker)
      setBusy(false)
    }
  }

  function onDrop(event: React.DragEvent) {
    event.preventDefault()
    setDragging(false)
    const file = event.dataTransfer.files[0]
    if (file && !busy) {
      void send(file)
    }
  }

  return (
    <section className="panel">
      <div
        className={`dropzone${dragging ? " dropzone--active" : ""}${busy ? " dropzone--busy" : ""}`}
        onDragOver={(event) => {
          event.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        {busy ? (
          <>
            <div className="spinner" aria-hidden="true" />
            <p className="dropzone__title">Reading and indexing your document</p>
            <p className="muted">
              {elapsed}s elapsed — embeddings run on CPU, so this takes a moment.
            </p>
          </>
        ) : (
          <>
            <p className="dropzone__title">Drop a PDF here</p>
            <p className="muted">Arabic or English, up to 20 pages</p>
            <button className="button" onClick={() => fileInput.current?.click()}>
              Choose a file
            </button>
          </>
        )}

        <input
          ref={fileInput}
          type="file"
          accept="application/pdf,.pdf"
          hidden
          onChange={(event) => {
            const file = event.target.files?.[0]
            if (file) {
              void send(file)
            }
            event.target.value = ""
          }}
        />
      </div>

      {error && <p className="notice notice--error">{error}</p>}

      <p className="muted footnote">
        Scanned PDFs have no text layer and cannot be read yet — they need OCR.
      </p>
    </section>
  )
}
