import db


def seed():
    """Legt Beispieldate und Testbenutzer an, falls sie noch nicht existieren."""
    # --- Geräte ---
    beispiele = [
        ('NB-001', 'Notebook'),
        ('TAB-001', 'Tablet'),
        ('CAM-001', 'Kamera'),
    ]

    print("Beispieldate werden angelegt:")
    for inventarnummer, bezeichnung in beispiele:
        ok, meldung = db.geraet_anlegen(inventarnummer, bezeichnung)
        if not ok and 'bereits vorhanden' in meldung:
            print(f"  {inventarnummer} ({bezeichnung}) existiert bereits.")
        elif ok:
            print(f"  {inventarnummer} ({bezeichnung}) angelegt.")
        else:
            print(f"  Fehler bei {inventarnummer}: {meldung}")

    # --- Testbenutzer ---
    test_benutzer = [
        ('admin',      'admin123',     'admin'),
        ('testuser',   'test1234',     'nutzer'),
        ('schueler01', 'schul12345',   'nutzer'),
        ('lehrer01',   'lehrer99',     'nutzer'),
    ]

    print("\nTestbenutzer werden angelegt:")
    conn = db.get_conn()
    for username, passwort_hash, rolle in test_benutzer:
        try:
            conn.execute(
                'INSERT INTO benutzer (username, passwort_hash, rolle) VALUES (?, ?, ?)',
                (username, passwort_hash, rolle)
            )
            conn.commit()
            print(f"  {username} ({rolle}) angelegt.")
        except Exception as e:
            if 'UNIQUE constraint failed' in str(e):
                print(f"  {username} existiert bereits.")
            else:
                print(f"  Fehler bei {username}: {e}")
    conn.close()


if __name__ == '__main__':
    db.init_db()
    seed()
