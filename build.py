"""Baut aus index.html (Artifact-Version) die installierbare PWA in docs/."""
import hashlib, json, pathlib, shutil

root = pathlib.Path(__file__).parent
dist = root / 'docs'
dist.mkdir(exist_ok=True)
body = (root / 'index.html').read_text()
title_end = body.index('</title>') + len('</title>')
title, rest = body[:title_end], body[title_end:]
head_end = rest.index('</style>') + len('</style>')
head, content = rest[:head_end], rest[head_end:]
cfg_file = root / 'firebase-config.json'
cfg = json.loads(cfg_file.read_text()) if cfg_file.exists() else None
version = hashlib.sha1((body + json.dumps(cfg)).encode()).hexdigest()[:10]
vendor = ['firebase-bundle.js']  # zxing.js wird bei Bedarf nachgeladen
firebase_tags = ''
if cfg:
    (dist / 'vendor').mkdir(exist_ok=True)
    for f in vendor + ['zxing.js']:
        shutil.copy(root / 'vendor' / f, dist / 'vendor' / f)
    for old in (dist / 'vendor').glob('firebase-*-compat.js'):
        old.unlink()
    firebase_tags = '\n'.join(f'<script src="vendor/{f}"></script>' for f in vendor)
    firebase_tags += f'\n<script>window.EISENLOG_FIREBASE = {json.dumps(cfg)};</script>'
elif (dist / 'vendor').exists():
    shutil.rmtree(dist / 'vendor')

page = f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{title}
<meta name="description" content="Workouts, Trainingspläne, Kalorien und Supplements tracken.">
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#F1F3F2" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0D1012" media="(prefers-color-scheme: dark)">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Eisenlog">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<style>:root{{padding-top:env(safe-area-inset-top,0px)}} body{{margin:0}} img{{max-width:100%}}</style>
{head}
{firebase_tags}
</head>
<body>
{content}
<script>
if ('serviceWorker' in navigator) addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {{}}));
</script>
</body>
</html>
'''
(dist / 'index.html').write_text(page)
shutil.copytree(root / 'icons', dist / 'icons', dirs_exist_ok=True)

manifest = {
    "name": "Eisenlog", "short_name": "Eisenlog", "lang": "de",
    "description": "Workouts, Trainingspläne, Kalorien und Supplements tracken.",
    "start_url": "./", "scope": "./", "display": "standalone", "orientation": "portrait",
    "background_color": "#F1F3F2", "theme_color": "#F1F3F2",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
(dist / 'manifest.webmanifest').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))

(dist / 'sw.js').write_text(f'''const CACHE = 'eisenlog-{version}';
const SHELL = {json.dumps(['./', 'index.html', 'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png'] + ([f'vendor/{f}' for f in vendor] if cfg else []))};
self.addEventListener('install', e => {{ e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); }});
self.addEventListener('activate', e => {{
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
}});
self.addEventListener('fetch', e => {{
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  // Seite selbst: erst Netz (für Updates), offline aus dem Cache
  if (req.mode === 'navigate') {{
    e.respondWith(fetch(req).then(r => {{ const c = r.clone(); caches.open(CACHE).then(x => x.put('index.html', c)); return r; }})
      .catch(() => caches.match('index.html')));
    return;
  }}
  // Alles andere (Icons, Schriften): Cache zuerst, im Hintergrund auffrischen
  if (url.origin === location.origin || /fonts\\.(googleapis|gstatic)\\.com$/.test(url.hostname)) {{
    e.respondWith(caches.match(req).then(hit => {{
      const net = fetch(req).then(r => {{ if (r.ok || r.type === 'opaque') {{ const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); }} return r; }}).catch(() => hit);
      return hit || net;
    }}));
  }}
}});
''')
print('built', version, 'mit Firebase' if cfg else 'ohne Firebase (nur lokal)')
