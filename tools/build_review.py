#!/usr/bin/env python3
"""Build the inspection review HTML from a Field Capture ZIP and a mapping file.

Usage:
  python3 -I build_review.py CAPTURE MAPPING.json INSPECTIONS_DIR OUT_DIR
  python3 -I report_kit.py   CAPTURE MAPPING.json OUT_DIR          (self-contained kit, no GitHub needed)
  CAPTURE = the Field Capture ZIP, or a folder with its unzipped files (photos may be flat, without photos/).
  python3 -I report_kit.py --questions                      list of checklist templates
  python3 -I report_kit.py --questions FORM.html [...]      questions of these templates
  python3 -I report_kit.py --version                        kit version
  (OUT_DIR = output folder: ONE file per checklist, named "YYYY MM DD <Vessel> <Inspection type> <Initials>.html".
   A path ending in .html gives a single file with all checklists.)

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
Rules checked: an observation is placed at most once per framework (OVID / Inspectare); questions holding the same
observations in two frameworks are linked, so an observation must be grouped with the same observations everywhere.
Review file: every question defaults to N/A, questions without finding get the NOT_ASSESSED comment, linked questions
copy their edits to the twin, and a question holding several observations shows one finding per observation
(own comment, Synergi subject and CTR action; one Synergi Excel line per observation; one block in the PDF).
"""
import base64, collections, datetime, json, os, re, sys, unicodedata, zipfile

KIT_VERSION = '2026-10-31 one finding per observation, OVID/Inspectare linking, default N/A'

HERE = os.path.dirname(os.path.abspath(__file__))
EMBEDDED_CHECKLISTS = None   # filled in report_kit.py
EMBEDDED_TEMPLATE = None     # filled in report_kit.py


def load_templates(src):
    if src is None:
        data = json.loads(EMBEDDED_CHECKLISTS)
    elif src.lower().endswith('.json'):
        data = json.load(open(src, encoding='utf-8'))
    else:
        sys.path.insert(0, HERE)
        import build_checklists
        tmp = os.path.join(HERE, '.checklists.tmp.json')
        build_checklists.main(src, tmp)
        data = json.load(open(tmp, encoding='utf-8'))
        os.remove(tmp)
    return {t['form']: t for t in data}


def review_template():
    if EMBEDDED_TEMPLATE is not None:
        return EMBEDDED_TEMPLATE
    return open(os.path.join(HERE, 'review_template.html'), encoding='utf-8').read()


class Capture:
    """Field Capture export: the ZIP itself or a folder with its files (photos may be flat)."""
    def __init__(self, path):
        self.zip = zipfile.ZipFile(path) if os.path.isfile(path) and zipfile.is_zipfile(path) else None
        self.files = {}
        if self.zip is None:
            for root, _, names in os.walk(path):
                for n in names:
                    full = os.path.join(root, n)
                    self.files.setdefault(os.path.relpath(full, path).replace(os.sep, '/'), full)
                    self.files.setdefault(n, full)

    def read(self, name):
        if self.zip is not None:
            return self.zip.read(name)
        for key in (name, os.path.basename(name)):
            if key in self.files:
                return open(self.files[key], 'rb').read()
        raise KeyError(name)


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
    z = Capture(zpath)
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
        cur = t['items'].setdefault(it['q'], [])
        if any(x['obs'] == o['no'] for x in cur):
            errors.append(tag + ': observation %d placed twice on %s %s' % (o['no'], t['form'], it['q'])); continue
        cur.append({'obs': o['no'], 'note': o.get('note', ''), 'comment': it['comment'].strip(), 'subject': it['subject'].strip(),
                    'action': it['action'].strip(), 'remark': str(it.get('remark', '')).strip(), 'photos': sel})
    # links: same group of observations everywhere, once per framework
    per_obs = collections.defaultdict(list)
    for t in templates:
        for q, lst in t['items'].items():
            for x in lst:
                per_obs[x['obs']].append((t['form'], q, frozenset(y['obs'] for y in lst)))
    for o_no, places in sorted(per_obs.items()):
        if len(set(p[2] for p in places)) > 1:
            errors.append('observation %d is grouped differently (link broken): %s' % (o_no, '; '.join(
                '%s %s = %s' % (f, q, sorted(g)) for f, q, g in places)))
        fws = collections.Counter('OVID' if p[0].startswith('OVID') else 'INSPECTARE' for p in places)
        for k, n in fws.items():
            if n > 1:
                errors.append('observation %d is placed %d times in %s checklists (place it once per framework)' % (o_no, n, k))
    # one finding per observation: first observation (lowest number) is the main finding, the others are extra findings
    for t in templates:
        for q in list(t['items']):
            lst = sorted(t['items'][q], key=lambda x: x['obs'])
            first, multi = lst[0], len(lst) > 1
            item = {'comment': first['comment'], 'subject': first['subject'], 'action': first['action'], 'remark': '',
                    'notes': [], 'photos': []}
            for x in lst:
                if x['remark']:
                    item['remark'] = (item['remark'] + ' ' if item['remark'] else '') + 'Obs %d: %s' % (x['obs'], x['remark'])
                item['notes'].append({'obs': x['obs'], 'text': x['note']})
                for p in x['photos']:
                    d = photo(p)
                    if d not in item['photos']: item['photos'].append(d)
            if multi:
                item['extra'] = [{'obs': x['obs'], 'comment': x['comment'], 'subject': x['subject'], 'action': x['action']} for x in lst[1:]]
            t['items'][q] = item
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
    meta = {'vessel': insp['vesselName'], 'date': insp['inspectionDate'],
            'inspector': mp.get('inspector') or insp.get('inspector', ''), 'location': insp.get('location', ''),
            'tag': mp.get('synergiTag') or 'TEPA DP NAV-DP1'}
    tpl = review_template()
    assert tpl.count('__REVIEW_DATA__') == 1

    def write(path, tlist):
        data = {'id': '%s|%s|%s|%s' % (meta['vessel'], meta['date'], '+'.join(t['form'] for t in tlist), now),
                'meta': meta, 'templates': tlist, 'unassigned': unassigned}
        payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
        open(path, 'w', encoding='utf-8').write(tpl.replace('__REVIEW_DATA__', payload))
        size = os.path.getsize(path) / 1048576.0
        print('OK %s  %.1f MB' % (path, size))
        for t in tlist:
            print('  %-40s %3d questions, %2d pre-filled' % (t['form'], t['questionCount'], len(t['items'])))
        if size > 15: print('WARNING: file larger than 15 MB')

    if out.lower().endswith('.html'):
        write(out, templates)                      # one file with all checklists
    else:
        os.makedirs(out, exist_ok=True)            # one file per checklist
        for t in templates:
            write(os.path.join(out, file_name(meta['date'], meta['vessel'], t.get('shortName') or t['title'], meta['inspector']) + '.html'), [t])
    print('observations: %d, unassigned: %d' % (len(obs), len(unassigned)))

def print_questions(src, forms):
    allt = load_templates(src)
    if not forms:
        for f, t in allt.items():
            print('%-40s %s (%d questions)' % (f, t.get('shortName') or t['title'], t['questionCount']))
        return
    for f in forms:
        t = allt.get(f)
        if not t:
            print('UNKNOWN TEMPLATE ' + f); continue
        print('### %s | %s' % (f, t['title']))
        for sec in t['sections']:
            print('## ' + sec['title'])
            for q in sec['questions']:
                print('%s  %s' % (q['q'], q['text']))
        print()


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--version':
        print(KIT_VERSION)
    elif len(sys.argv) >= 2 and sys.argv[1] == '--questions':
        # report_kit.py --questions [FORM.html ...]   |   build_review.py --questions INSPECTIONS_DIR [FORM.html ...]
        args = sys.argv[2:]
        if EMBEDDED_CHECKLISTS is not None:
            print_questions(None, args)
        else:
            print_questions(args[0], args[1:])
    elif EMBEDDED_CHECKLISTS is not None and len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], None, sys.argv[3])
    elif len(sys.argv) == 5:
        main(*sys.argv[1:])
    else:
        sys.exit(__doc__)
