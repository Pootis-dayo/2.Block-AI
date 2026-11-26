from flask import Flask, render_template, request, redirect, url_for, flash
import db
from validators import mask_ausweis

app = Flask(__name__)
app.secret_key = 'geheim2025'


@app.before_request
def init():
    db.init_db()


@app.route('/')
def index():
    conn = db.get_conn()
    geraete = conn.execute('SELECT * FROM geraete').fetchall()
    conn.close()
    return render_template('index.html', geraete=geraete, mask_ausweis=mask_ausweis)


@app.route('/anlegen', methods=['POST'])
def anlegen():
    inventarnummer = request.form.get('inventarnummer', '')
    bezeichnung = request.form.get('bezeichnung', '')
    ok, meldung = db.geraet_anlegen(inventarnummer, bezeichnung)
    if ok:
        flash(meldung, 'success')
    else:
        flash(meldung, 'error')
    return redirect(url_for('index'))


@app.route('/ausleihen/<int:id>', methods=['POST'])
def ausleihen(id):
    name = request.form.get('name', '')
    klasse = request.form.get('klasse', '')
    ausweisnummer = request.form.get('ausweisnummer', '')
    ok, meldung = db.ausleihen(id, name, klasse, ausweisnummer)
    if ok:
        flash(meldung, 'success')
    else:
        flash(meldung, 'error')
    return redirect(url_for('index'))


@app.route('/zurueck/<int:id>', methods=['POST'])
def zurueck(id):
    ok, meldung = db.zurueckgeben(id)
    if ok:
        flash(meldung, 'success')
    else:
        flash(meldung, 'error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=False)
