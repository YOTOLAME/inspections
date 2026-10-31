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
- Every question is pre-answered **N/A**. Every question without a finding is pre-filled with the comment *"This item was not assessed within the scope of this inspection due to time constraints; no evidence was reviewed and no conclusion is drawn."*. This comment disappears automatically when the inspector clicks YES or NO.
- The inspector then sets YES / NO himself, edits the comments, and exports the PDF of each checklist and the Synergi Excel file (NO answers).

### First: ask which checklists

The user chooses the checklists; it is not always the same vessel type. If the "Checklists" field above is empty, **ask the user first, before any other work**: "Which inspection template(s) do you want the report on? You can choose several." Show the list of checklist names below, the checklists recorded in `inspection.json` as a suggestion, and the suggested OVID / Inspectare counterpart of each (table below). Wait for the answer. Never add a checklist the user did not choose.

### Step 0 - Tools

- Normal case: use `report_kit.py` from the attachments. Put all attached files (unzipped) in one working folder; photos may be loose, without the `photos/` folder.
- If `report_kit.py` is missing (old export): get the same tools from GitHub, https://github.com/YOTOLAME/inspections (archive: https://github.com/YOTOLAME/inspections/archive/refs/heads/main.zip, tools in folder `tools`). If you cannot download, ask the user to attach that archive.
- Write the script given in the Appendix to `review_patches.py`, exactly as written, in the working folder.
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
5. **One finding per observation**: each item keeps its own `comment`, `subject` and `action`, written for that observation only, even when several observations share a question. Never merge two observations into one comment, subject or action: `review_patches.py` turns each observation into its own finding and its own Synergi line.

Rules:

- Everything you write is in **English**: `comment`, `subject`, `action`, `remark` and the summary table, even when the field notes are in French or Portuguese (translate them).
- Never answer YES / NO / N/A in `mapping.json`: the defaults (N/A + comment "This item was not assessed within the scope of this inspection due to time constraints; no evidence was reviewed and no conclusion is drawn.") are set by `review_patches.py`, the inspector does the rest.
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

Run, in this order:

```
python3 -I review_patches.py --check mapping.json
python3 -I report_kit.py <ZIP file or working folder> mapping.json "out/YYYY MM DD <Vessel> <Type 1> + <Type 2> <Initials>.html"
python3 -I review_patches.py "out/YYYY MM DD <Vessel> <Type 1> + <Type 2> <Initials>.html" mapping.json
```

- The output path **must end with `.html`**: this gives ONE file with all the checklists. Name it like `2026 10 26 ENERGY CRAFT 02 OVID CTV + Inspectare Crew Boat GC.html` (date of inspection, vessel, checklist short names joined by " + ", inspector initials).
- `--check` must print `OK links consistent`. Otherwise fix the grouping in `mapping.json` (Step 3) and run it again.
- `report_kit.py` rejects an unknown checklist or question, a forgotten observation and empty fields: fix `mapping.json` and run again until it prints `OK`.
- `review_patches.py` must print `OK patched`. If it prints `ERROR anchor not found`, `report_kit.py` has changed: deliver the file unpatched and tell the user in one line that links, defaults and separate findings per observation are missing.

### Step 5 - Check

- Every observation of the ZIP is placed or listed in `unassigned`.
- Each observation is placed at most once per framework, and linked groups are identical (`--check` OK).
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
- Every question without a finding starts at N/A with the comment "This item was not assessed within the scope of this inspection due to time constraints; no evidence was reviewed and no conclusion is drawn." Clicking YES or NO removes that comment (only if it was not modified). Questions with a finding start at N/A with the rewritten comment.
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

---

## Appendix - review_patches.py

Write this file exactly as below.

```python
#!/usr/bin/env python3
"""Post-process the review HTML built by report_kit.py.
  python3 -I review_patches.py --check mapping.json        check that linked questions group the same observations
  python3 -I review_patches.py REVIEW.html mapping.json    apply the patches in place
Patches: (1) questions holding the same observations in several checklists are linked: comment, Synergi
subject, CTR action, finding box and photos are copied to the twin; (2) every question defaults to N/A;
(3) questions without finding get the NOT_ASSESSED comment, removed when YES or NO is clicked;
(4) one finding per observation: a question holding several observations shows one comment, Synergi subject
and CTR action per observation, and gives one Synergi Excel line per observation."""
import json, sys, collections, re

NOT_ASSESSED = ("This item was not assessed within the scope of this inspection due to time constraints; "
                "no evidence was reviewed and no conclusion is drawn.")

def check(path):
    m = json.load(open(path, encoding="utf8"))
    groups = collections.defaultdict(set)
    for it in m["items"]:
        groups[(it["form"], it["q"])].add(it["obs"])
    fw = lambda f: "OVID" if f.startswith("OVID") else "INSPECTARE"
    errors, per_obs = [], collections.defaultdict(list)
    for (form, q), obs in groups.items():
        for o in obs:
            per_obs[o].append((form, q, frozenset(obs)))
    for o, places in sorted(per_obs.items()):
        sets = {p[2] for p in places}
        if len(sets) > 1:
            errors.append("obs %s is grouped differently: %s" % (o, "; ".join(
                "%s %s = %s" % (f, q, sorted(s)) for f, q, s in places)))
        seen = collections.Counter(fw(p[0]) for p in places)
        for k, n in seen.items():
            if n > 1:
                errors.append("obs %s is placed %d times in %s checklists (place it once per framework)" % (o, n, k))
    if errors:
        print("\n".join("ERROR " + e for e in errors)); sys.exit(1)
    print("OK links consistent")

TWIN_JS = r'''
/* ---------- linked duplicates (same observations in several checklists) ---------- */
var TWINS = {};
function twinKey(ti, q) {
  var it = D.templates[ti].items[q], o = [];
  if (!it || !it.notes) { return ''; }
  for (var i = 0; i < it.notes.length; i++) { o.push(it.notes[i].obs); }
  return o.sort(function (a, b) { return a - b; }).join(',');
}
function buildTwins() {
  TWINS = {}; var g = {};
  for (var ti = 0; ti < D.templates.length; ti++) {
    for (var q in D.templates[ti].items) { var k = twinKey(ti, q); if (k) { (g[k] || (g[k] = [])).push([ti, q]); } }
  }
  for (var k in g) {
    if (g[k].length < 2) { continue; }
    for (var a = 0; a < g[k].length; a++) {
      var l = [];
      for (var b = 0; b < g[k].length; b++) { if (b !== a) { l.push(g[k][b]); } }
      TWINS[g[k][a][0] + '|' + g[k][a][1]] = l;
    }
  }
}
function twinSet(ti, q, f, v) {
  var l = TWINS[ti + '|' + q] || [];
  for (var i = 0; i < l.length; i++) { ST.t[l[i][0]][f][l[i][1]] = v; }
}
function twinPhotos(ti, q) {
  var l = TWINS[ti + '|' + q] || [];
  for (var i = 0; i < l.length; i++) {
    ST.t[l[i][0]].removed[l[i][1]] = (ST.t[ti].removed[q] || []).slice(0);
    ADDED[l[i][0] + '|' + l[i][1]] = (ADDED[ti + '|' + q] || []).slice(0);
  }
}
function twinLabel(ti, q) {
  var l = TWINS[ti + '|' + q] || [], n = [];
  for (var i = 0; i < l.length; i++) { n.push(D.templates[l[i][0]].shortName + ' ' + l[i][1]); }
  return n.join(', ');
}
'''

FIND_JS = r"""
/* ---------- one finding per observation ---------- */
function findObs(ti, q) {
  var it = D.templates[ti].items[q], o = [], i;
  if (it && it.notes) { for (i = 0; i < it.notes.length; i++) { o.push(it.notes[i].obs); } }
  o.sort(function (a, b) { return a - b; });
  var mv = ST.moved[ti + '|' + q] || [];
  for (i = 0; i < mv.length; i++) { var u = D.unassigned[mv[i]]; if (u && o.indexOf(u.obs) < 0) { o.push(u.obs); } }
  return o;
}
function findKeys(ti, q) {
  var o = findObs(ti, q), k = [];
  for (var i = 1; i < o.length; i++) { k.push({ obs: o[i], key: q + '#' + o[i] }); }
  return k;
}
function findLabel(ti, q) {
  var o = findObs(ti, q);
  return o.length > 1 ? '<div class="fl">Finding 1 - Obs ' + esc(o[0]) + '</div>' : '';
}
function extraHtml(ti, q) {
  var ts = ST.t[ti], ks = findKeys(ti, q), h = '';
  for (var i = 0; i < ks.length; i++) {
    var k = ks[i].key;
    h += '<div class="fx" data-k="' + esc(k) + '"><div class="fl">Finding ' + (i + 2) + ' - Obs ' + esc(ks[i].obs) + '</div>' +
      '<textarea class="x-cmt" placeholder="Comment / Evidence...">' + esc(ts.cmt[k] || '') + '</textarea>' +
      '<div class="syn"><div><label>Synergi subject</label><input type="text" class="x-subj" value="' + esc(ts.subj[k] || '') + '"></div>' +
      '<div><label>CTR action</label><input type="text" class="x-act" value="' + esc(ts.act[k] || '') + '"></div></div></div>';
  }
  return h;
}
function twinSetX(ti, q, obs, f, v) {
  var l = TWINS[ti + '|' + q] || [];
  for (var i = 0; i < l.length; i++) { ST.t[l[i][0]][f][l[i][1] + '#' + obs] = v; }
}
function bindExtra(el, q) {
  var ts = ST.t[CUR], fx = el.querySelectorAll('.fx'), m = { 'x-cmt': 'cmt', 'x-subj': 'subj', 'x-act': 'act' };
  for (var i = 0; i < fx.length; i++) {
    var k = fx[i].getAttribute('data-k');
    for (var c in m) {
      fx[i].querySelector('.' + c).oninput = (function (k, f, obs) {
        return function () { ts[f][k] = this.value; twinSetX(CUR, q, obs, f, this.value); save(); };
      })(k, m[c], k.split('#')[1]);
    }
  }
}
"""

def patch_data(s, mpath):
    m = json.load(open(mpath, encoding="utf8"))
    groups = collections.defaultdict(list)
    for it in m["items"]:
        groups[(it["form"], it["q"])].append(it)
    rx = re.compile(r'(<script id="review-data" type="application/json">)(.*?)(</script>)', re.S)
    mt = rx.search(s)
    if not mt:
        sys.exit("ERROR anchor not found (report_kit.py changed?): review-data")
    d = json.loads(mt.group(2))
    for T in d["templates"]:
        for q, item in T["items"].items():
            its = sorted(groups.get((T["form"], q), []), key=lambda x: x["obs"])
            if len(its) < 2:
                continue
            item["comment"] = its[0]["comment"].strip()
            item["subject"] = its[0]["subject"].strip()
            item["action"] = its[0]["action"].strip()
            item["extra"] = [{"obs": x["obs"], "comment": x["comment"].strip(), "subject": x["subject"].strip(),
                              "action": x["action"].strip()} for x in its[1:]]
    payload = json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return s[:mt.start(2)] + payload + s[mt.end(2):]

def patch(path, mpath):
    s = open(path, encoding="utf8").read()
    if "var TWINS = {};" in s:
        print("already patched"); return
    s = patch_data(s, mpath)
    def rep(a, b):
        nonlocal s
        if s.count(a) != 1:
            sys.exit("ERROR anchor not found (report_kit.py changed?): " + a[:80])
        s = s.replace(a, b)
    # 1. linked duplicates
    rep("/* ---------- rendering ---------- */", TWIN_JS + FIND_JS + "\n/* ---------- rendering ---------- */")
    rep("  if (it.remark) { h += '<div class=\"remark\">Check: ' + esc(it.remark) + '</div>'; }",
        "  if (it.remark) { h += '<div class=\"remark\">Check: ' + esc(it.remark) + '</div>'; }\n"
        "  if (TWINS[ti + '|' + q]) { h += '<div class=\"linked\">&#128279; Linked with ' + esc(twinLabel(ti, q)) + ': comment, Synergi subject, CTR action, finding box and photos are copied there.</div>'; }")
    for fld, cls, val in (("obs", "f-obs", "this.checked"), ("cmt", "f-cmt", "this.value"),
                          ("subj", "f-subj", "this.value"), ("act", "f-act", "this.value")):
        ev = "onchange" if fld == "obs" else "oninput"
        old = "el.querySelector('.%s').%s = function () { ts.%s[q] = %s; save();" % (cls, ev, fld, val)
        rep(old, old.replace("save();", "twinSet(CUR, q, '%s', %s); save();" % (fld, val)))
    rep("removePhoto(CUR, q, this.getAttribute('data-ph')); refreshQ(el);",
        "removePhoto(CUR, q, this.getAttribute('data-ph')); twinPhotos(CUR, q); save(); saveAdded(); refreshQ(el);")
    rep("(ADDED[ti + '|' + q] || (ADDED[ti + '|' + q] = [])).push(d);\n      saveAdded(); refreshQ(el);",
        "(ADDED[ti + '|' + q] || (ADDED[ti + '|' + q] = [])).push(d);\n      twinPhotos(ti, q); save(); saveAdded(); refreshQ(el);")
    rep("  loadState();\n  var sel = $('selTpl');", "  loadState(); buildTwins();\n  var sel = $('selTpl');")
    rep("</style>", ".linked{margin:6px 0;padding:6px 9px;border-radius:6px;background:#e8f0fb;color:#00396b;font-size:12.5px}\n</style>")
    # 2 + 3. default N/A and NOT_ASSESSED comment
    rep("var D = null;", "var NOT_ASSESSED = " + json.dumps(NOT_ASSESSED) + ";\nvar D = null;")
    a = "    var T = D.templates[i], ts = { ans: {}, cmt: {}, obs: {}, subj: {}, act: {}, removed: {} };\n"
    rep(a, a + "    for (var s0 = 0; s0 < T.sections.length; s0++) { for (var k0 = 0; k0 < T.sections[s0].questions.length; k0++) "
               "{ var q0 = T.sections[s0].questions[k0].q; ts.ans[q0] = 'NA'; if (!T.items[q0]) { ts.cmt[q0] = NOT_ASSESSED; } } }\n")
    rep("return !!(D.templates[ti].items[q] || ts.obs[q] || trim(ts.cmt[q]) || ST.moved[ti + '|' + q]);",
        "return !!(D.templates[ti].items[q] || ts.obs[q] || (trim(ts.cmt[q]) && trim(ts.cmt[q]) !== NOT_ASSESSED) || ST.moved[ti + '|' + q]);")
    rep("if (v === 'NO' && ts.ans[q] === 'NO') { ts.obs[q] = true; }",
        "if (v === 'NO' && ts.ans[q] === 'NO') { ts.obs[q] = true; }\n"
        "        if ((ts.ans[q] === 'YES' || ts.ans[q] === 'NO') && trim(ts.cmt[q]) === NOT_ASSESSED) { ts.cmt[q] = ''; }")
    # 4. one finding per observation
    rep("  h += '<div class=\"obsrow\">", "  h += findLabel(ti, q);\n  h += '<div class=\"obsrow\">")
    a = "'<div><label>CTR action</label><input type=\"text\" class=\"f-act\" value=\"' + esc(ts.act[q] || '') + '\"></div></div>';"
    rep(a, a + "\n  h += extraHtml(ti, q);")
    rep("  var im = el.querySelectorAll('.ph img');", "  bindExtra(el, q);\n  var im = el.querySelectorAll('.ph img');")
    rep("      ts.act[q] = it.action || '';",
        "      ts.act[q] = it.action || '';\n"
        "      for (var x0 = 0; x0 < (it.extra || []).length; x0++) { var k0 = q + '#' + it.extra[x0].obs; "
        "ts.cmt[k0] = it.extra[x0].comment || ''; ts.subj[k0] = it.extra[x0].subject || ''; ts.act[k0] = it.extra[x0].action || ''; }")
    rep("inspector: M.inspector || '', finding: f });",
        "inspector: M.inspector || '', finding: f });\n"
        "      var ks = findKeys(ti, q);\n"
        "      for (var x = 0; x < ks.length; x++) {\n"
        "        var kk = ks[x].key, sx = trim(ts.subj[kk]).replace(/[\\s.]+$/, '');\n"
        "        sx = sx ? sx + ' (Q' + q + ')' : 'Question ' + q;\n"
        "        var fx = sx + '. > ' + dsp + ' - ' + (trim(M.tag) || 'TEPA DP NAV-DP1') + ' COMMENT: ' + trim(String(ts.cmt[kk] || '').replace(/\\s*\\n+\\s*/g, ' '));\n"
        "        if (trim(ts.act[kk])) { fx += ' --> ' + trim(ts.act[kk]); }\n"
        "        rows.push({ vessel: vessel, type: T.synergiType, subject: T.synergiLabel + ' - ' + dsp + ' - ' + vessel,\n"
        "          date: excelSerial(M.date), inspector: M.inspector || '', finding: fx });\n"
        "      }")
    a = "      if (trim(ts.cmt[q])) { body += '<div class=\"pv-c\">' + esc(trim(ts.cmt[q])) + '</div>'; }"
    rep(a, "      var kp = findKeys(CUR, q), cp = [];\n"
        "      if (trim(ts.cmt[q])) { cp.push(esc(trim(ts.cmt[q]))); }\n"
        "      for (var xp = 0; xp < kp.length; xp++) { if (trim(ts.cmt[kp[xp].key])) { cp.push(esc(trim(ts.cmt[kp[xp].key]))); } }\n"
        "      if (cp.length) { body += '<div class=\"pv-c\">' + cp.join('<br>') + '</div>'; }")
    rep(".linked{", ".fl{margin:8px 0 4px;font-size:12px;font-weight:bold;color:#003B6E}\n.fx{margin-top:10px;padding-top:6px;border-top:1px dashed #ccd3db}\n.linked{")
    open(path, "w", encoding="utf8").write(s)
    print("OK patched " + path)

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--check":
        check(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1].lower().endswith(".html"):
        patch(sys.argv[1], sys.argv[2])
    else:
        sys.exit(__doc__)
```
