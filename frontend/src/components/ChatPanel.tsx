import { useEffect, useRef, useState } from "react"
import { ArrowUpRight, Check, Copy, CornerDownLeft, Sparkles } from "lucide-react"
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
            <span className="starters__mark">
              <Sparkles size={18} strokeWidth={1.75} />
            </span>
            <p className="starters__lead">Ask in Arabic or English</p>
            <p className="muted">Every answer cites the page it came from.</p>
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
          <article key={message.id} className={`turn turn--${message.role}`}>
            <div className="bubble">
              <p dir={directionOf(message.text)} className="bubble__text">
                {message.text}
              </p>

              {message.citations && message.citations.length > 0 && (
                <div className="sources">
                  <span className="sources__label">
                    Source{message.citations.length > 1 ? "s" : ""}
                  </span>
                  {message.citations.map((citation) => (
                    <button
                      key={citation.page}
                      className="source"
                      onClick={() => onCitationClick(citation.page)}
                      title={`Open page ${citation.page}`}
                    >
                      <span className="source__page">p. {citation.page}</span>
                      <span dir={directionOf(citation.snippet)} className="source__snippet">
                        {citation.snippet}
                      </span>
                      <ArrowUpRight className="source__go" size={14} strokeWidth={2} />
                    </button>
                  ))}
                </div>
              )}
            </div>

            {message.role === "assistant" && (
              <button className="linkbutton" onClick={() => void copy(message)}>
                {copied === message.id ? (
                  <>
                    <Check size={13} strokeWidth={2} /> Copied
                  </>
                ) : (
                  <>
                    <Copy size={13} strokeWidth={2} /> Copy
                  </>
                )}
              </button>
            )}
          </article>
        ))}

        {busy && (
          <article className="turn turn--assistant">
            <div className="bubble">
              <span className="typing" aria-label="Searching the document">
                <i />
                <i />
                <i />
              </span>
            </div>
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
        <button
          className="composer__send"
          type="submit"
          disabled={busy || !question.trim()}
          aria-label="Ask"
        >
          <CornerDownLeft size={17} strokeWidth={2} />
        </button>
      </form>
    </section>
  )
}
