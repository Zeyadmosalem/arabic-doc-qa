import { useState } from "react"
import type { UploadedDocument } from "./api"
import UploadScreen from "./components/UploadScreen"
import Workspace from "./components/Workspace"
import { useTheme } from "./theme"

interface Loaded {
  document: UploadedDocument
  file: File
}

export default function App() {
  const [loaded, setLoaded] = useState<Loaded | null>(null)
  const { theme, toggle } = useTheme()

  return (
    <div className={`app${loaded ? " app--wide" : ""}`}>
      <header className="masthead">
        <div>
          <h1>Arabic Doc Q&amp;A</h1>
          <p className="muted">
            Ask a PDF in Arabic or English. Every answer cites the page it came from.
          </p>
        </div>
        <button
          className="iconbutton"
          onClick={toggle}
          aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
          title={theme === "dark" ? "Light theme" : "Dark theme"}
        >
          {theme === "dark" ? "☀" : "☾"}
        </button>
      </header>

      <main>
        {loaded ? (
          <Workspace
            document={loaded.document}
            file={loaded.file}
            onChangeDocument={() => setLoaded(null)}
          />
        ) : (
          <UploadScreen onUploaded={(document, file) => setLoaded({ document, file })} />
        )}
      </main>
    </div>
  )
}
