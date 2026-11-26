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


def create_user(username, password_hash, role='nutzer'):
    conn = get_conn()
    conn.execute(
        'INSERT INTO benutzer (username, passwort_hash, rolle) VALUES (?, ?, ?)',
        (username, password_hash, role)
    )
    conn.commit()
    conn.close()


def get_user(username):
    conn = get_conn()
    benutzer = conn.execute(
        'SELECT * FROM benutzer WHERE username = ?', (username,)
    ).fetchone()
    conn.close()
    return benutzer


def geraet_anlegen(inventarnummer, bezeichnung):
    try:
        conn = get_conn()
        conn.execute(
            'INSERT INTO geraete (inventarnummer, bezeichnung) VALUES (?, ?)',
            (inventarnummer, bezeichnung)
        )
        conn.commit()
        conn.close()
        return True, f'Gerät "{bezeichnung}" angelegt.'
    except Exception as e:
        return False, f'Fehler: {e}'


def ausleihen(geraet_id, name, klasse, ausweisnummer):
    try:
        conn = get_conn()
        conn.execute(
            'UPDATE geraete SET ausgeliehen_von = ?, klasse = ?, ausweisnummer = ? WHERE id = ?',
            (name, klasse, ausweisnummer, geraet_id)
        )
        conn.commit()
        conn.close()
        return True, f'Gerät an {name} verliehen.'
    except Exception as e:
        return False, f'Fehler: {e}'


def zurueckgeben(geraet_id):
    try:
        conn = get_conn()
        conn.execute(
            'UPDATE geraete SET ausgeliehen_von = NULL, klasse = NULL, ausweisnummer = NULL WHERE id = ?',
            (geraet_id,)
        )
        conn.commit()
        conn.close()
        return True, 'Gerät wurde zurückgegeben.'
    except Exception as e:
        return False, f'Fehler: {e}'


def geraet_loeschen(inventarnummer):
    try:
        conn = get_conn()
        conn.execute('DELETE FROM geraete WHERE inventarnummer = ?', (inventarnummer,))
        conn.commit()
        conn.close()
        return True, f'Gerät "{inventarnummer}" gelöscht.'
    except Exception as e:
        return False, f'Fehler: {e}'


def status_zuruecksetzen(geraet_id):
    try:
        conn = get_conn()
        conn.execute(
            'UPDATE geraete SET ausgeliehen_von = NULL, klasse = NULL, ausweisnummer = NULL WHERE id = ?',
            (geraet_id,)
        )
        conn.commit()
        conn.close()
        return True, 'Status wurde zurückgesetzt.'
    except Exception as e:
        return False, f'Fehler: {e}'


def aktualisiere_passwort(username, passwort_hash):
    conn = get_conn()
    conn.execute(
        'UPDATE benutzer SET passwort_hash = ? WHERE username = ?',
        (passwort_hash, username)
    )
    conn.commit()
    conn.close()


def loesche_benutzer(username):
    try:
        conn = get_conn()
        conn.execute('DELETE FROM benutzer WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        return True, f'Benutzer "{username}" gelöscht.'
    except Exception as e:
        return False, f'Fehler: {e}'


def aktualisiere_rolle(username, rolle):
    conn = get_conn()
    conn.execute(
        'UPDATE benutzer SET rolle = ? WHERE username = ?',
        (rolle, username)
    )
    conn.commit()
    conn.close()


