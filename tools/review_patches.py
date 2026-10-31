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
