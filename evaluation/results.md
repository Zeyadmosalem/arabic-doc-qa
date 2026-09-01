# Evaluation results

Document: `data/uploads/riyadh-ar-wikipedia.pdf` — 12 pages, 41 chunks.

**10/10 correct.** A question passes only if the answer contains the expected fact, cites the page that fact is on, and is written in the language it was asked in.

| # | Lang | Question | Expected | Fact | Page | Lang | Cited | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ar-1 | ar | متى تأسست مدينة الرياض؟ | 1746 on p.1 | yes | yes | yes | [1] | 1.82s |
| ar-2 | ar | كم بلغ عدد سكان الرياض في إحصاء 2022؟ | 7009120 on p.2 | yes | yes | yes | [2] | 1.94s |
| ar-3 | ar | ما هو الرمز البريدي لمدينة الرياض؟ | 11461 on p.2 | yes | yes | yes | [2] | 1.64s |
| ar-4 | ar | ما هو ارتفاع مدينة الرياض عن سطح البحر بالمتر؟ | 612 on p.2 | yes | yes | yes | [2] | 2.01s |
| ar-5 | ar | كم عدد الفنادق في مدينة الرياض؟ | declines to answer | yes | yes | yes | [11] | 3.88s |
| en-1 | en | When was the city of Riyadh founded? | 1746 on p.1 | yes | yes | yes | [1] | 11.63s |
| en-2 | en | What was the population of Riyadh in the 2022 census? | 7009120 on p.2 | yes | yes | yes | [2] | 17.03s |
| en-3 | en | What is the postal code of Riyadh? | 11461 on p.2 | yes | yes | yes | [2] | 13.01s |
| en-4 | en | How many government universities are there in Riyadh? | 5 on p.7 | yes | yes | yes | [7] | 15.07s |
| en-5 | en | How many hospitals are there in Riyadh? | declines to answer | yes | yes | yes | [6] | 13.55s |

## Answers

**ar-1** — متى تأسست مدينة الرياض؟

> تأسست مدينة الرياض في عام 1746 (p. 1).

**ar-2** — كم بلغ عدد سكان الرياض في إحصاء 2022؟

> بلغ عدد سكان الرياض في إحصاء 2022 حوالي 7 009 120 نسمة (p. 2).

**ar-3** — ما هو الرمز البريدي لمدينة الرياض؟

> الرمز البريدي لمدينة الرياض هو 11461 (p. 2).

**ar-4** — ما هو ارتفاع مدينة الرياض عن سطح البحر بالمتر؟

> ارتفاع الرياض حوالي 600 متر فوق مستوى سطح البحر (p. 2).

**ar-5** — كم عدد الفنادق في مدينة الرياض؟

> المستند لا يذكر عدد الفنادق في مدينة الرياض (p. 11).

**en-1** — When was the city of Riyadh founded?

> Riyadh was founded in 1746 (p. 1).

**en-2** — What was the population of Riyadh in the 2022 census?

> The 2022 census recorded Riyadh’s population as 7,009,120 people (p. 2).

**en-3** — What is the postal code of Riyadh?

> The postal code of Riyadh is 11461 (p. 2).

**en-4** — How many government universities are there in Riyadh?

> There are five government universities in Riyadh (p. 7).

**en-5** — How many hospitals are there in Riyadh?

> The provided context does not give a specific number of hospitals in Riyadh (p. 6).

