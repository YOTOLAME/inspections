#!/usr/bin/env python3
"""Build the inspection review HTML from a Field Capture ZIP and a mapping file.

Usage:
  python3 -I build_review.py CAPTURE.zip MAPPING.json INSPECTIONS_DIR OUT_DIR
  (OUT_DIR = output folder; the file is named "YYYY MM DD <Vessel> <Inspection type> <Initials>.html".
   A path ending in .html is also accepted and used as is.)

INSPECTIONS_DIR = clone of github.com/YOTOLAME/inspections (checklist templates).
MAPPING.json:
{
  "inspector": "SURNAME First name",            (optional, overrides the ZIP)
  "synergiTag": "TEPA DP NAV-DP1",              (optional, text before COMMENT: in the Synergi Finding)
  "templates": ["INSPECTARE-PSV-MOBILE.html", "OVID-DP-OPERATIONS-MOBILE.html"],
  "items": [
    {"obs": 1, "form": "INSPECTARE-PSV-MOBILE.html", "q": "12.41",
     "comment": "...", "subject": "...", "action": "CTR to ... and provide evidence.",
     "remark": "", "photos": [1]}                 (photos: 1-based, omit = all photos of the observation)
  ],
  "unassigned": [{"obs": 3, "reason": "..."}]
}
Every observation of the ZIP must appear at least once in "items" or in "unassigned".
"""
import base64, datetime, json, os, re, sys, unicodedata, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_checklists  # noqa: E402


def load_templates(src):
    tmp = os.path.join(HERE, '.checklists.tmp.json')
    build_checklists.main(src, tmp)
    data = json.load(open(tmp, encoding='utf-8'))
    os.remove(tmp)
    return {t['form']: t for t in data}


def initials(name):
    p = str(name or '').split()
    if not p:
        return ''
    if len(p) > 1 and len(p[0]) > 1 and p[0] == p[0].upper() and p[-1] != p[-1].upper():
        p = p[1:] + p[:1]
    out = ''
    for w in p:
        c = unicodedata.normalize('NFD', w[0])[0]
        if c.isascii() and c.isalpha():
            out += c.upper()
    return out


def combined_type(templates):
    common = [t for t in templates if t['form'].startswith('OVID-COMMON-PART')]
    names = []
    for t in templates:
        n = t.get('shortName') or t['title']
        if len(common) == 4 and t in common:
            n = 'OVID Common'
        if n not in names:
            names.append(n)
    return ' + '.join(names)


def file_name(ymd, vessel, typ, inspector):
    d = str(ymd or '').split('-')
    parts = [' '.join(d)] if len(d) == 3 else []
    parts += [p for p in (vessel, typ, initials(inspector)) if p]
    s = re.sub(r'[\\/:*?"<>|]+', ' ', ' '.join(parts))
    return re.sub(r'\s+', ' ', s).strip() or 'Inspection'


def main(zpath, mpath, src, out):
    z = zipfile.ZipFile(zpath)
    insp = json.loads(z.read('inspection.json').decode('utf-8'))
    mp = json.load(open(mpath, encoding='utf-8'))
    allt = load_templates(src)
    obs = {o['no']: o for o in insp['observations']}
    photo_cache = {}

    def photo(name):
        if name not in photo_cache:
            photo_cache[name] = 'data:image/jpeg;base64,' + base64.b64encode(z.read(name)).decode('ascii')
        return photo_cache[name]

    errors, templates, qsets = [], [], {}
    for f in mp['templates']:
        if f not in allt:
            errors.append('unknown template ' + f); continue
        t = dict(allt[f]); t['items'] = {}
        templates.append(t)
        qsets[f] = set(q['q'] for s in t['sections'] for q in s['questions'])
    byform = {t['form']: t for t in templates}
    used = set()
    for i, it in enumerate(mp.get('items', [])):
        tag = 'item %d' % (i + 1)
        t = byform.get(it.get('form'))
        o = obs.get(it.get('obs'))
        if not t: errors.append(tag + ': form not in templates: %s' % it.get('form')); continue
        if it.get('q') not in qsets[t['form']]: errors.append(tag + ': question %s not in %s' % (it.get('q'), t['form'])); continue
        if not o: errors.append(tag + ': observation %s not in ZIP' % it.get('obs')); continue
        for k in ('comment', 'subject', 'action'):
            if not str(it.get(k, '')).strip(): errors.append(tag + ': empty ' + k)
        used.add(o['no'])
        idx = it.get('photos')
        try:
            sel = o['photos'] if idx is None else [o['photos'][n - 1] for n in idx]
        except IndexError:
            errors.append(tag + ': bad photo index'); continue
        cur = t['items'].setdefault(it['q'], {'comment': '', 'subject': it['subject'].strip(), 'action': it['action'].strip(),
                                              'remark': '', 'notes': [], 'photos': []})
        cur['comment'] = (cur['comment'] + '\n' if cur['comment'] else '') + it['comment'].strip()
        if str(it.get('remark', '')).strip():
            cur['remark'] = (cur['remark'] + ' ' if cur['remark'] else '') + 'Obs %d: %s' % (o['no'], it['remark'].strip())
        if not any(n['obs'] == o['no'] for n in cur['notes']):
            cur['notes'].append({'obs': o['no'], 'text': o.get('note', '')})
        for p in sel:
            d = photo(p)
            if d not in cur['photos']: cur['photos'].append(d)
    unassigned = []
    for u in mp.get('unassigned', []):
        o = obs.get(u.get('obs'))
        if not o: errors.append('unassigned: observation %s not in ZIP' % u.get('obs')); continue
        used.add(o['no'])
        unassigned.append({'obs': o['no'], 'note': o.get('note', ''), 'reason': u.get('reason', ''),
                           'photos': [photo(p) for p in o['photos']]})
    missing = sorted(set(obs) - used)
    if missing: errors.append('observations not mapped and not listed as unassigned: %s' % missing)
    if errors:
        sys.exit('ERRORS:\n- ' + '\n- '.join(errors))

    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')
    data = {
        'id': '%s|%s|%s' % (insp['vesselName'], insp['inspectionDate'], now),
        'meta': {'vessel': insp['vesselName'], 'date': insp['inspectionDate'],
                 'inspector': mp.get('inspector') or insp.get('inspector', ''), 'location': insp.get('location', ''),
                 'tag': mp.get('synergiTag') or 'TEPA DP NAV-DP1'},
        'templates': templates, 'unassigned': unassigned,
    }
    if not out.lower().endswith('.html'):
        os.makedirs(out, exist_ok=True)
        out = os.path.join(out, file_name(data['meta']['date'], data['meta']['vessel'], combined_type(templates), data['meta']['inspector']) + '.html')
    tpl = open(os.path.join(HERE, 'review_template.html'), encoding='utf-8').read()
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    assert tpl.count('__REVIEW_DATA__') == 1
    html = tpl.replace('__REVIEW_DATA__', payload)
    open(out, 'w', encoding='utf-8').write(html)
    size = os.path.getsize(out) / 1048576.0
    print('OK %s  %.1f MB' % (out, size))
    for t in templates:
        print('  %-40s %3d questions, %2d pre-filled' % (t['form'], t['questionCount'], len(t['items'])))
    print('  observations: %d, unassigned: %d' % (len(obs), len(unassigned)))
    if size > 15: print('WARNING: file larger than 15 MB')


if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
