# Shamela Full Collection Reference

The owner exported 2,519 books from the Shamela desktop app (v4) in March 2026. This is a large subset of the Shamela desktop library, which contains thousands more books.

**Location:** https://drive.google.com/file/d/1LrQkHjzbXaxR3JUQaemiXTC6GiIOGAje/view?usp=sharing
**Format:** ZIP file, 1.3 GB compressed, ~6 GB uncompressed
**Structure:** All books in a single flat directory called "تصدير من الشاملة"
**Contents:** 1,932 single-file books (.htm) + 587 multi-volume directories (001.htm, 002.htm, ...)

## What's in the repo vs. what's in the exports

**In the repo** (`tests/fixtures/shamela_real/`): 13 selected fixtures covering key variation axes.
**In the exports** (Google Drive): All 2,519 exported books for broader testing when needed.

## How to re-download

```bash
wget --no-check-certificate "https://drive.usercontent.google.com/download?id=1LrQkHjzbXaxR3JUQaemiXTC6GiIOGAje&export=download&confirm=t" -O shamela_exports.zip
```

## Structural analysis

`reference/SHAMELA_FORMAT_ANALYSIS.md` contains the complete structural specification derived from surveying all 2,519 exports.
