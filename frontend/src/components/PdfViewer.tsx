import { useEffect, useRef, useState } from "react"
import { Document, Page, pdfjs } from "react-pdf"
import "react-pdf/dist/Page/AnnotationLayer.css"
import "react-pdf/dist/Page/TextLayer.css"

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url,
).toString()

interface Props {
  file: File
  page: number
  onPageChange: (page: number) => void
}

export default function PdfViewer({ file, page, onPageChange }: Props) {
  const [pageCount, setPageCount] = useState(0)
  const [width, setWidth] = useState(0)
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

  const go = (to: number) => onPageChange(Math.min(Math.max(to, 1), pageCount || 1))

  return (
    <aside className="viewer">
      <div className="viewer__bar">
        <button
          className="iconbutton"
          onClick={() => go(page - 1)}
          disabled={page <= 1}
          aria-label="Previous page"
        >
          ‹
        </button>
        <span className="viewer__count">
          Page {page}
          {pageCount > 0 && ` of ${pageCount}`}
        </span>
        <button
          className="iconbutton"
          onClick={() => go(page + 1)}
          disabled={pageCount > 0 && page >= pageCount}
          aria-label="Next page"
        >
          ›
        </button>
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
              pageNumber={page}
              width={width}
              renderAnnotationLayer={false}
              loading={<p className="muted viewer__status">Rendering page {page}…</p>}
            />
          )}
        </Document>
      </div>
    </aside>
  )
}
