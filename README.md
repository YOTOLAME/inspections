# Inspections - TEPA Marine

Offline inspection tools for vessels (DT/LOG-NAV).

## Web app
- Forms and Field Capture: https://yotolame.github.io/inspections/
- Field Capture (photos + dictated notes, ZIP export): https://yotolame.github.io/inspections/capture.html
- Open a report (Review file) on phone, tablet or PC: https://yotolame.github.io/inspections/review.html

Open once with network in Safari (iPhone) or Chrome (Android) and reload twice: everything then works offline.

## Checklists
- Inspectare (TEPA): 500m Zone Vessel, 500m Zone Asset, PSV, AHTS, TUG, Crew Boat
- OVID (OCIMF OVIQ4): Common 1/4 to 4/4, PSV / AHTS-TUG / MPSV / DP Operations, Crew Transfer Vessel 1/2 and 2/2, Barge

## Report from a capture ZIP
- Prompt for your AI assistant: [tools/PROMPT_REPORT_EN.md](tools/PROMPT_REPORT_EN.md)
- Tools: `tools/build_checklists.py`, `tools/build_review.py`, `tools/review_template.html`
- `report_kit.py`: self-contained kit (builder + template + all checklists), added to every capture ZIP. Regenerate after any change to a form or a tool: `python3 -I tools/make_kit.py .`
- Result: one HTML review file (default N/A, OVID / Inspectare linked questions, one finding per observation, editable comments, photos) with PDF export per checklist and Synergi Excel export (DP Inspection FU format).
