import { useState } from "react"
import type { UploadedDocument } from "./api"
import ChatScreen from "./components/ChatScreen"
import UploadScreen from "./components/UploadScreen"

export default function App() {
  const [uploaded, setUploaded] = useState<UploadedDocument | null>(null)

  return (
    <div className="app">
      <header className="masthead">
        <h1>Arabic Doc Q&amp;A</h1>
        <p className="muted">
          Ask a PDF in Arabic or English. Every answer cites the page it came from.
        </p>
      </header>

      <main>
        {uploaded ? (
          <ChatScreen document={uploaded} onChangeDocument={() => setUploaded(null)} />
        ) : (
          <UploadScreen onUploaded={setUploaded} />
        )}
      </main>
    </div>
  )
}
