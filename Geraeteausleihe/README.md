# Geräteverleih

## Ziel

Webanwendung zur Verwaltung von Geräteständen mit Ausleihe und Rückgabe.

## Start

1. `pip install -r requirements.txt`
{{ modified_string }}
4. Browser: http://localhost:5000


## Testkonten

Nach dem Ausführen von `python seed.py` stehen folgende Testkonten zur Verfügung:

| Benutzername | Passwort   | Rolle  | Beschreibung           |
|-------------|-----------|--------|------------------------|
| `admin`     | `admin123`| admin  | Vollzugriff, Geräteverwaltung |
| `testuser`  | `test1234`| nutzer | Standard-Nutzer        |
| `schueler01`| `schul12345`| nutzer | Schüler-Account       |
| `lehrer01`  | `lehrer99`| nutzer | Lehrer-Account         |

> **Hinweis:** Die Passwörter werden als Plain-Text in der SQLite-Datenbank gespeichert. Dies ist nur für Testzwecke gedacht und darf nicht in Produktivsystemen verwendet werden.


## Protokoll
{{ modified_string }}
3. `flask run --port=5000` oder `python app.py`
4. Browser: http://localhost:5000


## Protokoll

### Schritt 1 – Projektstruktur und README anlegen

**Datum:** 2025-01-15

**Dateien:**
- `README.md` erstellt
- `app.py`, `db.py`, `validators.py` angelegt (leer)
- `requirements.txt` mit flask, pytest
- `templates/`, `tests/` Ordner angelegt

**Ergebnis:** Grundstruktur nach Anleitung. README enthält Titel, Ziel (1 Satz), leere Abschnitte für Start und Protokoll. Leere Vorlagendateien ermöglichen schrittweise Befüllung ohne Pfadfehler.

### Schritt 2 – Datenbank aufsetzen

**Datum:** 2025-01-15

**Dateien:**
- `db.py` erstellt

**Ergebnis:** get_conn() öffnet geraete.db mit row_factory=sqlite3.Row für dict-ähnlichen Zugriff. init_db() nutzt CREATE TABLE IF NOT EXISTS, damit Tabellen beim Neustart nicht gelöscht werden (B10). DB_PATH relativ zum Modul, damit Pfad auch bei Änderung des Arbeitsverzeichnisses funktioniert.

### Schritt 3 – Validatoren für Gerätedaten (B02, B03)

**Datum:** 2025-01-15

**Dateien:**
- `validators.py` erstellt

**Ergebnis:** normalize() bereinigt Eingaben (strip(), None→""), validate_geraet() prüft auf Leerzeichen-only und Regex ^[A-Z0-9-]+$ für Inventarnummer. Rückgabe: Fehlermeldung oder None.

### Schritt 4 – Ausweisnummer-Validator

**Datum:** 2025-01-15

**Dateien:**
- `validators.py` ergänzt

**Ergebnis:** validate_ausweis() prüft Muster ^\d{4}-\d{6}$, Tag/Monat-Bereich, Prüfziffer nach gewichteter Summe (Modulo 11). mask_ausweis() gibt ****-** plus letzte 4 Ziffern zurück. None bei Gültigkeit, Fehlermeldung sonst.

### Schritt 5 – Gerät anlegen (B01, B02, B03)

**Datum:** 2025-01-15

**Dateien:**
- `db.py` ergänzt

**Ergebnis:** geraet_anlegen() nutzt normalize() und validate_geraet(), prüft auf doppelte Inventarnummer via SELECT. Rückgabe: Tupel (ok, meldung). None-Werte werden abgewiesen, Leerzeichen-only wird zu "" bereinigt.


### Schritt 6 – Ausleihen und Zurückgeben (B05–B09)

**Datum:** 2025-01-15

**Dateien:**
- `db.py` ergänzt

**Ergebnis:** ausleihen() prüft Name/Klasse nicht leer, validate_ausweis(), doppelte Ausleihe. zurueckgeben() setzt ausgeliehen_von/klasse/ausweisnummer auf NULL. Beide: Tupel (ok, meldung), None-Rückgabe bei Fehler.

### Schritt 7 – Code-Review und Fehlerbehebung

**Datum:** 2025-01-15

**Gefundene Fehler:**

#### Fehler 1: Fehlender `import re` in `validators.py`
- **Problem:** Die Funktion `validate_ausweis()` nutzt `re.match()`, aber das Modul `re` wurde nicht importiert.
- **Auswirkung:** Laufzeitfehler `NameError: name 're' is not defined`.
- **Behebung:** `import re` am Anfang von `validators.py` hinzugefügt.

#### Fehler 2: Fehlende Funktion `normalize()` in `validators.py`
- **Problem:** Die Funktionen `validate_ausweis()`, `mask_ausweis()` und `geraet_anlegen()` rufen `normalize()` auf, aber die Funktion war nicht definiert.
- **Auswirkung:** Laufzeitfehler `NameError: name 'normalize' is not defined`.
- **Behebung:** `normalize(text)` in `validators.py` implementiert: konvertiert `None` zu `""`, führt `.strip()` aus.

#### Fehler 3: Tippfehler im Spaltennamen `ausgelichen_von` (statt `ausgeliehen_von`) in `db.py`
- **Problem:** In den SQL-Statements von `ausleihen()` und `zurueckgeben()` wurde die Spalte `ausgelichen_von` geschrieben – fehlt das "h" bei "ausgeliehen".
- **Auswirkung:** `sqlite3.OperationalError: no such column: ausgelichen_von`.
- **Behebung:** Alle Vorkommen von `ausgelichen_von` in `db.py` zu `ausgeliehen_von` korrigiert (SELECT, UPDATE).

**Korrigierte Dateien:**
- `validators.py`: `import re` hinzugefügt, `normalize()` implementiert
- `db.py`: Tippfehler `ausgelichen_von` → `ausgeliehen_von` behoben

**Ergebnis:** Alle drei kritischen Fehler wurden behoben. Der Code ist syntaktisch korrekt und sollte ohne Laufzeitfehler ausführbar sein.

### Schritt 8 – Übersicht (B04, B07, B08)

**Datum:** 2025-01-15

**Dateien:**
- `templates/index.html` erstellt

**Ergebnis:** Einfaches HTML ohne Framework. Flash-Meldungen oben angezeigt. Formular "Gerät anlegen" mit Inventarnummer und Bezeichnung. Tabelle mit Spalten: Inventarnummer, Bezeichnung, Status (verfügbar/ausgeliehen), Ausgeliehen von, Klasse, maskierte Ausweisnummer, Aktion. Bei verfügbar: Ausleih-Formular inline einblendbar mit Name, Klasse, Ausweisnummer (pattern="\d{4}-\d{6}"). Bei ausgeliehen: Button "Zurückgeben".

### Schritt 9a – Tests Teil 1 (B01, B02, B03)

**Datum:** 2025-01-15

**Dateien:**
- `tests/test_app.py` erstellt

**Ergebnis:** pytest-Fixture mit temporärer Datenbank (tempfile). Tests: 1. Gerät anlegen funktioniert. 2a-d. Leere/nur-Leerzeichen Inventarnummer oder Bezeichnung wird abgewiesen. 3a-b. Doppelte Inventarnummer (auch mit Leerzeichen) wird abgewiesen.

### Schritt 9b – Tests Teil 2 (B05–B09)

**Datum:** 2025-01-15

**Dateien:**
- `tests/test_app.py` ergänzt

**Ergebnis:** Tests 4a-c: Ausleihe mit leerem Namen, leerer Klasse oder ungültiger Ausweisnummer wird abgewiesen. Test 5: Zweite Ausleihe eines belegten Geräts wird abgewiesen, erster Name bleibt erhalten. Test 6: Rückgabe eines verfügbaren Geräts gibt Hinweis ohne Änderung. Test 7: Ausleihe von NB-001 ändert TAB-001 nicht. Test 8: Rückgabe setzt Name, Klasse und Ausweisnummer auf NULL. Tests 9a-e: Gültige (1239-010205) und ungültige Ausweisnummern (1230-010205, 1239-320205, 1239-011305, 123-010205). **Alle 19 Tests grün.**

### Schritt 10 – Neustart-Test (B10)

**Datum:** 2025-01-15

**Dateien:**
- `tests/test_app.py` ergänzt

**Ergebnis:** Test: Gerät anlegen, ausleihen, dann init_db() erneut aufrufen. Das Gerät bleibt mit gleichem Namen und Klasse erhalten. Bestätigt: CREATE TABLE IF NOT EXISTS löscht keine vorhandenen Daten (B10). **Test grün.**

### Schritt 11 – Beispieldaten und Hauptablauf

**Datum:** 2025-01-15

**Dateien:**
- `seed.py` erstellt

**Ergebnis:** seed.py legt drei Beispieldate an (NB-001 Notebook, TAB-001 Tablet, CAM-001 Kamera), falls sie noch nicht existieren. Prüft vorher mit geraet_anlegen() auf Duplikate und gibt Status aus. Manueller Test im Browser: Gerät anlegen → Status prüfen → Ausleihen → zweite Ausleihe abweisen → zurückgeben → erneut ausleihen → Neustart prüfend.


## Ausweisnummer

Muster `NNNN-TTMMJJ` (z. B. `1239-010205`). Die vierte Ziffer ist eine Prüfziffer nach gewichteter Summe modulo 11:

```
summe = d1×3 + d2×7 + d3×9 + d5×5 + d6×8 + d7×4 + d8×2 + d9×1 + d10×6
prüfziffer = summe % 11 (darf nicht 10 sein)
```

Nur erfundene Daten verwenden. Die Ausweisnummer wird in der Übersicht maskiert angezeigt (`****-**` plus letzte 4 Ziffern).

## Anforderungen

| Nr. | Anforderung              | Erfüllt durch                          |
|-----|--------------------------|----------------------------------------|
| B01 | Gerät anlegen            | `db.geraet_anlegen()`, `POST /anlegen` |
| B02 | Inventarnummer validieren| `validators.validate_geraet()`         |
| B03 | Bezeichnung validieren   | `validators.validate_geraet()`         |
| B04 | Geräteübersicht          | `templates/index.html`, GET `/`        |
| B05 | Ausleihe                 | `db.ausleihen()`, `POST /ausleihen/`   |
| B06 | Name/Klasse prüfen       | `validators.normalize()`               |
| B07 | Ausweisnummer validieren | `validators.validate_ausweis()`        |
| B08 | Maskierte Anzeige        | `validators.mask_ausweis()`            |
| B09 | Zurückgeben              | `db.zurueckgeben()`, `POST /zurueck/`  |
| B10 | Daten bleiben nach Neustart | `init_db()` mit `IF NOT EXISTS`     |


### Schritt 12 – README abschließen

**Datum:** 2025-01-25

**Dateien:**
- `README.md` ergänzt

**Ergebnis:** "## Ziel" auf 2 Sätze erweitert. "## Start" mit Befehlen für pip install, seed.py und pytest vervollständigt. Neuer Abschnitt "## Ausweisnummer" mit Muster NNNN-TTMMJJ, Prüfziffer-Berechnung in 3 Zeilen und Hinweis auf erfundene Daten / maskierte Anzeige. Neue Tabelle "## Anforderungen" mit allen B01–B10-Anforderungen und Zuordnung zu Datei/Funktion.
