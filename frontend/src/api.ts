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

const BASE_URL = (import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "")

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

/** Turn a failed response into an ApiError, preferring FastAPI's "detail" message. */
async function failure(response: Response): Promise<ApiError> {
  let detail = `The server returned ${response.status}.`
  try {
    const body = await response.json()
    if (typeof body?.detail === "string") {
      detail = body.detail
    }
  } catch {
    // No JSON body — keep the status-based message.
  }
  return new ApiError(detail, response.status)
}

export async function uploadDocument(file: File): Promise<UploadedDocument> {
  const body = new FormData()
  body.append("file", file)

  const response = await fetch(`${BASE_URL}/upload`, { method: "POST", body })
  if (!response.ok) {
    throw await failure(response)
  }
  return response.json()
}

export async function askQuestion(question: string, documentId: string): Promise<Answer> {
  const response = await fetch(`${BASE_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, document_id: documentId }),
  })
  if (!response.ok) {
    throw await failure(response)
  }
  return response.json()
}
