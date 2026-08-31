import { useEffect, useRef, useState } from "react"
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut } from "lucide-react"
import { Document, Page, pdfjs } from "react-pdf"
import "react-pdf/dist/Page/AnnotationLayer.css"
import "react-pdf/dist/Page/TextLayer.css"

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url,
).toString()

const ZOOM_STEPS = [0.75, 1, 1.25, 1.5, 2]

interface Props {
  file: File
  page: number
  onPageChange: (page: number) => void
}

export default function PdfViewer({ file, page, onPageChange }: Props) {
  const [pageCount, setPageCount] = useState(0)
  const [width, setWidth] = useState(0)
  const [zoom, setZoom] = useState(1)
  const frame = useRef<HTMLDivElement>(null)

  // react-pdf needs an explicit pixel width, so track the column as it resizes.
  useEffect(() => {
    const element = frame.current
    if (!element) {
      return
    }
    const observer = new ResizeObserver(([entry]) =>
      setWidth(Math.floor(entry.contentRect.width)),
    )
    observer.observe(element)
    return () => observer.disconnect()
  }, [])

  // A jump from a citation should start at the top of the new page. The
  // highlight itself needs no state: the Page below is keyed, so remounting
  // replays its CSS animation.
  useEffect(() => {
    frame.current?.scrollTo({ top: 0 })
  }, [page])

  const go = (to: number) => onPageChange(Math.min(Math.max(to, 1), pageCount || 1))
  const stepZoom = (direction: 1 | -1) => {
    const next = ZOOM_STEPS.indexOf(zoom) + direction
    if (next >= 0 && next < ZOOM_STEPS.length) {
      setZoom(ZOOM_STEPS[next])
    }
  }

  return (
    <aside className="viewer">
      <div className="viewer__bar">
        <div className="viewer__group">
          <button
            className="iconbutton"
            onClick={() => go(page - 1)}
            disabled={page <= 1}
            aria-label="Previous page"
          >
            <ChevronLeft size={16} strokeWidth={2} />
          </button>
          <span className="viewer__count">
            {page}
            {pageCount > 0 && ` / ${pageCount}`}
          </span>
          <button
            className="iconbutton"
            onClick={() => go(page + 1)}
            disabled={pageCount > 0 && page >= pageCount}
            aria-label="Next page"
          >
            <ChevronRight size={16} strokeWidth={2} />
          </button>
        </div>

        <div className="viewer__group">
          <button
            className="iconbutton"
            onClick={() => stepZoom(-1)}
            disabled={zoom === ZOOM_STEPS[0]}
            aria-label="Zoom out"
          >
            <ZoomOut size={16} strokeWidth={2} />
          </button>
          <span className="viewer__zoom">{Math.round(zoom * 100)}%</span>
          <button
            className="iconbutton"
            onClick={() => stepZoom(1)}
            disabled={zoom === ZOOM_STEPS[ZOOM_STEPS.length - 1]}
            aria-label="Zoom in"
          >
            <ZoomIn size={16} strokeWidth={2} />
          </button>
        </div>
      </div>

      <div className="viewer__frame" ref={frame}>
        <Document
          file={file}
          onLoadSuccess={({ numPages }) => setPageCount(numPages)}
          loading={<p className="muted viewer__status">Opening document…</p>}
          error={<p className="muted viewer__status">This PDF could not be displayed.</p>}
        >
          {width > 0 && (
            <Page
              key={`${page}-${zoom}`}
              className="is-flashing"
              pageNumber={page}
              width={Math.floor((width - 24) * zoom)}
              renderAnnotationLayer={false}
              loading={<p className="muted viewer__status">Rendering page {page}…</p>}
            />
          )}
        </Document>
      </div>
    </aside>
  )
}
