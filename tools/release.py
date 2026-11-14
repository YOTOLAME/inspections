#!/usr/bin/env python3
"""Release helper: bump the app version everywhere.

Usage: python3 -I tools/release.py <repo_dir> "Short description of the change"

- version = 1.N (N + 1 at each release), date = today
- writes the version footer on every page, APP_VERSION in capture.html
  and review template, CACHE_NAME in sw.js, a line in CHANGELOG.txt
- regenerates review.html, report_kit.py, review-loader.js
"""
import datetime
import glob
import os
import re
import subprocess
import sys

root = os.path.abspath(sys.argv[1])
note = sys.argv[2].strip()
today = datetime.date.today().isoformat()


def rd(p):
    with open(os.path.join(root, p), encoding='utf-8') as f:
        return f.read()


def wr(p, s):
    with open(os.path.join(root, p), 'w', encoding='utf-8', newline='') as f:
        f.write(s)


log = rd('CHANGELOG.txt')
last = re.search(r'^v1\.(\d+) ', log, re.M)
ver = '1.%d' % (int(last.group(1)) + 1)
label = 'Version %s - %s' % (ver, today)
FOOT = ('<style>@media print { .app-version { display: none !important; } }</style>'
        '<div class="app-version" style="text-align:center;font-size:11px;color:#888;margin:18px 0 26px">'
        '%s - <a href="https://yotolame.github.io/inspections/CHANGELOG.txt" style="color:#888">changes</a></div>')

pages = sorted(glob.glob(os.path.join(root, '*.html'))) + [os.path.join(root, 'tools', 'review_template.html')]
for full in pages:
    p = os.path.relpath(full, root)
    if p == 'review.html':
        continue
    s = rd(p)
    s, n = re.subn(r'(?:<style>@media print \{ \.app-version[^<]*</style>)?<div class="app-version"[^>]*>.*?</div>', FOOT % label, s, flags=re.S)
    if not n:
        i = s.rindex('</body>')
        s = s[:i] + FOOT % label + '\n' + s[i:]
    s = re.sub(r"var APP_VERSION = '[^']*';", "var APP_VERSION = '%s';" % ver, s)
    wr(p, s)

sw = rd('sw.js')
m = re.search(r"inspectare-v(\d+)", sw)
sw = sw.replace(m.group(0), 'inspectare-v%d' % (int(m.group(1)) + 1))
wr('sw.js', sw)

head, sep, rest = log.partition('\n\n')
wr('CHANGELOG.txt', head + sep + 'v%s (%s)  %s\n' % (ver, today, note) + rest)

subprocess.check_call([sys.executable, '-I', os.path.join(root, 'tools', 'make_kit.py'), root], stdout=subprocess.DEVNULL)
subprocess.check_call([sys.executable, '-I', os.path.join(root, 'tools', 'make_loader.py'), root], stdout=subprocess.DEVNULL)
tpl = rd('tools/review_template.html')
cur = rd('review.html')
data = re.search(r'id="review-data" type="application/json">(.*?)</script>', cur, re.S).group(1)
wr('review.html', tpl.replace('__REVIEW_DATA__', data))
print(label, '| sw', re.search(r"inspectare-v\d+", rd('sw.js')).group(0))
