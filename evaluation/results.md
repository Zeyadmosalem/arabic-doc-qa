# Evaluation results

Document: `data/uploads/riyadh-ar-wikipedia.pdf` — 12 pages, 41 chunks.

**7/10 correct.** A question passes only if the answer contains the expected fact, cites the page that fact is on, and is written in the language it was asked in.

| # | Lang | Question | Expected | Fact | Page | Lang | Cited | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ar-1 | ar | متى تأسست مدينة الرياض؟ | 1746 on p.1 | yes | yes | yes | [1] | 1.61s |
| ar-2 | ar | كم بلغ عدد سكان الرياض في إحصاء 2022؟ | 7009120 on p.2 | yes | yes | yes | [2] | 1.61s |
| ar-3 | ar | ما هو الرمز البريدي لمدينة الرياض؟ | 11461 on p.2 | yes | yes | yes | [2] | 1.64s |
| ar-4 | ar | ما هو ارتفاع مدينة الرياض عن سطح البحر بالمتر؟ | 612 on p.2 | no | no | yes | [4] | 1.47s |
| ar-5 | ar | كم عدد الفنادق في مدينة الرياض؟ | declines to answer | yes | yes | no | [11, 7, 6] | 3.46s |
| en-1 | en | When was the city of Riyadh founded? | 1746 on p.1 | yes | yes | yes | [1] | 10.44s |
| en-2 | en | What was the population of Riyadh in the 2022 census? | 7009120 on p.2 | yes | no | yes | [7] | 15.91s |
| en-3 | en | What is the postal code of Riyadh? | 11461 on p.2 | yes | yes | yes | [2] | 13.87s |
| en-4 | en | How many government universities are there in Riyadh? | 5 on p.7 | yes | yes | yes | [7] | 14.16s |
| en-5 | en | How many hospitals are there in Riyadh? | declines to answer | yes | yes | yes | [6] | 11.74s |

## Answers

**ar-1** — متى تأسست مدينة الرياض؟

> تأسست مدينة الرياض في عام 1746 (p. 1).

**ar-2** — كم بلغ عدد سكان الرياض في إحصاء 2022؟

> بلغ عدد سكان مدينة الرياض 7,009,120 نسمة وفق إحصاء 2022 (p. 2).

**ar-3** — ما هو الرمز البريدي لمدينة الرياض؟

> الرمز البريدي لمدينة الرياض هو 11461 (p. 2).

**ar-4** — ما هو ارتفاع مدينة الرياض عن سطح البحر بالمتر؟

> تقع مدينة الرياض على هضبة رسوبية يبلغ ارتفاعها نحو 600 متر فوق مستوى سطح البحر (p. 4).

**ar-5** — كم عدد الفنادق في مدينة الرياض؟

> The provided context does not state the number of hotels in Riyadh.

**en-1** — When was the city of Riyadh founded?

> The city of Riyadh was founded in 1746 (p. 1).

**en-2** — What was the population of Riyadh in the 2022 census?

> According to the 2022 Saudi census, the population of Riyadh was 7,009,120 people (p. 7).

**en-3** — What is the postal code of Riyadh?

> The postal code of Riyadh is 11461 (p. 2).

**en-4** — How many government universities are there in Riyadh?

> According to the document, there are 5 government universities in Riyadh (p. 7).

**en-5** — How many hospitals are there in Riyadh?

> The provided context does not state the total number of hospitals in Riyadh, only listing specific examples such as King Faisal Specialist Hospital and King Khalid University Hospital (p. 6).

