# Inspection report from a Field Capture ZIP

Prompt to paste into your AI assistant, with the capture ZIP attached.

## Fill in before sending

| Field | Value | If empty |
|---|---|---|
| Checklists | e.g. Inspectare PSV + OVID DP Operations | checklists recorded in the ZIP |
| Inspector | SURNAME First name | value recorded in the ZIP |
| Synergi tag | e.g. TEPA DP NAV-DP1 | TEPA DP NAV-DP1 |

---

## Prompt

You are assisting a marine superintendent / vessel inspector.

The attached ZIP was exported by the Field Capture app (https://yotolame.github.io/inspections/capture.html). It contains:

- `inspection.json`: vessel, date, location, inspector, checklist(s) selected, and the field observations (dictated note + photo file names).
- `photos/`: the photos of each observation.
- `audio/`: voice memos. Do not use them.

### Goal

Produce **one self-contained HTML review file**. For each requested checklist it shows the complete list of questions, with the ZIP observations rewritten and placed under the right question, photos included. The inspector then ticks YES / NO / N/A himself, edits or adds comments, and exports a PDF (one per checklist) and a Synergi Excel file (all NO answers).

### Step 0 - Get the checklist templates and the tools from GitHub

- Everything is in one repository: https://github.com/YOTOLAME/inspections
  - checklist templates (Inspectare and OVID forms): `*-MOBILE.html` files at the root
  - report tools: folder `tools` (`build_checklists.py`, `build_review.py`, `review_template.html`)
  - download as archive: https://github.com/YOTOLAME/inspections/archive/refs/heads/main.zip
- If you can run code with internet access: `git clone --depth 1 https://github.com/YOTOLAME/inspections` (or download the archive and unzip it).
- If you can run code but have no internet access: ask the user to download the archive link above and attach it, then unzip it.
- If you cannot run Python at all: say so in one line and stop. Do not try to write the HTML by hand.

Checklist names and template files (root of the repository):

| Checklist | Template file |
|---|---|
| Inspectare PSV | `INSPECTARE-PSV-MOBILE.html` |
| Inspectare AHTS | `INSPECTARE-AHTS-MOBILE.html` |
| Inspectare TUG | `INSPECTARE-TUG-MOBILE.html` |
| Inspectare Crew Boat | `INSPECTARE-CREWBOAT-MOBILE.html` |
| Inspectare 500m Zone Vessel | `INSPECTARE-500M-MOBILE.html` |
| Inspectare 500m Zone Asset | `INSPECTARE-500M-ASSET-MOBILE.html` |
| OVID Common 1/4 to 4/4 | `OVID-COMMON-PART1-MOBILE.html` ... `OVID-COMMON-PART4-MOBILE.html` |
| OVID PSV Operations | `OVID-PSV-OPERATIONS-MOBILE.html` |
| OVID AHTS/TUG Operations | `OVID-AHTS-TUG-OPERATIONS-MOBILE.html` |
| OVID MPSV Operations | `OVID-MPSV-OPERATIONS-MOBILE.html` |
| OVID DP Operations (Ch.15) | `OVID-DP-OPERATIONS-MOBILE.html` |
| OVID Crew Transfer Vessel 1/2, 2/2 | `OVID-CREWBOAT-PART1-MOBILE.html`, `OVID-CREWBOAT-PART2-MOBILE.html` |
| OVID Barge | `OVID-BARGE-OPERATIONS-MOBILE.html` |

Extract the questions of all checklists (`<repo>` = the repository folder, e.g. `inspections` or `inspections-main`):

```
python3 -I <repo>/tools/build_checklists.py <repo> checklists.json
```

### Step 1 - Read everything

- Read `inspection.json` completely.
- Open and look at **every** photo, not only the first one of each observation.
- Read the questions of each requested checklist in `checklists.json`.

### Step 2 - Rework each observation

1. **Dictated note**: it may be badly transcribed (homophones, distorted maritime terms, French / English / Portuguese mix, no punctuation). Correct it only when the meaning is obvious from the context or the photo. Otherwise keep the literal meaning and flag it in `remark`.
2. **Photo**: identify the object, the location (visible clues: name plates, markings, signage, deck or room features), the defect, and any readable text (maker plate, inspection date, label). Use the photo to make the comment more precise, never to add a defect that is neither in the note nor clearly visible. If the photo contradicts the note, is blurred, or does not show the defect, say so in `remark`.
3. **`comment`**: English, past tense, factual, OVID style.
   - Structure: location + object + defect observed. One or two short sentences.
   - Wording: "was found ...", "were found ...", "was not sighted", "was observed".
   - No judgement of acceptability, no recommendation, no person names, no "I" or "we".
   - Examples: "The aft starboard liquid bulk manifold was not clearly labelled and the manifold valves were found corroded." / "The CCTV recording computer located on the bridge was found not operational."
4. **Question**: in **each** requested checklist, choose the question whose subject best covers the defect. The same observation may be placed in several checklists when a question fits. Never force a match: if no question fits in any checklist, put the observation in `unassigned` with the reason. One observation containing two distinct defects may give two items with the same `obs` number.
5. **`subject`**: a 3 to 6 word title in Title Case, e.g. "Liquid Bulk Manifold Condition".
6. **`action`**: one sentence "CTR to ... and provide evidence."
7. **`remark`**: empty, or a short note to the inspector (dictation doubt, weak match with the question, photo not showing the defect...).
8. **`photos`**: numbers (1, 2...) of the observation photos showing the defect; omit = all photos.

Rules:

- Never answer YES / NO / N/A: the inspector does it.
- Never invent a fact, a figure or a reference.
- OVID (OCIMF OVIQ4) and Inspectare (TEPA checklists) are different: do not mix their names.

### Step 3 - Build the HTML

Write `mapping.json`:

```json
{
  "inspector": "SURNAME First name",
  "synergiTag": "TEPA DP NAV-DP1",
  "templates": ["INSPECTARE-PSV-MOBILE.html", "OVID-DP-OPERATIONS-MOBILE.html"],
  "items": [
    {"obs": 1, "form": "INSPECTARE-PSV-MOBILE.html", "q": "12.41",
     "comment": "...", "subject": "...", "action": "CTR to ... and provide evidence.",
     "remark": "", "photos": [1]}
  ],
  "unassigned": [{"obs": 4, "reason": "..."}]
}
```

Run:

```
python3 -I <repo>/tools/build_review.py CAPTURE.zip mapping.json <repo> .
```

The file is named automatically: `YYYY MM DD <Vessel> <Inspection type> <Initials>.html` (e.g. `2026 09 13 MAMOLA RELIANCE Inspectare PSV + OVID DP Ops LP.html`). The script rejects an unknown checklist or question, a forgotten observation and empty fields: fix `mapping.json` and run again until it prints `OK`.

### Step 4 - Check

- Every observation of the ZIP is placed or listed in `unassigned`.
- Re-read each comment against the note and the photos: nothing invented, English, past tense, no judgement.
- File size below 15 MB.

### Step 5 - Deliver

- Give the HTML file for download.
- In the answer, a short table: Obs | Checklist | Question | Comment | Remark. Then the observations not placed. Nothing else.
- Then repeat the user guide below in one short paragraph.

## User guide for the HTML review file

- PC: open the file in Chrome or Edge (double-click). Entries are saved automatically in the browser.
- Phone or tablet: save the file (iPhone: in Files), open https://yotolame.github.io/inspections/review.html, press "Open report file" and choose it. The file is read on the device only; nothing is sent to any server.
- Choose the checklist at the top. The filter "Pre-filled / commented" shows only the questions to review.
- Under each question, the raw field note is shown above the rewritten comment, to fix any dictation error.
- Tick YES / NO / N/A, edit the comment, the Synergi subject and the CTR action, remove or add photos.
- Observation not placed: type a question number and press "Move to this checklist question".
- "Export PDF" exports the checklist on screen. "Export Excel (Synergi)" exports all NO answers of all checklists.
- File names follow: YYYY MM DD Vessel Inspection type Initials (e.g. "2026 09 13 MAMOLA RELIANCE Inspectare PSV LP.pdf").
