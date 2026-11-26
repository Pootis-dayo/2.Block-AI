# Schritt-für-Schritt-Anleitung für einen lokalen LLM-Agenten: Geräteverleih

## Vorab: Festlegungen

- **Technik:** Python, Flask und SQLite. Das ist klein, braucht keinen Server und erfüllt B10 (Daten bleiben nach einem Neustart erhalten).
- **Ausweisnummer:** Muster `NNNN-TTMMJJ` (10 Ziffern, Aufbau angelehnt an die österreichische Sozialversicherungsnummer). Die ersten drei Ziffern sind eine Laufnummer, die vierte ist eine Prüfziffer (Gewichte, Modulo 11), die letzten sechs sind ein Datum. Im Test nur erfundene Daten verwenden, nie echte Geburtsdaten. Beispiel einer gültigen Nummer: `1239-010205`.
- **Abweichung von der Aufgabe:** Die Aufgabe verlangt nur einen erfundenen Namen. Zusätzlich sind hier Klasse und Ausweisnummer eingebaut. Die Ausweisnummer wird in der Übersicht nur maskiert angezeigt (`****-**0205`), weil sie personenbezogen ist.
- **Für 17 Token/s:** Jeder Schritt ist klein (eine Datei, eine Aufgabe), die Prompts sind kurz, und der Agent soll nur Code ausgeben, ohne Erklärungen. Jeder Schritt endet mit einem README-Protokolleintrag.

---

## Schritt 0: System-Prompt (einmalig setzen)

```
Du bist ein Programmier-Agent. Regeln:
- Arbeite immer nur an dem einen Schritt, den ich nenne.
- Gib nur Code oder Befehle aus, keine langen Erklärungen.
- Ändere keine Dateien, die ich nicht nenne.
- Technik: Python 3, Flask, SQLite (Datei geraete.db), pytest.
- Nach jedem Schritt: Hänge einen Eintrag an README.md unter "## Protokoll" an.
  Format: "### Schritt N – Titel", dann "Datum", "Dateien", "Ergebnis" (max. 3 Zeilen).
- Wenn etwas unklar ist, stelle genau eine kurze Rückfrage.
Bestätige mit "OK".
```

---

## Schritt 1: Projektstruktur und README anlegen

```
Schritt 1: Lege diese Struktur an:
projekt/
  app.py
  db.py
  validators.py
  templates/index.html
  tests/test_app.py
  requirements.txt (flask, pytest)
  README.md
Dateien dürfen zunächst leer sein.
README.md bekommt: Titel "Geräteverleih", Abschnitt "## Ziel" (1 Satz),
Abschnitt "## Start" (leer) und Abschnitt "## Protokoll".
Schreibe danach den Protokolleintrag für Schritt 1.
```

**Prüfen:** Die Ordner und Dateien existieren, README.md hat vier Abschnitte.

---

## Schritt 2: Datenbank aufsetzen

```
Schritt 2: Schreibe in db.py die SQLite-Anbindung.
- Funktion get_conn() öffnet geraete.db mit row_factory = sqlite3.Row.
- Funktion init_db() erstellt (CREATE TABLE IF NOT EXISTS) die Tabelle geraete mit:
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  inventarnummer TEXT NOT NULL UNIQUE,
  bezeichnung TEXT NOT NULL,
  ausgeliehen_von TEXT NULL,
  klasse TEXT NULL,
  ausweisnummer TEXT NULL
- Ein Gerät ist verfügbar, wenn ausgeliehen_von NULL ist.
Nur db.py ändern. Dann Protokolleintrag für Schritt 2.
```

**Prüfen:** `python -c "import db; db.init_db()"` erzeugt `geraete.db` ohne Fehler.

---

## Schritt 3: Validatoren für Gerätedaten (B02, B03)

```
Schritt 3: Schreibe in validators.py:
- normalize(text): gibt text.strip() zurück, bei None einen leeren String.
- validate_geraet(inventarnummer, bezeichnung): gibt eine Fehlermeldung als
  String zurück, oder None wenn alles passt.
  Fehler, wenn nach normalize eines der Felder leer ist.
  Inventarnummer: nur Großbuchstaben, Ziffern, Bindestrich (Regex ^[A-Z0-9-]+$).
Nur validators.py ändern. Dann Protokolleintrag für Schritt 3.
```

---

## Schritt 4: Ausweisnummer-Validator

```
Schritt 4: Ergänze in validators.py die Funktion validate_ausweis(nr).
Muster: genau ^\d{4}-\d{6}$ (nach strip). Beispiel: 1239-010205.
Ziffern d1..d10 ohne Bindestrich. d4 ist die Prüfziffer.
Berechnung: summe = d1*3 + d2*7 + d3*9 + d5*5 + d6*8 + d7*4 + d8*2 + d9*1 + d10*6.
Prüfziffer = summe % 11. Ist sie 10, ist die Nummer ungültig.
Die Prüfziffer muss gleich d4 sein.
Zusätzlich: d5d6 (Tag) 01–31, d7d8 (Monat) 01–12.
Rückgabe: Fehlermeldung als String oder None.
Ergänze die Funktion mask_ausweis(nr): gibt "****-**" plus die letzten 4 Ziffern zurück.
Nur validators.py ändern. Dann Protokolleintrag für Schritt 4.
```

**Prüfen:** `validate_ausweis("1239-010205")` ergibt `None`. `validate_ausweis("1230-010205")` ergibt eine Fehlermeldung.

---

## Schritt 5: Gerät anlegen (B01, B02, B03)

```
Schritt 5: Schreibe in db.py die Funktion geraet_anlegen(inventarnummer, bezeichnung).
- Beide Werte mit normalize() bereinigen, dann validate_geraet() aufrufen.
- Existiert die Inventarnummer schon (nach strip), gib die Meldung
  "Inventarnummer bereits vorhanden." zurück.
- Sonst einfügen. Rückgabe immer als Tupel (ok: bool, meldung: str).
Nur db.py ändern. Dann Protokolleintrag für Schritt 5.
```

---

## Schritt 6: Ausleihen und Zurückgeben (B05–B09)

```
Schritt 6: Schreibe in db.py zwei Funktionen, Rückgabe jeweils (ok, meldung).
ausleihen(geraet_id, name, klasse, ausweisnummer):
- name, klasse mit normalize() bereinigen, beide dürfen nicht leer sein.
- validate_ausweis() muss None liefern.
- Ist das Gerät schon ausgeliehen, abweisen mit "Gerät ist bereits ausgeliehen."
  Die erste Ausleihe darf nicht verändert werden.
- Sonst nur dieses eine Gerät (WHERE id = ?) aktualisieren.
zurueckgeben(geraet_id):
- Ist das Gerät verfügbar, ok=False mit "Gerät ist bereits verfügbar." und keine Änderung.
- Sonst ausgeliehen_von, klasse, ausweisnummer auf NULL setzen (nur dieses Gerät).
Nur db.py ändern. Dann Protokolleintrag für Schritt 6.
```

---

## Schritt 7: Flask-Routen

```
Schritt 7: Schreibe in app.py eine Flask-App mit init_db() beim Start.
Routen:
- GET / : alle Geräte laden, index.html rendern. Ausweisnummer mit mask_ausweis maskieren.
- POST /anlegen : geraet_anlegen aufrufen
- POST /ausleihen/<int:id> : ausleihen aufrufen
- POST /zurueck/<int:id> : zurueckgeben aufrufen
Meldungen per flash() anzeigen, danach redirect auf /.
Setze einen secret_key. Starte mit app.run(debug=False).
Nur app.py ändern. Dann Protokolleintrag für Schritt 7.
```

---

## Schritt 8: Übersicht (B04, B07, B08)

```
Schritt 8: Schreibe templates/index.html (einfaches HTML, kein Framework).
- Flash-Meldungen oben anzeigen.
- Formular "Gerät anlegen": Inventarnummer, Bezeichnung.
- Tabelle mit Spalten: Inventarnummer, Bezeichnung, Status, Ausgeliehen von,
  Klasse, Ausweis (maskiert), Aktion.
- Status: "verfügbar" oder "ausgeliehen".
- Bei verfügbar: Ausleih-Formular mit Name, Klasse, Ausweisnummer
  (placeholder "1239-010205", pattern="\d{4}-\d{6}").
- Bei ausgeliehen: Button "Zurückgeben".
Nur index.html ändern. Dann Protokolleintrag für Schritt 8.
```

---

## Schritt 9: Tests für die Prüffälle

Dieser Schritt ist am größten, deshalb in zwei Teilen.

### 9a

```
Schritt 9a: Schreibe in tests/test_app.py eine pytest-Fixture, die für jeden Test
eine temporäre Datenbankdatei nutzt (Pfad per monkeypatch in db setzen).
Dann diese Tests:
1. Gerät anlegen funktioniert.
2. Leere und nur aus Leerzeichen bestehende Inventarnummer oder Bezeichnung wird abgewiesen.
3. Doppelte Inventarnummer, auch mit Leerzeichen davor oder danach, wird abgewiesen.
Nur tests/test_app.py ändern. Dann Protokolleintrag für Schritt 9a.
```

### 9b

```
Schritt 9b: Ergänze Tests:
4. Ausleihe mit leerem Namen, leerer Klasse oder ungültiger Ausweisnummer wird abgewiesen.
5. Zweite Ausleihe eines belegten Geräts wird abgewiesen, der erste Name bleibt.
6. Rückgabe eines verfügbaren Geräts: Hinweis, keine Zustandsänderung.
7. Ausleihe von NB-001 ändert TAB-001 nicht.
8. Rückgabe setzt Name, Klasse und Ausweisnummer auf NULL.
9. Gültige und ungültige Ausweisnummern: 1239-010205 gültig; 1230-010205,
   1239-320205, 1239-011305, 123-010205 ungültig.
Dann Protokolleintrag für Schritt 9b.
```

**Prüfen:** `pytest` läuft vollständig grün. Wenn nicht, gib dem Agenten nur die Fehlermeldung eines einzelnen Tests und lass ihn genau diesen beheben.

---

## Schritt 10: Neustart-Test (B10)

```
Schritt 10: Schreibe einen Test: Gerät anlegen, ausleihen, dann die Datenbankverbindung
schließen und neu öffnen (init_db() erneut aufrufen). Das Gerät muss noch ausgeliehen
sein, mit gleichem Namen und gleicher Klasse. Dass init_db() vorhandene Daten
nicht löscht (CREATE TABLE IF NOT EXISTS), ist dabei der Kern.
Dann Protokolleintrag für Schritt 10.
```

---

## Schritt 11: Beispieldaten und Hauptablauf

```
Schritt 11: Schreibe ein Skript seed.py, das diese Geräte anlegt, falls sie fehlen:
NB-001 Notebook, TAB-001 Tablet, CAM-001 Kamera.
Dann Protokolleintrag für Schritt 11.
```

**Manueller Test des Hauptablaufs** (im Browser, `python app.py`):

1. Gerät anlegen: `NB-001` / Notebook
2. Status prüfen: verfügbar
3. Ausleihen: Anna Muster / 3A / `1239-010205`
4. Zweite Ausleihe versuchen: wird abgewiesen
5. Zurückgeben
6. Erneut ausleihen: klappt

Zum Schluss `app.py` mit Strg+C beenden, neu starten und prüfen, ob eine aktive Ausleihe erhalten bleibt.

---

## Schritt 12: README abschließen

```
Schritt 12: Vervollständige README.md:
- "## Ziel": 2 Sätze.
- "## Start": Befehle zum Installieren (pip install -r requirements.txt),
  Starten (python app.py) und Testen (pytest).
- "## Ausweisnummer": Muster NNNN-TTMMJJ, Prüfziffer-Berechnung in 3 Zeilen,
  Hinweis: nur erfundene Daten verwenden, Anzeige maskiert.
- "## Anforderungen": Tabelle B01–B10 mit Spalte "erfüllt durch" (Datei/Funktion).
Das Protokoll darf nicht verändert werden. Ergänze am Ende den Eintrag für Schritt 12.
```

---

## Tipps für den Betrieb mit 17 Token/s

- **Ein Schritt pro Anfrage.** Sende nie mehrere Schritte zusammen. 17 Token/s entsprechen etwa 800 bis 1000 Zeichen Code pro Minute, daher sind Schritte unter 60 Zeilen ideal.
- **Kontext klein halten.** Starte pro Schritt gern eine neue Sitzung. Gib dem Agenten den System-Prompt und die jeweils betroffene Datei, nicht das ganze Projekt.
- **Bei Fehlern gezielt eingreifen:** „Behebe nur diesen Fehler in Datei X: [Fehlermeldung]. Gib nur die geänderte Funktion aus."
- **Geschätzte Gesamtdauer:** etwa 60 bis 90 Minuten reine Generierungszeit.
