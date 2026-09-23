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

## KI-Foto-Analyse (Firebase AI Logic)
Firebase → **KI-Dienste → AI Logic** → **Jetzt starten** → **Gemini Developer API** auswählen und aktivieren (kostenlos im Spark-Tarif).
Die App nutzt das Modell `gemini-3.6-flash` (Ersatz: `gemini-2.5-flash`), eingestellt in `index.html` unter `AI_MODELS`.

## Barcode-Scanner
Produktdaten kommen aus der freien Datenbank Open Food Facts (keine Einrichtung nötig). Der Scanner (`vendor/zxing.js`) wird erst beim ersten Scannen geladen.
