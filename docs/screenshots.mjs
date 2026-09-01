// Drives the deployed app in a real browser and captures the README
// screenshots, so they can be regenerated instead of going stale.
//
//   npm i playwright && npx playwright install chromium
//   node docs/screenshots.mjs
//
// Playwright is deliberately not a project dependency — it is only needed to
// refresh the images.

import { chromium } from 'playwright'
import { mkdirSync } from 'node:fs'

const SITE = process.env.SITE ?? 'https://arabic-doc-qa.vercel.app'
const PDF = 'C:/Users/DELL/Desktop/arabic-doc-qa/data/uploads/riyadh-ar-wikipedia.pdf'
const OUT = process.env.OUT ?? './out'
mkdirSync(OUT, { recursive: true })

const log = (...a) => console.log('  ', ...a)

const browser = await chromium.launch()
const page = await browser.newPage({
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 2,
})

log('opening', SITE)
await page.goto(SITE, { waitUntil: 'networkidle' })
await page.waitForSelector('.dropzone', { timeout: 30000 })
await page.screenshot({ path: `${OUT}/01-upload.png` })
log('shot 1: upload screen')

log('uploading PDF (indexing takes ~10s)…')
await page.setInputFiles('input[type=file]', PDF)
await page.waitForSelector('.panes', { timeout: 180000 })
await page.waitForSelector('.react-pdf__Page canvas', { timeout: 120000 })
await page.waitForTimeout(1500)
await page.screenshot({ path: `${OUT}/02-workspace.png` })
log('shot 2: workspace with PDF rendered')

log('asking an Arabic question…')
await page.fill('.composer__input', 'ما هي أشهر معالم مدينة الرياض؟')
await page.click('.composer__send')
await page.waitForSelector('.sources', { timeout: 120000 })
await page.waitForTimeout(1200)
await page.screenshot({ path: `${OUT}/03-arabic-answer.png` })
log('shot 3: Arabic answer with citations')

log('clicking the citation…')
await page.click('.source')
await page.waitForTimeout(2500)
await page.screenshot({ path: `${OUT}/04-citation-open.png` })
log('shot 4: cited page opened in the viewer')

log('asking an English question…')
await page.fill('.composer__input', 'What is the climate of Riyadh like?')
await page.click('.composer__send')
await page.waitForFunction(() => document.querySelectorAll('.turn--assistant').length >= 2, {
  timeout: 120000,
})
await page.waitForTimeout(1200)
await page.screenshot({ path: `${OUT}/05-english-answer.png` })
log('shot 5: English answer from the Arabic document')

log('switching to dark theme…')
await page.click('.masthead .iconbutton')
await page.waitForTimeout(900)
await page.screenshot({ path: `${OUT}/06-dark.png` })
log('shot 6: dark theme')

await browser.close()
console.log('done')
