# Pricewire Price Bot — Setup (runs every 2 weeks)

This folder contains **pricewire.html** — your laptop price site, tracking 502 laptops across MacBooks, ThinkPads, Dell, HP, ASUS, gaming, Chromebooks, rugged, and budget picks. The bot's job is to re-verify the price of **every one of the 502 laptops** on a schedule.

**Schedule: every 2 weeks**, not daily. The task must cover the full catalog of 502. If a single run can't finish all of them, it saves progress and continues where it left off — between runs, every laptop gets covered. See the prompt below.

## One-time setup (about 2 minutes)

1. Save this folder somewhere permanent on your computer, e.g. `Documents/Pricewire`.
2. Open the **Claude Desktop app** → open **Cowork**.
3. Create a **scheduled task** (in the sidebar, look for Scheduled / Routines → new task).
4. Set it to run **every 2 weeks** at a time your computer is usually awake (e.g. 8:00 AM). If the scheduler only offers daily/weekly/monthly, choose weekly and set "repeat every 2 weeks" if available, or just pick a day (e.g. every other Monday) manually. Note: local tasks only run while the desktop app is open and the computer is awake — turn on "keep computer awake" during setup, or choose a cloud/remote routine if offered so it runs even when the computer is off.
5. Point the task at this folder, and paste the instructions below as the task prompt.
6. Click **Run now** once, approve any permission prompts with "always allow", and check that pricewire.html shows today's date under "prices verified".

Open `pricewire.html` in any browser to use the site. Bookmark it.

## The task prompt (paste this)

```
You are the Pricewire price bot, running every 2 weeks. In this folder is pricewire.html.
It contains a <script id="price-data" type="application/json"> block listing laptops,
each with retailers, prices, notes, a bestIndex, a "why" sentence, and a "verified" flag.

Do the following:
1. Read the current JSON block — it has just over 500 laptops.
2. Your goal is that EVERY one of the 500+ laptops gets re-verified — none permanently
   skipped. Process them in order of most-stale first: entries with no "lastChecked"
   date come first, then oldest "lastChecked". For each laptop, search the web for
   its current price at 1-2 reputable US retailers (Amazon, Best Buy, B&H, Newegg,
   Walmart, Costco, Micro Center, Target, Adorama, or the manufacturer's store). Prefer
   the exact config in "specs". Use real prices you find — do not invent numbers. On every
   entry you successfully re-check, set "verified": true and "lastChecked" to today's
   date (e.g. "2026-07-17").
2b. SOUTH AFRICA: also search for the current ZAR price at SA retailers — Takealot,
   Evetech, Incredible Connection, Makro, Wootware, and iStore (Apple only). Add any
   you verify to the laptop's entry as a "za" array using the same retailer shape, with
   prices written like "R21 999". Only include prices you actually found — never convert
   from USD and present it as a real SA price.
3. Rewrite each entry with: updated prices, updated one-line notes (mention active sales
   or all-time lows), retailers ordered best deal first, bestIndex pointing at the best
   overall deal (price + trustworthiness + stock), and an updated "why" sentence.
4. Keep real product-page URLs where you find them; otherwise use the retailer's search
   URL for that model. Never invent URLs.
5. Set the top-level "asOf" to today's date in the format "July 15, 2026".
6. Replace ONLY the JSON inside the <script id="price-data"> tag. Do not touch any other
   part of the file. The JSON must remain valid — validate it before saving.
7. If a laptop's price genuinely can't be found this run, leave its existing price and
   note in place rather than guessing, and leave "verified" as it was.
8. This is a big catalog (500+). If you're at risk of running out of time or budget
   partway through, SAVE YOUR PROGRESS by writing the partial JSON back to the file —
   never lose completed work. Because you always process most-stale entries first, the
   next run automatically picks up exactly where this one left off, so across runs all
   502 laptops get covered with none left behind.

Finish with a short summary: how many laptops were freshly verified, which had notable
price changes (drops, all-time lows, discontinued models), and what's still pending.
```

## Managing the watchlist

To track a new laptop, tell the bot (or any Cowork chat pointed at this folder):
"Add [laptop name] to the Pricewire watchlist" — it should append a new entry to the
JSON block following the same structure. To remove one, ask it to delete that entry.

## Notes

- The site works offline from the file — no server, no accounts, no API keys.
- Searches on the site check the bot's data first; unknown laptops get direct search
  links at trusted retailers instead of stale numbers.
- 502 laptops is a lot of searching for one run. The bot always works most-stale-first
  and saves partial progress, so even if one run covers only part of the catalog, the
  next run continues from there — every laptop gets refreshed in rotation, none skipped.
  If you want faster full coverage, you can also manually trigger extra runs anytime
  with "Run now".
- If a scheduled run is missed (computer asleep), one catch-up run fires when it wakes.
- Since prices are only re-checked every 2 weeks, expect some drift on fast-moving deals
  (flash sales, doorbusters) — the site is meant for typical/current pricing, not
  minute-to-minute tracking.
