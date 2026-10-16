# Eisenlog einrichten

Eisenlog ist eine installierbare Web-App (PWA). Konten und Daten laufen über Firebase (kostenloser Spark-Tarif), die App selbst liegt kostenlos auf GitHub Pages.

## 1. Firebase-Projekt anlegen
1. https://console.firebase.google.com → **Projekt hinzufügen** → Name `eisenlog` → Google Analytics ausschalten → erstellen.
2. **Build → Authentication → Loslegen** → Anbieter **E-Mail/Passwort** aktivieren → speichern.
3. **Build → Firestore Database → Datenbank erstellen** → Standort `europe-west3 (Frankfurt)` → **Produktionsmodus**.
4. In Firestore den Tab **Regeln** öffnen, den Inhalt von `firestore.rules` einfügen → **Veröffentlichen**.
5. **Projektübersicht → Web-App hinzufügen (`</>`)** → Name `Eisenlog` → registrieren. Den angezeigten `firebaseConfig`-Block kopieren und als `firebase-config.json` speichern (Format siehe `firebase-config.example.json`). Diese Werte sind nicht geheim; die Regeln aus Schritt 4 schützen die Daten.

## 2. Bauen und veröffentlichen
```
python3 build.py        # erzeugt docs/
```
GitHub Pages veröffentlicht den Ordner `docs/` (Settings → Pages → Branch `main`, Ordner `/docs`).

## 3. Nach dem Veröffentlichen
Firebase → **Authentication → Einstellungen → Autorisierte Domains** → `DEINNAME.github.io` hinzufügen.

## Installieren
- **iPhone:** Link in Safari öffnen → Teilen → „Zum Home-Bildschirm“
- **Android:** Link in Chrome öffnen → Menü ⋮ → „App installieren“

Jede Person erstellt in der App ihr eigenes Konto und sieht nur ihre eigenen Daten.

## Barcode-Scanner
Produktdaten kommen aus der freien Datenbank Open Food Facts (keine Einrichtung nötig). Der Scanner (`vendor/zxing.js`) wird erst beim ersten Scannen geladen.

## Vor dem Veröffentlichen (Rechtliches)
1. In `index.html` ganz oben im Abschnitt „Rechtliches“ das Objekt `OPERATOR` mit deinem Namen, deiner Anschrift und deiner Kontakt-E-Mail ausfüllen. Diese Angaben erscheinen im Impressum und in der Datenschutzerklärung. Danach `python3 build.py`.
2. Firebase → **KI-Dienste → AI Logic** wieder ausschalten (falls aktiviert). Die App nutzt keine KI mehr.
3. Firebase → **Authentication → Einstellungen → Passwortrichtlinie**: Mindestlänge 10 Zeichen einstellen, damit die Regel auch serverseitig gilt.
4. Firebase → **Projekteinstellungen → Datenschutz**: die Datenverarbeitungsbedingungen (Data Processing Terms) akzeptieren und prüfen, dass Firestore wirklich in `europe-west3 (Frankfurt)` liegt.
5. Datenschutzerklärung (`LEGAL.datenschutz` in `index.html`) lesen und anpassen, wenn du Dienste änderst. Bei Unsicherheit von einer Fachperson prüfen lassen.
