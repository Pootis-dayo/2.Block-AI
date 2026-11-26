import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'geraete.db')


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS geraete (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inventarnummer TEXT NOT NULL UNIQUE,
            bezeichnung TEXT NOT NULL,
            ausgeliehen_von TEXT NULL,
            klasse TEXT NULL,
            ausweisnummer TEXT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS benutzer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            passwort_hash TEXT NOT NULL,
            rolle TEXT NOT NULL DEFAULT 'nutzer'
        )
    ''')
    # Standard-Admin anlegen falls nicht existiert
    conn.execute('''
        INSERT OR IGNORE INTO benutzer (username, passwort_hash, rolle)
        VALUES (?, ?, ?)
    ''', ('admin', 'admin123', 'admin'))
    conn.commit()
    conn.close()


from validators import normalize, validate_geraet, validate_ausweis


def geraet_anlegen(inventarnummer, bezeichnung):
    inv = normalize(inventarnummer)
    bez = normalize(bezeichnung)

    fehler = validate_geraet(inv, bez)
    if fehler:
        return (False, fehler)

    conn = get_conn()
    try:
        existing = conn.execute(
            'SELECT id FROM geraete WHERE inventarnummer = ?', (inv,)
        ).fetchone()
        if existing:
            return (False, "Inventarnummer bereits vorhanden.")

        conn.execute(
            'INSERT INTO geraete (inventarnummer, bezeichnung) VALUES (?, ?)',
            (inv, bez)
        )
        conn.commit()
        return (True, "Gerät erfolgreich angelegt.")
    finally:
        conn.close()


def geraet_loeschen(inventarnummer):
    """Löscht ein Gerät. Gibt (ok, meldung) zurück."""
    inv = normalize(inventarnummer)
    if not inv:
        return (False, "Inventarnummer darf nicht leer sein.")

    conn = get_conn()
    try:
        geraet = conn.execute(
            'SELECT id, ausgeliehen_von FROM geraete WHERE inventarnummer = ?', (inv,)
        ).fetchone()
        if not geraet:
            return (False, "Gerät nicht gefunden.")
        if geraet['ausgeliehen_von'] is not None:
            return (False, "Gerät kann nicht gelöscht werden, da es ausgeliehen ist.")

        conn.execute('DELETE FROM geraete WHERE inventarnummer = ?', (inv,))
        conn.commit()
        return (True, f"Gerät {inv} wurde gelöscht.")
    finally:
        conn.close()


def status_zuruecksetzen(geraet_id):
    """Setzt Status eines Geräts zurück auf verfügbar."""
    conn = get_conn()
    try:
        geraet = conn.execute(
            'SELECT id, ausgeliehen_von FROM geraete WHERE id = ?', (geraet_id,)
        ).fetchone()
        if not geraet:
            return (False, "Gerät nicht gefunden.")
        if geraet['ausgeliehen_von'] is None:
            return (False, "Gerät ist bereits verfügbar.")

        conn.execute(
            'UPDATE geraete SET ausgeliehen_von = NULL, klasse = NULL, ausweisnummer = NULL WHERE id = ?',
            (geraet_id,)
        )
        conn.commit()
        return (True, f"Status von Gerät {geraet_id} wurde zurückgesetzt.")
    finally:
        conn.close()


def ausleihen(geraet_id, name, klasse, ausweisnummer):
    n = normalize(name)
    k = normalize(klasse)

    if not n or not k:
        return (False, "Name und Klasse dürfen nicht leer sein.")

    ausweis_fehler = validate_ausweis(ausweisnummer)
    if ausweis_fehler:
        return (False, ausweis_fehler)

    conn = get_conn()
    try:
        geraet = conn.execute(
            'SELECT id, ausgeliehen_von FROM geraete WHERE id = ?', (geraet_id,)
        ).fetchone()

        if not geraet:
            return (False, "Gerät nicht gefunden.")

        if geraet['ausgeliehen_von'] is not None:
            return (False, "Gerät ist bereits ausgeliehen.")

        conn.execute(
            'UPDATE geraete SET ausgeliehen_von = ?, klasse = ?, ausweisnummer = ? WHERE id = ?',
            (n, k, normalize(ausweisnummer), geraet_id)
        )
        conn.commit()
        return (True, "Gerät erfolgreich ausgeliehen.")
    finally:
        conn.close()


def zurueckgeben(geraet_id):
    conn = get_conn()
    try:
        geraet = conn.execute(
            'SELECT id, ausgeliehen_von FROM geraete WHERE id = ?', (geraet_id,)
        ).fetchone()

        if not geraet:
            return (False, "Gerät nicht gefunden.")

        if geraet['ausgeliehen_von'] is None:
            return (False, "Gerät ist bereits verfügbar.")

        conn.execute(
            'UPDATE geraete SET ausgeliehen_von = NULL, klasse = NULL, ausweisnummer = NULL WHERE id = ?',
            (geraet_id,)
        )
        conn.commit()
        return (True, "Gerät erfolgreich zurückgegeben.")
    finally:
        conn.close()
