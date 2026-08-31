import { useState } from "react"
import { Moon, Sun } from "lucide-react"
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
        <div className="brand">
          <span className="brand__mark" aria-hidden="true">
            ع
          </span>
          <span className="brand__name">
            Arabic Doc Q&amp;A
            <small>Grounded answers with page citations</small>
          </span>
        </div>

        <button
          className="iconbutton"
          onClick={toggle}
          aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
          title={theme === "dark" ? "Light theme" : "Dark theme"}
        >
          {theme === "dark" ? (
            <Sun size={16} strokeWidth={1.75} />
          ) : (
            <Moon size={16} strokeWidth={1.75} />
          )}
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
