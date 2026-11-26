import re


def normalize(text):
    """Bereinigt Eingaben: None → '', strip() für Leerzeichen."""
    if text is None:
        return ""
    return str(text).strip()


def validate_geraet(inventarnummer, bezeichnung):
    """Prüft Inventarnummer und Bezeichnung. Gibt Fehlermeldung oder None zurück."""
    if not inventarnummer or not bezeichnung:
        return "Inventarnummer und Bezeichnung dürfen nicht leer sein."

    if re.match(r'^\s*$', inventarnummer) or re.match(r'^\s*$', bezeichnung):
        return "Nur Leerzeichen sind ungültig."

    if not re.match(r'^[A-Z0-9-]+$', inventarnummer):
        return "Inventarnummer muss alphanumerisch sein (A-Z, 0-9, -)."

    return None


def validate_ausweis(nr):
    """
    Prüft Ausweisnummer im Muster NNNN-TTMMJJ.
    d4 ist Prüfziffer: summe = d1*3 + d2*7 + d3*9 + d5*5 + d6*8 + d7*4 + d8*2 + d9*1 + d10*6
    prüfziffer = summe % 11 (darf nicht 10 sein) und muss gleich d4 sein.
    TT: 01-31, MM: 01-12.
    """
    nr = normalize(nr)
    if not re.match(r'^\d{4}-\d{6}$', nr):
        return "Ausweisnummer muss dem Muster NNNN-TTMMJJ entsprechen."

    ziffern = nr.replace('-', '')
    d = [int(c) for c in ziffern]

    tag = d[4] * 10 + d[5]
    monat = d[6] * 10 + d[7]

    if not (1 <= tag <= 31):
        return f"Ungültiger Tag: {tag}."
    if not (1 <= monat <= 12):
        return f"Ungültiger Monat: {monat}."

    summe = (d[0] * 3 + d[1] * 7 + d[2] * 9
             + d[4] * 5 + d[5] * 8 + d[6] * 4
             + d[7] * 2 + d[8] * 1 + d[9] * 6)

    pruefziffer = summe % 11
    if pruefziffer == 10:
        return "Ungültige Prüfziffer (Berechnung ergibt 10)."
    if pruefziffer != d[3]:
        return f"Prüfziffer stimmt nicht überein."

    return None


def mask_ausweis(nr):
    """Gibt ****-** plus die letzten 4 Ziffern zurück."""
    nr = normalize(nr)
    ziffern = nr.replace('-', '')
    return '****-**' + ziffern[-4:]
