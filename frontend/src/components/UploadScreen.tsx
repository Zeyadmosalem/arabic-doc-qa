import { useRef, useState } from "react"
import { FileText, Languages, Quote, UploadCloud } from "lucide-react"
import { ApiError, uploadDocument, type UploadProgress, type UploadedDocument } from "../api"

interface Props {
  onUploaded: (document: UploadedDocument, file: File) => void
}

const FEATURES = [
  { icon: Languages, label: "Arabic & English" },
  { icon: Quote, label: "Answers cite their page" },
  { icon: FileText, label: "Your PDF never leaves the page" },
]

export default function UploadScreen({ onUploaded }: Props) {
  const [progress, setProgress] = useState<UploadProgress | null>(null)
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
    setProgress({ phase: "sending", percent: 0 })

    try {
      onUploaded(await uploadDocument(file, setProgress), file)
    } catch (problem) {
      setError(
        problem instanceof ApiError
          ? problem.message
          : "Could not reach the server. Is the backend running?",
      )
    } finally {
      setProgress(null)
    }
  }

  return (
    <section className="hero">
      <h2 className="hero__title">Ask your document anything</h2>
      <p className="hero__subtitle">
        Upload a PDF in Arabic or English. Every answer points back to the page it
        came from, so you can check it.
      </p>

      <div
        className={`dropzone${dragging ? " is-dragging" : ""}${busy ? " is-busy" : ""}`}
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
          <div className="uploading">
            <span className="uploading__label">
              {progress.phase === "sending" ? "Uploading" : "Reading and indexing"}
            </span>

            <div
              className={`progress${progress.phase === "indexing" ? " progress--pending" : ""}`}
              role="progressbar"
              aria-valuenow={progress.phase === "sending" ? progress.percent : undefined}
            >
              <div
                className="progress__bar"
                style={
                  progress.phase === "sending" ? { width: `${progress.percent}%` } : undefined
                }
              />
            </div>

            <span className="uploading__hint">
              {progress.phase === "sending"
                ? `${progress.percent}% transferred`
                : "Extracting text and building embeddings — this takes about a minute."}
            </span>
          </div>
        ) : (
          <>
            <span className="dropzone__badge">
              <UploadCloud size={22} strokeWidth={1.75} />
            </span>
            <p className="dropzone__title">Drop a PDF here</p>
            <p className="muted">or</p>
            <button className="button" onClick={() => fileInput.current?.click()}>
              Choose a file
            </button>
            <p className="dropzone__limit">Text-based PDF, up to 20 pages</p>
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

      <ul className="features">
        {FEATURES.map(({ icon: Icon, label }) => (
          <li key={label} className="feature">
            <Icon size={15} strokeWidth={1.75} />
            {label}
          </li>
        ))}
      </ul>

      <p className="muted footnote">
        Scanned PDFs have no text layer and cannot be read yet — they need OCR.
      </p>
    </section>
  )
}
