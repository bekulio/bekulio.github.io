# Holocene Calendar · IFC

A single-page calendar that displays today's date in a custom **Holocene + International Fixed Calendar** system, alongside its Gregorian and Hebrew equivalents.

**Live:** https://bekulio.github.io

לוח שנה הולוצני בעל 13 חודשים של 28 ימים, עם מקבילות לתאריך הגרגוריאני והעברי.

---

## Calendar rules

| Property         | Value |
|------------------|-------|
| Year offset      | Gregorian year + 10,000 (Holocene Era) |
| Months per year  | 13 |
| Days per month   | 28 (exactly 4 weeks) |
| Month order      | January, February, March, April, May, June, **Sol**, July, August, September, October, November, December |
| Year Day         | 1 intercalary day after 28 December — not part of any month or weekday |
| Leap Day         | 1 intercalary day between 28 June and 1 Sol — only in leap years |
| Leap rule        | Every 4 years (Julian-style) |
| Week start       | Sunday — every month starts on Sunday |

The new month `Sol` sits between June and July. The two intercalary days exist outside the weekly cycle, so every date in a given month always falls on the same weekday.

---

## Features

- Today's date displayed prominently in the IFC system
- Equivalent Gregorian and Hebrew dates (via `Intl.DateTimeFormat`)
- Browse by day or month with on-screen buttons or keyboard arrows
- Click any day in the month grid or any month tile to jump
- Date converter for arbitrary Gregorian dates

### Keyboard shortcuts

| Key       | Action |
|-----------|--------|
| `←` / `→` | Navigate one day |
| `↑` / `↓` | Navigate one month |
| `T` / `ה` | Return to today |

---

## Implementation

Single `index.html` file. No build step, no dependencies beyond Google Fonts (Fraunces, JetBrains Mono, Frank Ruhl Libre).

Hebrew calendar conversion uses the browser's built-in `Intl.DateTimeFormat('he-u-ca-hebrew', …)` — no external library required.

### Local preview

```
# any static file server works
python3 -m http.server 8000
# then open http://localhost:8000
```

Or just double-click `index.html`.

---

## Notes

The weekday shown by this calendar reflects the **IFC-fixed weekday** (where day-of-month deterministically maps to day-of-week), not the actual Gregorian weekday of the same calendar day. This is the central design feature of IFC, not a bug.

The Julian-style leap rule (every 4 years, no century exception) accumulates roughly 1 day of drift against the solar year every ~128 years. For a personal calendar this is irrelevant; for a multi-century project, switch to the Gregorian rule.

---

## Credits

- **International Fixed Calendar** — Moses B. Cotsworth, 1902. Used internally by Eastman Kodak from 1928 to 1989.
- **Holocene Era** — Cesare Emiliani, 1993. Year offset of +10,000 to align the start of the era with the approximate beginning of human civilization.
