# Eisenlog

Fitness-App fürs Handy: Workouts mit Gewichten loggen, Trainingspläne erstellen, Kalorien und Supplements tracken. Jede Person hat ein eigenes Konto.

- **App:** https://68sbfpthhn.github.io/eisenlog/
- **Quellcode:** `index.html` (die ganze App), `build.py` erzeugt daraus die installierbare Version in `docs/`
- **Daten & Konten:** Firebase (Projekt `eisenlog-ad93d`), Regeln in `firestore.rules`
- **Einrichtung:** siehe `ANLEITUNG.md`

Nach Änderungen an `index.html`: `python3 build.py` ausführen und `docs/` mit committen.
