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
SNIP = ("<!--APPVER--><style>@media print { .app-version, .app-version-new { display: none !important; } }"
        " .app-version { font-size: 12px; font-weight: normal; opacity: .8; margin: 2px 0 0; }"
        " .app-version-new { position: fixed; left: 0; right: 0; bottom: 0; z-index: 9999; background: #003a70; color: #fff;"
        " text-align: center; padding: 12px; font: 14px -apple-system, Segoe UI, Arial, sans-serif; cursor: pointer; }</style>"
        "<script>\n(function () {\n"
        "  var V = '%s', D = '%s', i, h = document.getElementsByTagName('h1');\n"
        "  function lab() { var d = document.createElement('div'); d.className = 'app-version'; d.appendChild(document.createTextNode('Version ' + V + ' - ' + D)); return d; }\n"
        "  if (h.length) { for (i = 0; i < h.length; i++) { h[i].parentNode.insertBefore(lab(), h[i].nextSibling); } }\n"
        "  else { document.body.insertBefore(lab(), document.body.firstChild); }\n"
        "  if (location.protocol.indexOf('http') !== 0) { return; }\n"
        "  try {\n"
        "    var x = new XMLHttpRequest();\n"
        "    x.open('GET', '/inspections/version.txt?t=' + new Date().getTime(), true);\n"
        "    x.onload = function () {\n"
        "      var n = String(x.responseText || '').replace(/\\s+/g, '');\n"
        "      if (x.status !== 200 || !/^\\d+\\.\\d+$/.test(n) || n === V) { return; }\n"
        "      var b = document.createElement('div'); b.className = 'app-version-new';\n"
        "      b.appendChild(document.createTextNode('New version ' + n + ' available - tap here to update'));\n"
        "      b.onclick = function () {\n"
        "        function go() { location.reload(); }\n"
        "        if (window.caches && caches.keys) { caches.keys().then(function (k) { var p = []; for (var j = 0; j < k.length; j++) { p.push(caches['delete'](k[j])); } return Promise.all(p); }).then(go, go); } else { go(); }\n"
        "      };\n"
        "      document.body.appendChild(b);\n"
        "    };\n"
        "    x.send();\n"
        "  } catch (e) {}\n"
        "})();\n</script><!--/APPVER-->")

pages = sorted(glob.glob(os.path.join(root, '*.html'))) + [os.path.join(root, 'tools', 'review_template.html')]
for full in pages:
    p = os.path.relpath(full, root)
    if p == 'review.html':
        continue
    s = rd(p)
    s = re.sub(r'(?:<style>@media print \{ \.app-version[^<]*</style>)?<div class="app-version"[^>]*>.*?</div>\n?', '', s, flags=re.S)
    s, n = re.subn(r'<!--APPVER-->.*?<!--/APPVER-->', lambda m: SNIP % (ver, today), s, flags=re.S)
    if not n:
        i = s.rindex('</body>')
        s = s[:i] + SNIP % (ver, today) + '\n' + s[i:]
    s = re.sub(r"var APP_VERSION = '[^']*';", "var APP_VERSION = '%s';" % ver, s)
    wr(p, s)

sw = rd('sw.js')
m = re.search(r"inspectare-v(\d+)", sw)
sw = sw.replace(m.group(0), 'inspectare-v%d' % (int(m.group(1)) + 1))
wr('sw.js', sw)
wr('version.txt', ver + '\n')

head, sep, rest = log.partition('\n\n')
wr('CHANGELOG.txt', head + sep + 'v%s (%s)  %s\n' % (ver, today, note) + rest)

subprocess.check_call([sys.executable, '-I', os.path.join(root, 'tools', 'make_kit.py'), root], stdout=subprocess.DEVNULL)
subprocess.check_call([sys.executable, '-I', os.path.join(root, 'tools', 'make_loader.py'), root], stdout=subprocess.DEVNULL)
tpl = rd('tools/review_template.html')
cur = rd('review.html')
data = re.search(r'id="review-data" type="application/json">(.*?)</script>', cur, re.S).group(1)
wr('review.html', tpl.replace('__REVIEW_DATA__', data))
print(label, '| sw', re.search(r"inspectare-v\d+", rd('sw.js')).group(0))
