# ABLE 0.3.4 rewrite progress

Source: `comparison/bsb.txt` (Berean Standard Bible).

Finish all Psalms first. Then finish each remaining book in ascending chapter count. For equal chapter counts, use canonical Bible order. Within each book, use chapter order.

After completing and checking each book, make one commit in GitHub Desktop. Do not reverse or rewrite earlier commits. If committing is unavailable, leave the files uncommitted.

Keep the `0.3.3/<book>/<book><chapter>_<timestamp>.md` layout under `0.3.4`. Keep verse addresses and emojis. Write directly from BSB, preserving meaning, speakers, names, numbers, conditions, prayers, and judgments. Use short sentences, active verbs, clear subjects, consistent terms, and no contractions. Explain difficult images briefly without turning them into new factual claims. Retain song headings and label musical directions separately. Keep terms with uncertain meanings rather than inventing definitions.

Apply [ASD-STE100 principles](https://www.asd-ste100.org/STE_faq.html) to Bible language. Full controlled-dictionary compliance has not been verified. Structural checks do not establish meaning fidelity or dictionary compliance; compare each rewrite with BSB during authoring.

Written and structurally checked: **157/1189 chapters; 2597/31102 source verse addresses**. Longest current sentence: 20 words.

Next: **Joel 1**.

Inventory differences to resolve for full coverage:

- `0.3.3` has no 2 Samuel 21–24. Write these from BSB using the same filename pattern.
- `0.3.3/ruth` has two Ruth 1 files. Compare them when reaching Ruth and record the output choice.

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
| 8 | Joel | 3 | 0 | — |
| 9 | Nahum | 3 | 0 | — |
| 10 | Habakkuk | 3 | 0 | — |
| 11 | Zephaniah | 3 | 0 | — |
| 12 | 2 Thessalonians | 3 | 0 | — |
| 13 | Titus | 3 | 0 | — |
| 14 | 2 Peter | 3 | 0 | — |
| 15 | Ruth | 4 | 0 | — |
| 16 | Jonah | 4 | 0 | — |
| 17 | Malachi | 4 | 0 | — |
| 18 | Philippians | 4 | 0 | — |
| 19 | Colossians | 4 | 0 | — |
| 20 | 2 Timothy | 4 | 0 | — |
| 21 | Lamentations | 5 | 0 | — |
| 22 | 1 Thessalonians | 5 | 0 | — |
| 23 | James | 5 | 0 | — |
| 24 | 1 Peter | 5 | 0 | — |
| 25 | 1 John | 5 | 0 | — |
| 26 | Galatians | 6 | 0 | — |
| 27 | Ephesians | 6 | 0 | — |
| 28 | 1 Timothy | 6 | 0 | — |
| 29 | Micah | 7 | 0 | — |
| 30 | Song of Solomon | 8 | 0 | — |
| 31 | Amos | 9 | 0 | — |
| 32 | Ezra | 10 | 0 | — |
| 33 | Esther | 10 | 0 | — |
| 34 | Ecclesiastes | 12 | 0 | — |
| 35 | Daniel | 12 | 0 | — |
| 36 | Nehemiah | 13 | 0 | — |
| 37 | 2 Corinthians | 13 | 0 | — |
| 38 | Hebrews | 13 | 0 | — |
| 39 | Hosea | 14 | 0 | — |
| 40 | Zechariah | 14 | 0 | — |
| 41 | Mark | 16 | 0 | — |
| 42 | Romans | 16 | 0 | — |
| 43 | 1 Corinthians | 16 | 0 | — |
| 44 | Judges | 21 | 0 | — |
| 45 | John | 21 | 0 | — |
| 46 | 1 Kings | 22 | 0 | — |
| 47 | Revelation | 22 | 0 | — |
| 48 | Joshua | 24 | 0 | — |
| 49 | 2 Samuel | 24 | 0 | — |
| 50 | Luke | 24 | 0 | — |
| 51 | 2 Kings | 25 | 0 | — |
| 52 | Leviticus | 27 | 0 | — |
| 53 | Matthew | 28 | 0 | — |
| 54 | Acts | 28 | 0 | — |
| 55 | 1 Chronicles | 29 | 0 | — |
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
