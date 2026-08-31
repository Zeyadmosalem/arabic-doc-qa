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
  onCitationClick: (page: number) => void
}

const STARTERS = [
  "What is this document about?",
  "Summarise the main points.",
  "ما هو موضوع هذا المستند؟",
  "ما أهم النقاط الواردة فيه؟",
]

export default function ChatPanel({ document: uploaded, onCitationClick }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [question, setQuestion] = useState("")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState<number | null>(null)
  const endOfThread = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endOfThread.current?.scrollIntoView({ behavior: "smooth", block: "end" })
  }, [messages, busy])

  async function ask(asked: string) {
    if (!asked || busy) {
      return
    }
    setMessages((current) => [...current, { id: Date.now(), role: "user", text: asked }])
    setQuestion("")
    setError(null)
    setBusy(true)

    try {
      const answer = await askQuestion(asked, uploaded.document_id)
      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "assistant",
          text: answer.text,
          citations: answer.citations,
        },
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

  async function copy(message: Message) {
    await navigator.clipboard.writeText(message.text)
    setCopied(message.id)
    window.setTimeout(() => setCopied(null), 1500)
  }

  return (
    <section className="chat">
      <div className="thread">
        {messages.length === 0 && !busy && (
          <div className="starters">
            <p className="muted">Ask in Arabic or English. Every answer cites its page.</p>
            <div className="starters__chips">
              {STARTERS.map((starter) => (
                <button
                  key={starter}
                  className="chip"
                  dir={directionOf(starter)}
                  onClick={() => void ask(starter)}
                >
                  {starter}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <article key={message.id} className={`bubble bubble--${message.role}`}>
            <p dir={directionOf(message.text)} className="bubble__text">
              {message.text}
            </p>

            {message.role === "assistant" && (
              <div className="bubble__tools">
                <button className="linkbutton" onClick={() => void copy(message)}>
                  {copied === message.id ? "Copied" : "Copy"}
                </button>
              </div>
            )}

            {message.citations && message.citations.length > 0 && (
              <div className="citations">
                {message.citations.map((citation) => (
                  <button
                    key={citation.page}
                    className="citation"
                    onClick={() => onCitationClick(citation.page)}
                    title={`Open page ${citation.page}`}
                  >
                    <span className="citation__page">p. {citation.page}</span>
                    <span dir={directionOf(citation.snippet)} className="citation__snippet">
                      {citation.snippet}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </article>
        ))}

        {busy && (
          <article className="bubble bubble--assistant">
            <span className="typing" aria-label="Searching the document">
              <i />
              <i />
              <i />
            </span>
          </article>
        )}

        <div ref={endOfThread} />
      </div>

      {error && <p className="notice notice--error">{error}</p>}

      <form
        className="composer"
        onSubmit={(event) => {
          event.preventDefault()
          void ask(question.trim())
        }}
      >
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
