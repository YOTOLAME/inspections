#!/usr/bin/env python3
"""Extract all checklist templates (sections, questions) from the inspections repo forms into checklists.json.
Usage: python3 build_checklists.py INSPECTIONS_DIR OUT.json"""
import glob, html, json, os, re, sys

DP_FORMS = ('OVID-DP-OPERATIONS-MOBILE.html', 'INSPECTARE-500M-MOBILE.html', 'INSPECTARE-500M-ASSET-MOBILE.html')

def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()

def main(src, out):
    res = []
    for path in sorted(glob.glob(os.path.join(src, '*-MOBILE.html'))):
        f = os.path.basename(path)
        s = open(path, encoding='utf-8').read()
        title = clean(re.search(r'<title>(.*?)</title>', s, re.S).group(1))
        prefix = re.search(r'var fileTitle = "([^"]+)"', s).group(1)
        texts = json.loads(re.search(r'var Q_TEXTS = (\{.*?\});', s, re.S).group(1))
        nums = json.loads(re.search(r'var Q_NUMS = (\{.*?\});', s, re.S).group(1))
        body = s[:s.index('<script')] if '<script' in s else s
        sections, cur = [], None
        for m in re.finditer(r'class="section-title"[^>]*>(.*?)</div>|<div class="question[^"]*" id="wrap-(q[0-9_]+)"', body, re.S):
            if m.group(1) is not None:
                cur = {'title': clean(m.group(1)), 'questions': []}
                sections.append(cur)
            else:
                qid = m.group(2)
                if cur is None:
                    cur = {'title': '', 'questions': []}; sections.append(cur)
                cur['questions'].append({'q': nums[qid], 'text': texts[qid]})
        n = sum(len(x['questions']) for x in sections)
        assert n == len(nums), (f, n, len(nums))
        fw = 'OVID' if f.startswith('OVID') else 'Inspectare'
        label = title.replace(' -- ', ' - ', 1) if fw == 'OVID' else title.replace(' -- ', ' ', 1)
        res.append({'form': f, 'framework': fw, 'title': title, 'pdfPrefix': prefix,
                    'synergiType': 'DP Inspection' if f in DP_FORMS else 'Marine Inspection',
                    'synergiLabel': label, 'questionCount': n, 'sections': sections})
        if __name__ == '__main__': print('%-40s %4d q  %2d sections  %s' % (f, n, len(sections), prefix))
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

if __name__ == '__main__':
    main(*sys.argv[1:])
