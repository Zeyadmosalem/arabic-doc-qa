export interface Citation {
  page: number
  snippet: string
}

export interface Answer {
  text: string
  citations: Citation[]
}

export interface UploadedDocument {
  document_id: string
  filename: string
  pages: number
  chunks: number
}

export interface UploadProgress {
  /** "sending" while bytes are in flight, "indexing" once the server has them. */
  phase: "sending" | "indexing"
  percent: number
}

const BASE_URL = (import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "")

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

/** Prefer FastAPI's own "detail" message; fall back to the status code. */
function messageFrom(body: unknown, status: number): string {
  const detail = (body as { detail?: unknown } | null)?.detail
  return typeof detail === "string" ? detail : `The server returned ${status}.`
}

/**
 * Upload over XHR rather than fetch, because only XHR reports upload progress.
 * Transfer is the fast half; indexing on the server is the slow half, so the
 * phase flips once the bytes have landed.
 */
export function uploadDocument(
  file: File,
  onProgress?: (progress: UploadProgress) => void,
): Promise<UploadedDocument> {
  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest()
    request.open("POST", `${BASE_URL}/upload`)
    request.responseType = "json"

    request.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable) {
        const percent = Math.round((event.loaded / event.total) * 100)
        onProgress?.({ phase: percent < 100 ? "sending" : "indexing", percent })
      }
    })
    request.upload.addEventListener("load", () =>
      onProgress?.({ phase: "indexing", percent: 100 }),
    )

    request.addEventListener("load", () => {
      if (request.status >= 200 && request.status < 300) {
        resolve(request.response as UploadedDocument)
      } else {
        reject(new ApiError(messageFrom(request.response, request.status), request.status))
      }
    })
    request.addEventListener("error", () =>
      reject(new ApiError("Could not reach the server. Is the backend running?", 0)),
    )

    const body = new FormData()
    body.append("file", file)
    request.send(body)
  })
}

export async function askQuestion(question: string, documentId: string): Promise<Answer> {
  const response = await fetch(`${BASE_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, document_id: documentId }),
  })
  if (!response.ok) {
    let body: unknown = null
    try {
      body = await response.json()
    } catch {
      // No JSON body — messageFrom falls back to the status code.
    }
    throw new ApiError(messageFrom(body, response.status), response.status)
  }
  return response.json()
}
