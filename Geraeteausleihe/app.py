from flask import Flask, render_template, request, redirect, url_for, flash, session
import db_new as db
from validators import mask_ausweis

app = Flask(__name__)
app.secret_key = 'geheim2025'


@app.before_request
def init():
    db.init_db()


def logged_in():
    return 'benutzername' in session


# ---- Öffentliche Seite ----

@app.route('/')
def index():
    conn = db.get_conn()
    geraete = conn.execute('SELECT * FROM geraete').fetchall()
    conn.close()
    return render_template('index.html', geraete=geraete, mask_ausweis=mask_ausweis,
                           logged_in=logged_in(), benutzername=session.get('benutzername'))


# ---- Login / Logout ----

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        conn = db.get_conn()
        benutzer = conn.execute(
            'SELECT * FROM benutzer WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        if benutzer and benutzer['passwort_hash'] == password:
            session['benutzername'] = username
            session['rolle'] = benutzer['rolle']
            flash(f'Willkommen, {username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Benutzername oder Passwort falsch.', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Erfolgreich abgemeldet.', 'success')
    return redirect(url_for('index'))


# ---- Öffentliche Aktionen (erfordern Login) ----

@app.route('/anlegen', methods=['POST'])
def anlegen():
    if not logged_in():
        flash('Bitte zuerst einloggen.', 'error')
        return redirect(url_for('login'))
    inventarnummer = request.form.get('inventarnummer', '')
    bezeichnung = request.form.get('bezeichnung', '')
    ok, meldung = db.geraet_anlegen(inventarnummer, bezeichnung)
    flash(meldung, 'success' if ok else 'error')
    return redirect(url_for('index'))


@app.route('/ausleihen/<int:id>', methods=['POST'])
def ausleihen(id):
    if not logged_in():
        flash('Bitte zuerst einloggen.', 'error')
        return redirect(url_for('login'))
    name = request.form.get('name', '')
    klasse = request.form.get('klasse', '')
    ausweisnummer = request.form.get('ausweisnummer', '')
    ok, meldung = db.ausleihen(id, name, klasse, ausweisnummer)
    flash(meldung, 'success' if ok else 'error')
    return redirect(url_for('index'))


@app.route('/zurueck/<int:id>', methods=['POST'])
def zurueck(id):
    if not logged_in():
        flash('Bitte zuerst einloggen.', 'error')
        return redirect(url_for('login'))
    ok, meldung = db.zurueckgeben(id)
    flash(meldung, 'success' if ok else 'error')
    return redirect(url_for('index'))


# ---- Admin-Bereich ----

@app.route('/admin')
def admin():
    if not logged_in():
        flash('Bitte zuerst einloggen.', 'error')
        return redirect(url_for('login'))
    if session.get('rolle') != 'admin':
        flash('Keine Berechtigung für den Admin-Bereich.', 'error')
        return redirect(url_for('index'))
    conn = db.get_conn()
    geraete = conn.execute('SELECT * FROM geraete').fetchall()
    benutzer = conn.execute('SELECT id, username, rolle FROM benutzer').fetchall()
    conn.close()
    return render_template('admin.html', geraete=geraete, benutzer=benutzer, mask_ausweis=mask_ausweis)


@app.route('/admin/loeschen/<int:id>', methods=['POST'])
def admin_loeschen(id):
    if session.get('rolle') != 'admin':
        flash('Keine Berechtigung.', 'error')
        return redirect(url_for('login'))
    conn = db.get_conn()
    geraet = conn.execute('SELECT * FROM geraete WHERE id = ?', (id,)).fetchone()
    if geraet:
        ok, meldung = db.geraet_loeschen(geraet['inventarnummer'])
        flash(meldung, 'success' if ok else 'error')
    conn.close()
    return redirect(url_for('admin'))


@app.route('/admin/status_zuruecksetzen/<int:id>', methods=['POST'])
def admin_status_zurueck(id):
    if session.get('rolle') != 'admin':
        flash('Keine Berechtigung.', 'error')
        return redirect(url_for('login'))
    ok, meldung = db.status_zuruecksetzen(id)
    flash(meldung, 'success' if ok else 'error')
    return redirect(url_for('admin'))


@app.route('/admin/benutzer_anlegen', methods=['POST'])
def admin_benutzer_anlegen():
    if session.get('rolle') != 'admin':
        flash('Keine Berechtigung.', 'error')
        return redirect(url_for('login'))
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    rolle = request.form.get('rolle', 'nutzer')
    if not username or not password:
        flash('Benutzername und Passwort dürfen nicht leer sein.', 'error')
        return redirect(url_for('admin'))
    conn = db.get_conn()
    try:
        conn.execute(
            'INSERT INTO benutzer (username, passwort_hash, rolle) VALUES (?, ?, ?)',
            (username, password, rolle)
        )
        conn.commit()
        flash(f'Benutzer "{username}" angelegt.', 'success')
    except Exception as e:
        flash(f'Fehler beim Anlegen: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=False)

