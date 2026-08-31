const ARABIC_LETTERS = /[\u0600-\u06FF]/g
const LATIN_LETTERS = /[A-Za-z]/g

/**
 * Whether a string is predominantly Arabic.
 *
 * Compares script counts rather than looking for the first Arabic character,
 * so an English sentence quoting one Arabic word still reads left to right.
 */
export function isArabic(text: string): boolean {
  const arabic = text.match(ARABIC_LETTERS)?.length ?? 0
  const latin = text.match(LATIN_LETTERS)?.length ?? 0
  return arabic > latin
}

export function directionOf(text: string): "rtl" | "ltr" {
  return isArabic(text) ? "rtl" : "ltr"
}
