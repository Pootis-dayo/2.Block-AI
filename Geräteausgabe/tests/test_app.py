import os
import sys
import tempfile
import pytest

# Pfad zum Projekt hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import db


@pytest.fixture
def temp_db():
    """Erstellt eine temporäre Datenbank für jeden Test."""
    tmp = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    tmp.close()
    original_path = db.DB_PATH
    db.DB_PATH = tmp.name
    db.init_db()
    yield tmp.name
    db.DB_PATH = original_path
    os.unlink(tmp.name)


def test_geraet_anlegen_funktioniert(temp_db):
    """Test 1: Gerät anlegen funktioniert."""
    ok, meldung = db.geraet_anlegen('NB-001', 'Notebook')
    assert ok is True
    assert 'erfolgreich' in meldung

    conn = db.get_conn()
    geraet = conn.execute(
        "SELECT * FROM geraete WHERE inventarnummer = ?", ('NB-001',)
    ).fetchone()
    conn.close()
    assert geraet is not None
    assert geraet['bezeichnung'] == 'Notebook'


def test_leere_inventarnummer_abgewiesen(temp_db):
    """Test 2a: Leere Inventarnummer wird abgewiesen."""
    ok, meldung = db.geraet_anlegen('', 'Notebook')
    assert ok is False


def test_nur_leszeichen_inventarnummer_abgewiesen(temp_db):
    """Test 2b: Nur aus Leerzeichen bestehende Inventarnummer wird abgewiesen."""
    ok, meldung = db.geraet_anlegen('   ', 'Notebook')
    assert ok is False


def test_leere_bezeichnung_abgewiesen(temp_db):
    """Test 2c: Leere Bezeichnung wird abgewiesen."""
    ok, meldung = db.geraet_anlegen('NB-001', '')
    assert ok is False


def test_nur_leszeichen_bezeichnung_abgewiesen(temp_db):
    """Test 2d: Nur aus Leerzeichen bestehende Bezeichnung wird abgewiesen."""
    ok, meldung = db.geraet_anlegen('NB-001', '   ')
    assert ok is False


def test_doppelte_inventarnummer_abgewiesen(temp_db):
    """Test 3a: Doppelte Inventarnummer wird abgewiesen."""
    db.geraet_anlegen('NB-001', 'Notebook')
    ok, meldung = db.geraet_anlegen('NB-001', 'Laptop')
    assert ok is False
    assert 'bereits vorhanden' in meldung


def test_doppelte_inventarnummer_mit_leerzeichen_abgewiesen(temp_db):
    """Test 3b: Doppelte Inventarnummer mit Leerzeichen wird abgewiesen."""
    db.geraet_anlegen('NB-001', 'Notebook')
    ok, meldung = db.geraet_anlegen('  NB-001  ', 'Laptop')
    assert ok is False
    assert 'bereits vorhanden' in meldung


def test_ausleihe_leerer_name_abgewiesen(temp_db):
    """Test 4a: Ausleihe mit leerem Namen wird abgewiesen."""
    db.geraet_anlegen('NB-001', 'Notebook')
    ok, meldung = db.ausleihen(1, '', '3A', '1239-010205')
    assert ok is False


def test_ausleihe_leere_klasse_abgewiesen(temp_db):
    """Test 4b: Ausleihe mit leerer Klasse wird abgewiesen."""
    db.geraet_anlegen('NB-001', 'Notebook')
    ok, meldung = db.ausleihen(1, 'Anna', '', '1239-010205')
    assert ok is False


def test_ausleihe_ungueltige_ausweisnummer_abgewiesen(temp_db):
    """Test 4c: Ausleihe mit ungültiger Ausweisnummer wird abgewiesen."""
    db.geraet_anlegen('NB-001', 'Notebook')
    ok, meldung = db.ausleihen(1, 'Anna', '3A', '1230-010205')
    assert ok is False


def test_zweite_ausleihe_abgewiesen(temp_db):
    """Test 5: Zweite Ausleihe eines belegten Geräts wird abgewiesen."""
    db.geraet_anlegen('NB-001', 'Notebook')
    db.ausleihen(1, 'Anna', '3A', '1239-010205')
    ok, meldung = db.ausleihen(1, 'Max', '4B', '1239-010205')
    assert ok is False

    conn = db.get_conn()
    geraet = conn.execute('SELECT * FROM geraete WHERE id = ?', (1,)).fetchone()
    conn.close()
    assert geraet['ausgeliehen_von'] == 'Anna'


def test_rueckgabe_verfuegbares_geraet(temp_db):
    """Test 6: Rückgabe eines verfügbaren Geräts: Hinweis, keine Änderung."""
    db.geraet_anlegen('NB-001', 'Notebook')
    ok, meldung = db.zurueckgeben(1)
    assert ok is False
    assert 'bereits verfügbar' in meldung

    conn = db.get_conn()
    geraet = conn.execute('SELECT * FROM geraete WHERE id = ?', (1,)).fetchone()
    conn.close()
    assert geraet['ausgeliehen_von'] is None


def test_ausleihe_anderes_geraet_nicht_geaendert(temp_db):
    """Test 7: Ausleihe von NB-001 ändert TAB-001 nicht."""
    db.geraet_anlegen('NB-001', 'Notebook')
    db.geraet_anlegen('TAB-001', 'Tablet')
    db.ausleihen(1, 'Anna', '3A', '1239-010205')

    conn = db.get_conn()
    tab = conn.execute('SELECT * FROM geraete WHERE inventarnummer = ?', ('TAB-001',)).fetchone()
    conn.close()
    assert tab['ausgeliehen_von'] is None


def test_rueckgabe_setzt_auf_null(temp_db):
    """Test 8: Rückgabe setzt Name, Klasse und Ausweisnummer auf NULL."""
    db.geraet_anlegen('NB-001', 'Notebook')
    db.ausleihen(1, 'Anna', '3A', '1239-010205')

    conn = db.get_conn()
    geraet = conn.execute('SELECT * FROM geraete WHERE id = ?', (1,)).fetchone()
    assert geraet['ausgeliehen_von'] == 'Anna'
    assert geraet['klasse'] == '3A'
    assert geraet['ausweisnummer'] is not None
    conn.close()

    db.zurueckgeben(1)

    conn = db.get_conn()
    geraet = conn.execute('SELECT * FROM geraete WHERE id = ?', (1,)).fetchone()
    conn.close()
    assert geraet['ausgeliehen_von'] is None
    assert geraet['klasse'] is None
    assert geraet['ausweisnummer'] is None


def test_ausweis_gueltig(temp_db):
    """Test 9a: Gültige Ausweisnummer 1239-010205."""
    assert db.validate_ausweis('1239-010205') is None


def test_ausweis_ungueltige_pruefziffer(temp_db):
    """Test 9b: Ungültige Ausweisnummer 1230-010205 (falsche Prüfziffer)."""
    assert db.validate_ausweis('1230-010205') is not None


def test_ausweis_ungueltiger_tag(temp_db):
    """Test 9c: Ungültige Ausweisnummer 1239-320205 (Tag 32)."""
    assert db.validate_ausweis('1239-320205') is not None


def test_ausweis_ungueltiger_monat(temp_db):
    """Test 9d: Ungültige Ausweisnummer 1239-011305 (Monat 13)."""
    assert db.validate_ausweis('1239-011305') is not None


def test_ausweis_falsches_muster(temp_db):
    """Test 9e: Ungültige Ausweisnummer 123-010205 (falsches Muster)."""
    assert db.validate_ausweis('123-010205') is not None


def test_neustart_daten_erhalten(temp_db):
    """Test 10: Gerät anlegen, ausleihen, dann init_db() erneut aufrufen.
    Das Gerät muss noch ausgeliehen sein mit gleichem Namen und Klasse.
    Kern: init_db() löscht keine vorhandenen Daten (CREATE TABLE IF NOT EXISTS)."""
    # Gerät anlegen und ausleihen
    db.geraet_anlegen('NB-001', 'Notebook')
    ok, meldung = db.ausleihen(1, 'Anna Muster', '3A', '1239-010205')
    assert ok is True

    # Datenbankverbindung schließen und neu initialisieren
    conn = db.get_conn()
    ausleihedaten = (
        conn.execute('SELECT * FROM geraete WHERE id = ?', (1,)).fetchone(),
    )
    conn.close()

    # init_db() erneut aufrufen (simuliert Neustart)
    db.init_db()

    # Nach dem Neustart muss das Gerät noch ausgeliehen sein
    conn2 = db.get_conn()
    geraet = conn2.execute('SELECT * FROM geraete WHERE id = ?', (1,)).fetchone()
    conn2.close()

    assert geraet is not None
    assert geraet['inventarnummer'] == 'NB-001'
    assert geraet['bezeichnung'] == 'Notebook'
    assert geraet['ausgeliehen_von'] == 'Anna Muster'
    assert geraet['klasse'] == '3A'
    assert geraet['ausweisnummer'] is not None
