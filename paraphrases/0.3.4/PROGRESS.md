# ABLE 0.3.4 rewrite progress

Source: `comparison/bsb.txt` (Berean Standard Bible).

Finish all Psalms first. Then finish each remaining book in ascending chapter count. For equal chapter counts, use canonical Bible order. Within each book, use chapter order.

After completing and checking each book, make one commit in GitHub Desktop. Do not reverse or rewrite earlier commits. If committing is unavailable, leave the files uncommitted.

Keep the `0.3.3/<book>/<book><chapter>_<timestamp>.md` layout under `0.3.4`. Keep verse addresses and emojis. Write directly from BSB, preserving meaning, speakers, names, numbers, conditions, prayers, and judgments. Use short sentences, active verbs, clear subjects, consistent terms, and no contractions. Explain difficult images briefly without turning them into new factual claims. Retain song headings and label musical directions separately. Keep terms with uncertain meanings rather than inventing definitions.

Apply [ASD-STE100 principles](https://www.asd-ste100.org/STE_faq.html) to Bible language. Full controlled-dictionary compliance has not been verified. Structural checks do not establish meaning fidelity or dictionary compliance; compare each rewrite with BSB during authoring.

Written and structurally checked: **723/1189 chapters; 18563/31102 source verse addresses**. Longest current sentence: 25 words.

Next: **1 Samuel 1**.

Inventory differences and output choices:

- `0.3.3` has no 2 Samuel 21–24. Added these chapters from BSB under `0.3.4` using the same filename pattern.
- Compared both Ruth 1 files. Use `ruth1_1757372779.md`, the newer filename from the same batch as Ruth 2–4. Rewrote its content directly from BSB. Both original files remain in `0.3.3`.

The local BSB has 16 reserved verse addresses with no text. Keep those verse headings and add a clearly labeled BSB source note when reaching them. Do not invent Scripture text.

Refresh and check with `python3 scripts/check_034.py --write-progress`.

| Order | Book | Source chapters | Written chapters | Chapter numbers |
| --- | --- | ---: | ---: | --- |
| 1 | Psalm | 150 | 150 | 1–150 |
| 2 | Obadiah | 1 | 1 | 1 |
| 3 | Philemon | 1 | 1 | 1 |
| 4 | 2 John | 1 | 1 | 1 |
| 5 | 3 John | 1 | 1 | 1 |
| 6 | Jude | 1 | 1 | 1 |
| 7 | Haggai | 2 | 2 | 1–2 |
| 8 | Joel | 3 | 3 | 1–3 |
| 9 | Nahum | 3 | 3 | 1–3 |
| 10 | Habakkuk | 3 | 3 | 1–3 |
| 11 | Zephaniah | 3 | 3 | 1–3 |
| 12 | 2 Thessalonians | 3 | 3 | 1–3 |
| 13 | Titus | 3 | 3 | 1–3 |
| 14 | 2 Peter | 3 | 3 | 1–3 |
| 15 | Ruth | 4 | 4 | 1–4 |
| 16 | Jonah | 4 | 4 | 1–4 |
| 17 | Malachi | 4 | 4 | 1–4 |
| 18 | Philippians | 4 | 4 | 1–4 |
| 19 | Colossians | 4 | 4 | 1–4 |
| 20 | 2 Timothy | 4 | 4 | 1–4 |
| 21 | Lamentations | 5 | 5 | 1–5 |
| 22 | 1 Thessalonians | 5 | 5 | 1–5 |
| 23 | James | 5 | 5 | 1–5 |
| 24 | 1 Peter | 5 | 5 | 1–5 |
| 25 | 1 John | 5 | 5 | 1–5 |
| 26 | Galatians | 6 | 6 | 1–6 |
| 27 | Ephesians | 6 | 6 | 1–6 |
| 28 | 1 Timothy | 6 | 6 | 1–6 |
| 29 | Micah | 7 | 7 | 1–7 |
| 30 | Song of Solomon | 8 | 8 | 1–8 |
| 31 | Amos | 9 | 9 | 1–9 |
| 32 | Ezra | 10 | 10 | 1–10 |
| 33 | Esther | 10 | 10 | 1–10 |
| 34 | Ecclesiastes | 12 | 12 | 1–12 |
| 35 | Daniel | 12 | 12 | 1–12 |
| 36 | Nehemiah | 13 | 13 | 1–13 |
| 37 | 2 Corinthians | 13 | 13 | 1–13 |
| 38 | Hebrews | 13 | 13 | 1–13 |
| 39 | Hosea | 14 | 14 | 1–14 |
| 40 | Zechariah | 14 | 14 | 1–14 |
| 41 | Mark | 16 | 16 | 1–16 |
| 42 | Romans | 16 | 16 | 1–16 |
| 43 | 1 Corinthians | 16 | 16 | 1–16 |
| 44 | Judges | 21 | 21 | 1–21 |
| 45 | John | 21 | 21 | 1–21 |
| 46 | 1 Kings | 22 | 22 | 1–22 |
| 47 | Revelation | 22 | 22 | 1–22 |
| 48 | Joshua | 24 | 24 | 1–24 |
| 49 | 2 Samuel | 24 | 24 | 1–24 |
| 50 | Luke | 24 | 24 | 1–24 |
| 51 | 2 Kings | 25 | 25 | 1–25 |
| 52 | Leviticus | 27 | 27 | 1–27 |
| 53 | Matthew | 28 | 28 | 1–28 |
| 54 | Acts | 28 | 28 | 1–28 |
| 55 | 1 Chronicles | 29 | 29 | 1–29 |
| 56 | 1 Samuel | 31 | 0 | — |
| 57 | Proverbs | 31 | 0 | — |
| 58 | Deuteronomy | 34 | 0 | — |
| 59 | Numbers | 36 | 0 | — |
| 60 | 2 Chronicles | 36 | 0 | — |
| 61 | Exodus | 40 | 0 | — |
| 62 | Job | 42 | 0 | — |
| 63 | Ezekiel | 48 | 0 | — |
| 64 | Genesis | 50 | 0 | — |
| 65 | Jeremiah | 52 | 0 | — |
| 66 | Isaiah | 66 | 0 | — |
