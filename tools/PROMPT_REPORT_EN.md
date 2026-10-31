# Inspection report from a Field Capture ZIP

Prompt to paste into your AI assistant, with the capture ZIP attached.
If your AI does not open ZIP files: unzip it and attach the files themselves (`inspection.json`, `report_kit.py` and all photos; photos can be sent in several messages).

## Fill in before sending

| Field | Value | If empty |
|---|---|---|
| Checklists | e.g. Inspectare PSV + OVID Common 1/4 to 4/4 + OVID PSV Operations | the AI asks you |
| Inspector | SURNAME First name | value recorded in the ZIP |
| Synergi tag | e.g. TEPA NAVAL2 | TEPA NAVAL2 for marine inspections, TEPA DP NAV-DP1 for DP / 500m zone checklists |

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

Produce **one single self-contained HTML review file containing all the requested checklists** (selector at the top of the page). The inspector reviews and corrects everything **once**:

- Every question of every checklist is listed, with the ZIP observations rewritten and placed under the right question, photos included.
- **One finding per observation**: several observations may share a question, but each observation keeps its own comment, Synergi subject and CTR action (shown as "Finding 1 - Obs N", "Finding 2 - Obs N"... under the question) and gives its own line in the Synergi Excel export. In the PDF, the question shows one single observation with all the comments.
- When the same observation(s) are placed in an OVID checklist and in an Inspectare checklist, the two questions are **linked**: any correction of the comment, Synergi subject, CTR action, finding box or photos in one is copied to the other.
- Every question is pre-answered **N/A**. Every question without a finding is pre-filled with the comment *"This item was not assessed within the scope of this inspection; no evidence was reviewed and no conclusion is drawn."*. This comment disappears automatically when the inspector clicks YES or NO.
- The inspector then sets YES / NO himself, edits the comments, and exports the PDF of each checklist and the Synergi Excel file (NO answers).

### First: ask which checklists

The user chooses the checklists; it is not always the same vessel type. If the "Checklists" field above is empty, **ask the user first, before any other work**: "Which inspection template(s) do you want the report on? You can choose several." Show the list of checklist names below, the checklists recorded in `inspection.json` as a suggestion, and the suggested OVID / Inspectare counterpart of each (table below). Wait for the answer. Never add a checklist the user did not choose.

### Step 0 - Tools

- Normal case: use `report_kit.py` from the attachments. Put all attached files (unzipped) in one working folder; photos may be loose, without the `photos/` folder.
- Check the kit version: `python3 -I report_kit.py --version` must print a version dated 2026-10-31 or later.
- If `report_kit.py` is missing or `--version` fails (old export): get the current `report_kit.py` from GitHub, https://github.com/YOTOLAME/inspections (file `report_kit.py` at the root; archive: https://github.com/YOTOLAME/inspections/archive/refs/heads/main.zip). If you cannot download, ask the user to attach that file.
- If you cannot run Python at all: say so in one line and stop. Do not try to write the HTML by hand.

Checklist names, template files and suggested counterparts:

| Checklist | Template file | Suggested counterpart (other framework) |
|---|---|---|
| Inspectare PSV | `INSPECTARE-PSV-MOBILE.html` | OVID Common 1/4 to 4/4 + OVID PSV Operations |
| Inspectare AHTS | `INSPECTARE-AHTS-MOBILE.html` | OVID Common 1/4 to 4/4 + OVID AHTS/TUG Operations |
| Inspectare TUG | `INSPECTARE-TUG-MOBILE.html` | OVID Common 1/4 to 4/4 + OVID AHTS/TUG Operations |
| Inspectare Crew Boat | `INSPECTARE-CREWBOAT-MOBILE.html` | OVID Crew Transfer Vessel 1/2, 2/2 |
| Inspectare 500m Zone Vessel | `INSPECTARE-500M-MOBILE.html` | OVID DP Operations (Ch.15) |
| Inspectare 500m Zone Asset | `INSPECTARE-500M-ASSET-MOBILE.html` | none |
| OVID Common 1/4 to 4/4 | `OVID-COMMON-PART1-MOBILE.html` ... `OVID-COMMON-PART4-MOBILE.html` | Inspectare PSV, AHTS or TUG |
| OVID PSV Operations | `OVID-PSV-OPERATIONS-MOBILE.html` | Inspectare PSV |
| OVID AHTS/TUG Operations | `OVID-AHTS-TUG-OPERATIONS-MOBILE.html` | Inspectare AHTS or TUG |
| OVID MPSV Operations | `OVID-MPSV-OPERATIONS-MOBILE.html` | none |
| OVID DP Operations (Ch.15) | `OVID-DP-OPERATIONS-MOBILE.html` | Inspectare 500m Zone Vessel |
| OVID Crew Transfer Vessel 1/2, 2/2 | `OVID-CREWBOAT-PART1-MOBILE.html`, `OVID-CREWBOAT-PART2-MOBILE.html` | Inspectare Crew Boat |
| OVID Barge | `OVID-BARGE-OPERATIONS-MOBILE.html` | none |

The counterparts are suggestions only: the user decides. Linking works for any combination chosen.

Read the questions of the requested checklists:

```
python3 -I report_kit.py --questions INSPECTARE-PSV-MOBILE.html OVID-PSV-OPERATIONS-MOBILE.html
```

### Step 1 - Read everything

- Read `inspection.json` completely.
- Open and look at **every** photo, not only the first one of each observation.
- Read all the questions of each requested checklist (output of `--questions`).

### Step 2 - Rework each observation

1. **Dictated note**: it may be badly transcribed (homophones, distorted maritime terms, French / English / Portuguese mix, no punctuation). Correct it only when the meaning is obvious from the context or the photo. Otherwise keep the literal meaning and flag it in `remark`.
2. **Photo**: identify the object, the location (visible clues: name plates, markings, signage, deck or room features), the defect, and any readable text (maker plate, inspection date, label, panel display). Use the photo to make the comment more precise, never to add a defect that is neither in the note nor clearly visible. If the photo contradicts the note, is blurred, or does not show the defect, say so in `remark`.
3. **`comment`**: English, past tense, factual, OVID style.
   - Structure: location + object + defect observed. One or two short sentences.
   - Wording: "was found ...", "were found ...", "was not sighted", "was observed".
   - No judgement of acceptability, no recommendation, no person names, no "I" or "we".
   - Examples: "The aft starboard liquid bulk manifold was not clearly labelled and the manifold valves were found corroded." / "The CCTV recording computer located on the bridge was found not operational."
4. **`subject`**: a 3 to 6 word title in Title Case, e.g. "Liquid Bulk Manifold Condition".
5. **`action`**: one sentence "CTR to ... and provide evidence."
6. **`remark`**: empty, or a short note to the inspector (dictation doubt, weak match with the question, photo not showing the defect, a better alternative question...).
7. **`photos`**: numbers (1, 2...) of the observation photos showing the defect; omit = all photos.
8. If the note states no defect and the photo shows none, do not invent one: put the observation in `unassigned` with the reason.

### Step 3 - Place the observations (linked OVID / Inspectare)

Two frameworks: **OVID** (all `OVID-...` templates) and **Inspectare** (all `INSPECTARE-...` templates). They are different: never mix their names.

1. In **each framework** requested, place each observation **once only**: one question in one of the OVID checklists, and one question in one of the Inspectare checklists. Never twice in the same framework (e.g. not in OVID Common and in OVID PSV Operations): it would create a double finding in Synergi.
2. Choose the question whose subject best covers the defect. Several observations may share a question. Never force a match: if no question fits in a framework, place it only in the other one and say so in `remark`. If no question fits anywhere, put it in `unassigned` with the reason. One observation containing two distinct defects may give two items with the same `obs` number, on two different questions.
3. **Linking rule (mandatory)**: questions are linked when they hold exactly the same set of observations. So when several observations share a question in one framework, the same observations, and only them, must share one question in the other framework. If this is not possible, choose other questions (one question per observation) so that the groups are identical on both sides. A group that differs breaks the link and forces the inspector to correct twice.
4. Linked items carry **the same** `comment`, `subject`, `action` and `photos` in both frameworks (only `q`, `form` and `remark` may differ).
5. **One finding per observation**: each item keeps its own `comment`, `subject` and `action`, written for that observation only, even when several observations share a question. Never merge two observations into one comment, subject or action: `report_kit.py` turns each observation into its own finding and its own Synergi line.

Rules:

- Everything you write is in **English**: `comment`, `subject`, `action`, `remark` and the summary table, even when the field notes are in French or Portuguese (translate them).
- Never answer YES / NO / N/A in `mapping.json`: the defaults (N/A + comment "This item was not assessed within the scope of this inspection; no evidence was reviewed and no conclusion is drawn.") are set by `report_kit.py`, the inspector does the rest.
- Never invent a fact, a figure or a reference.

### Step 4 - Build the HTML

Write `mapping.json`:

```json
{
  "inspector": "SURNAME First name",
  "synergiTag": "TEPA NAVAL2",
  "templates": ["INSPECTARE-PSV-MOBILE.html", "OVID-PSV-OPERATIONS-MOBILE.html"],
  "items": [
    {"obs": 1, "form": "OVID-PSV-OPERATIONS-MOBILE.html", "q": "8.1.2",
     "comment": "...", "subject": "...", "action": "CTR to ... and provide evidence.",
     "remark": "", "photos": [1]},
    {"obs": 1, "form": "INSPECTARE-PSV-MOBILE.html", "q": "12.41",
     "comment": "...", "subject": "...", "action": "CTR to ... and provide evidence.",
     "remark": "", "photos": [1]}
  ],
  "unassigned": [{"obs": 4, "reason": "..."}]
}
```

Run:

```
python3 -I report_kit.py <ZIP file or working folder> mapping.json "out/YYYY MM DD <Vessel> <Type 1> + <Type 2> <Initials>.html"
```

- The output path **must end with `.html`**: this gives ONE file with all the checklists. Name it like `2026 10 26 ENERGY CRAFT 02 OVID CTV + Inspectare Crew Boat GC.html` (date of inspection, vessel, checklist short names joined by " + ", inspector initials).
- `report_kit.py` rejects an unknown checklist or question, a forgotten observation, empty fields, an observation placed twice in the same framework and an observation grouped differently in the two frameworks (broken link): fix `mapping.json` (Step 3) and run again until it prints `OK`.

### Step 5 - Check

- Every observation of the ZIP is placed or listed in `unassigned`.
- Each observation is placed at most once per framework, and linked groups are identical (`report_kit.py` OK).
- Each observation has its own comment, subject and action, even when it shares a question.
- Re-read each comment against the note and the photos: nothing invented, English, past tense, no judgement.
- If you can run a browser, open the file: no script error, the questions show N/A, linked questions show the blue "Linked with ..." banner, a question holding several observations shows "Finding 1 - Obs N", "Finding 2 - Obs N"...
- File size below 15 MB.

### Step 6 - Deliver

- Give the single HTML file for download.
- In the answer, a short table: Obs | OVID question | Inspectare question | Comment | Remark. Then the observations not placed. Nothing else.
- Then repeat the user guide below in one short paragraph.

## User guide for the HTML review file

- PC: open the file in Chrome or Edge (double-click). Entries are saved automatically in the browser.
- Phone or tablet: save the file (iPhone: in Files), open https://yotolame.github.io/inspections/review.html, press "Open report file" and choose it. The file is read on the device only; nothing is sent to any server.
- All checklists are in one file: switch with the selector at the top left. The filter "Pre-filled / commented" shows only the questions with findings.
- A question showing "Linked with ..." is linked to the same finding in the other checklist: correct it once, the twin is updated (comment, Synergi subject, CTR action, finding box, photos). YES / NO / N/A answers are not copied: set them in each checklist.
- Every question without a finding starts at N/A with the comment "This item was not assessed within the scope of this inspection; no evidence was reviewed and no conclusion is drawn." Clicking YES or NO removes that comment (only if it was not modified). Questions with a finding start at N/A with the rewritten comment.
- Under each question, the raw field note is shown above the rewritten comment, to fix any dictation error.
- A question holding several observations shows one finding per observation ("Finding 1 - Obs N", "Finding 2 - Obs N"...), each with its own comment, Synergi subject and CTR action. Answered NO, it gives one Synergi line per finding. In the PDF, the question shows one single observation with all the comments.
- Observation not placed: type a question number and press "Move to this checklist question" (a moved observation is not linked). Moved to a question that already holds a finding, it is added as a separate finding with empty fields: fill them in.
- "Export PDF" exports the checklist shown. "Export Excel (Synergi)" exports the NO answers of all the checklists of the file: one line per finding (observation) of each question answered NO; a linked finding answered NO on both sides gives two lines.
- "Reset" goes back to the original draft (N/A everywhere, and the default comment above on every question without a finding).
- A new version of the file starts empty: entries made in a previous version are not carried over.

---

## Optional - TEPA follow-up file from the Synergi export

Use this when the user attaches the Synergi Excel export of this report and the previous TEPA Marine Inspection follow-up file (e.g. `26-2 - Marine inspection - EC-02 - Rev04.xlsx`) and asks to update the follow-up.

1. Keep the TEPA follow-up format exactly: same sheet, columns, merged cells, styles, row heights, conditional formatting (extend its ranges to the new last row), logos and header comment. Edit with openpyxl and check that the logos are still in the saved file.
2. Take the findings of the Synergi export. **OVID / Inspectare duplicates give one finding only.** Also merge two findings of the export that state the same defect, and tell the user. If one Synergi line still contains two distinct defects (old report), split it into two cases and tell the user.
3. Remove every reference to OVID or Inspectare from titles and text: no checklist name, no question number (e.g. "(Q4.1.13)").
4. A finding that is already an **open** case of the follow-up is not added again: append to that case's comments column `TEPA>DD/MM/YYYY: Still observed during inspection of DD/MM/YYYY: ...`. A finding matching a **closed** case is a new case. If you are not sure it is the same defect, add it as a new case and tell the user.
5. A Synergi line with an empty comment is not added: tell the user.
6. New case format, column "ACTION DESCRIPTION":
   ```
   > SUBJECT: TEPA Marine Inspection - YYYY MM DD - <inspector initials>
   >>Observation: <short title, sentence case>
   During the inspection, it was observed that <defect>.

   CTR is required to <action> and provide evidence.
   ```
   Comments column empty, progress empty, action deadline = inspection date + 11 days (same delay as the previous cases; tell the user), completion date empty.
7. Header: LAST VISIT = inspection date, LAST UPDATE = today, INSPECTION SEQUENCE NBR revision + 1; save as the next revision (`... Rev05.xlsx`).
8. If the user asks: remove the closed cases (progress 100 % or a completion date) and renumber the cases from 1. Tell the user to keep the previous revision, which is the only record of the closed cases.
9. Everything written in the file is in English. In the answer: a short table old case no. | new case no. | title, then the points to check.
