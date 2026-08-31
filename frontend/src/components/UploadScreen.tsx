import { useRef, useState } from "react"
import { ApiError, uploadDocument, type UploadProgress, type UploadedDocument } from "../api"

interface Props {
  onUploaded: (document: UploadedDocument, file: File) => void
}

export default function UploadScreen({ onUploaded }: Props) {
  const [progress, setProgress] = useState<UploadProgress | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [dragging, setDragging] = useState(false)
  const fileInput = useRef<HTMLInputElement>(null)
  const busy = progress !== null

  async function send(file: File) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are supported.")
      return
    }

    setError(null)
    setElapsed(0)
    setProgress({ phase: "sending", percent: 0 })
    const startedAt = Date.now()
    const ticker = window.setInterval(
      () => setElapsed(Math.round((Date.now() - startedAt) / 1000)),
      1000,
    )

    try {
      onUploaded(await uploadDocument(file, setProgress), file)
    } catch (problem) {
      setError(
        problem instanceof ApiError
          ? problem.message
          : "Could not reach the server. Is the backend running?",
      )
    } finally {
      window.clearInterval(ticker)
      setProgress(null)
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
        onDrop={(event) => {
          event.preventDefault()
          setDragging(false)
          const file = event.dataTransfer.files[0]
          if (file && !busy) {
            void send(file)
          }
        }}
      >
        {busy ? (
          <>
            <div className="progress">
              <div
                className="progress__bar"
                style={{
                  width: progress.phase === "sending" ? `${progress.percent}%` : "100%",
                }}
              />
            </div>
            <p className="dropzone__title">
              {progress.phase === "sending" ? "Uploading…" : "Reading and indexing"}
            </p>
            <p className="muted">
              {progress.phase === "sending"
                ? `${progress.percent}% transferred`
                : `${elapsed}s — embeddings run on CPU, so this takes a moment.`}
            </p>
          </>
        ) : (
          <>
            <svg className="dropzone__icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M12 16V4m0 0L8 8m4-4 4 4" />
              <path d="M4 16v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" />
            </svg>
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
