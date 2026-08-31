import { lazy, Suspense, useState } from "react"
import type { UploadedDocument } from "../api"
import ChatPanel from "./ChatPanel"

// pdf.js is ~1 MB, so it should not sit in the bundle the upload screen loads.
const PdfViewer = lazy(() => import("./PdfViewer"))

interface Props {
  document: UploadedDocument
  file: File
  onChangeDocument: () => void
}

export default function Workspace({ document: uploaded, file, onChangeDocument }: Props) {
  const [page, setPage] = useState(1)
  const [showViewer, setShowViewer] = useState(true)

  return (
    <div className="workspace">
      <div className="docbar">
        <div className="docbar__meta">
          <strong className="docbar__name" title={uploaded.filename}>
            {uploaded.filename}
          </strong>
          <span className="muted">
            {uploaded.pages} pages · {uploaded.chunks} chunks
          </span>
        </div>
        <div className="docbar__actions">
          <button
            className="button button--quiet"
            onClick={() => setShowViewer((shown) => !shown)}
            aria-pressed={showViewer}
          >
            {showViewer ? "Hide PDF" : "Show PDF"}
          </button>
          <button className="button button--quiet" onClick={onChangeDocument}>
            New document
          </button>
        </div>
      </div>

      <div className={`panes${showViewer ? "" : " panes--single"}`}>
        <ChatPanel document={uploaded} onCitationClick={setPage} />
        {showViewer && (
          <Suspense
            fallback={
              <aside className="viewer">
                <p className="muted viewer__status">Loading viewer…</p>
              </aside>
            }
          >
            <PdfViewer file={file} page={page} onPageChange={setPage} />
          </Suspense>
        )}
      </div>
    </div>
  )
}
