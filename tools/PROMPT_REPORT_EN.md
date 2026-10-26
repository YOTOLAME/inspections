# Inspection report from a Field Capture ZIP

Prompt to paste into your AI assistant, with the capture ZIP attached.
If your AI does not open ZIP files: unzip it and attach the files themselves (`inspection.json`, `report_kit.py` and all photos; photos can be sent in several messages).

## Fill in before sending

| Field | Value | If empty |
|---|---|---|
| Checklists | e.g. Inspectare PSV + OVID DP Operations (one or several) | the AI asks you |
| Inspector | SURNAME First name | value recorded in the ZIP |
| Synergi tag | e.g. TEPA DP NAV-DP1 | TEPA DP NAV-DP1 |

---

## Prompt

You are assisting a marine superintendent / vessel inspector.

The attached files were exported by the Field Capture app (https://yotolame.github.io/inspections/capture.html), as one ZIP or as its unzipped files:

- `inspection.json`: vessel, date, location, inspector, checklist(s) selected, and the field observations (dictated note + photo file names).
- `photos/` (or loose `obsNN_N.jpg` files): the photos of each observation.
- `report_kit.py`: self-contained tool with all checklist templates and the report builder. **No internet or GitHub access is needed.**
- `inspection_details.txt`, `AI_PROMPT.md`: for information.
- `audio/`: voice memos. Do not use them.

**Check that you have every photo listed in `inspection.json`.** If the user sends the photos in several messages, list the missing ones and wait until all are received before building.

### Goal

Produce **one self-contained HTML review file per requested checklist**. Each file shows the complete list of questions of its checklist, with the ZIP observations rewritten and placed under the right question, photos included. The inspector then ticks YES / NO / N/A himself, edits or adds comments, and exports the PDF and the Synergi Excel file (NO answers) of that checklist.

### First: ask which checklists

If the "Checklists" field above is empty, **ask the user first, before any other work**: "Which inspection template(s) do you want the report on? You can choose several." Show the list of checklist names below (and the checklists recorded in `inspection.json` as a suggestion). Wait for the answer. The same ZIP can be used for several checklists: one HTML file will be produced for each.

### Step 0 - Tools

- Normal case: use `report_kit.py` from the attachments. Put all attached files (unzipped) in one working folder; photos may be loose, without the `photos/` folder.
- If `report_kit.py` is missing (old export): get the same tools from GitHub, https://github.com/YOTOLAME/inspections (archive: https://github.com/YOTOLAME/inspections/archive/refs/heads/main.zip, tools in folder `tools`). If you cannot download, ask the user to attach that archive.
- If you cannot run Python at all: say so in one line and stop. Do not try to write the HTML by hand.

Checklist names and template files:

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

Read the questions of the requested checklists:

```
python3 -I report_kit.py --questions INSPECTARE-PSV-MOBILE.html OVID-DP-OPERATIONS-MOBILE.html
```

### Step 1 - Read everything

- Read `inspection.json` completely.
- Open and look at **every** photo, not only the first one of each observation.
- Read all the questions of each requested checklist (output of `--questions`).

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

- Everything you write is in **English**: `comment`, `subject`, `action`, `remark` and the summary table, even when the field notes are in French or Portuguese (translate them).
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
python3 -I report_kit.py <ZIP file or working folder> mapping.json out
```

The script writes **one HTML file per checklist** in the folder `out`, named automatically `YYYY MM DD <Vessel> <Inspection type> <Initials>.html` (e.g. `2026 09 13 MAMOLA RELIANCE Inspectare PSV LP.html` and `2026 09 13 MAMOLA RELIANCE OVID DP Ops LP.html`). The script rejects an unknown checklist or question, a forgotten observation and empty fields: fix `mapping.json` and run again until it prints `OK`.

### Step 4 - Check

- Every observation of the ZIP is placed or listed in `unassigned`.
- Re-read each comment against the note and the photos: nothing invented, English, past tense, no judgement.
- File size below 15 MB.

### Step 5 - Deliver

- Give every HTML file for download (one per checklist).
- In the answer, a short table: Obs | Checklist | Question | Comment | Remark. Then the observations not placed. Nothing else.
- Then repeat the user guide below in one short paragraph.

## User guide for the HTML review file

- PC: open the file in Chrome or Edge (double-click). Entries are saved automatically in the browser.
- Phone or tablet: save the file (iPhone: in Files), open https://yotolame.github.io/inspections/review.html, press "Open report file" and choose it. The file is read on the device only; nothing is sent to any server.
- One file per checklist. The filter "Pre-filled / commented" shows only the questions to review.
- Under each question, the raw field note is shown above the rewritten comment, to fix any dictation error.
- Tick YES / NO / N/A, edit the comment, the Synergi subject and the CTR action, remove or add photos.
- Observation not placed: type a question number and press "Move to this checklist question".
- "Export PDF" exports the checklist. "Export Excel (Synergi)" exports its NO answers.
- File names follow: YYYY MM DD Vessel Inspection type Initials (e.g. "2026 09 13 MAMOLA RELIANCE Inspectare PSV LP.pdf").
