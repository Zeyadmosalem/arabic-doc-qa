import { useEffect, useRef, useState } from "react"
import { ApiError, askQuestion, type Citation, type UploadedDocument } from "../api"
import { directionOf } from "../lang"

interface Message {
  id: number
  role: "user" | "assistant"
  text: string
  citations?: Citation[]
}

interface Props {
  document: UploadedDocument
  onChangeDocument: () => void
}

export default function ChatScreen({ document, onChangeDocument }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [question, setQuestion] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const endOfThread = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endOfThread.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, busy])

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    const asked = question.trim()
    if (!asked || busy) {
      return
    }

    setMessages((current) => [...current, { id: Date.now(), role: "user", text: asked }])
    setQuestion("")
    setError(null)
    setBusy(true)

    try {
      const answer = await askQuestion(asked, document.document_id)
      setMessages((current) => [
        ...current,
        { id: Date.now() + 1, role: "assistant", text: answer.text, citations: answer.citations },
      ])
    } catch (problem) {
      setError(
        problem instanceof ApiError
          ? problem.message
          : "Could not reach the server. Is the backend running?",
      )
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="panel">
      <div className="docbar">
        <div>
          <strong className="docbar__name">{document.filename}</strong>
          <span className="muted">
            {" "}
            · {document.pages} pages · {document.chunks} chunks
          </span>
        </div>
        <button className="button button--quiet" onClick={onChangeDocument}>
          Use another document
        </button>
      </div>

      <div className="thread">
        {messages.length === 0 && (
          <p className="muted empty">
            Ask a question in Arabic or English. Every answer cites the page it came from.
          </p>
        )}

        {messages.map((message) => (
          <article key={message.id} className={`bubble bubble--${message.role}`}>
            <p dir={directionOf(message.text)} className="bubble__text">
              {message.text}
            </p>

            {message.citations && message.citations.length > 0 && (
              <div className="citations">
                {message.citations.map((citation) => (
                  <div key={citation.page} className="citation">
                    <span className="citation__page">p. {citation.page}</span>
                    <span dir={directionOf(citation.snippet)} className="citation__snippet">
                      {citation.snippet}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </article>
        ))}

        {busy && (
          <article className="bubble bubble--assistant">
            <p className="muted">Searching the document…</p>
          </article>
        )}

        <div ref={endOfThread} />
      </div>

      {error && <p className="notice notice--error">{error}</p>}

      <form className="composer" onSubmit={submit}>
        <input
          className="composer__input"
          dir={directionOf(question)}
          value={question}
          placeholder="Ask a question…"
          onChange={(event) => setQuestion(event.target.value)}
          disabled={busy}
        />
        <button className="button" type="submit" disabled={busy || !question.trim()}>
          Ask
        </button>
      </form>
    </section>
  )
}
