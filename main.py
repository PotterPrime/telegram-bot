from telethon import TelegramClient, events
import re
from datetime import datetime, timedelta
import os

# SAJÁT ADATOK
api_id = int(os.getenv('TELEGRAM_API_ID', '26323340'))
api_hash = os.getenv('TELEGRAM_API_HASH', '342872321015c5140d34443fa08d712e')  # Felesleges ) eltávolítva
source_channel = 'OddAlertsBot'
target_chat = -1002160063925

client = TelegramClient('tipp_session', api_id, api_hash, timeout=30)

# Hónapnevek magyar fordítása
honapok = {
    'January': 'Január',
    'February': 'Február',
    'March': 'Március',
    'April': 'Április',
    'May': 'Május',
    'June': 'Június',
    'July': 'Július',
    'August': 'Augusztus',
    'September': 'Szeptember',
    'October': 'Október',
    'November': 'November',
    'December': 'December'
}

def format_tip(szoveg, tipp_tipus=None):
    print(f"Feldolgozás alatt: {szoveg}")  # Naplózás
    # Tipp típusa
    tipp = ''
    if tipp_tipus:
        print(f"Tipp típus: {tipp_tipus}")  # Naplózás
        if 'Home Win' in tipp_tipus:
            tipp = 'Hazai győzelem'
        elif 'Away Win' in tipp_tipus:
            tipp = 'Vendég győzelem'
        elif 'Draw' in tipp_tipus:
            tipp = 'Döntetlen'
        else:
            gól_tipp = re.search(r'([+-]?\d+\.?\d*) Goals', tipp_tipus)
            if gól_tipp:
                szam = gól_tipp.group(1)
                tipp = f'Több mint {szam} gól' if float(szam) > 0 else f'Kevesebb mint {abs(float(szam))} gól'
            else:
                print("Nem ismert tipp típus.")  # Naplózás

    # Csapatok
    try:
        meccs = re.search(r'🆚 (.*?)\n', szoveg)
        csapatok = meccs.group(1) if meccs else 'Nincs adat'
        print(f"Csapatok: {csapatok}")  # Naplózás
    except Exception as e:
        print(f"Hiba a csapatok kinyerésekor: {e}")
        csapatok = 'Hiba a csapatoknál'

    # Liga
    try:
        liga = re.search(r'🏆 (.*?)\n', szoveg)
        liga_nev = liga.group(1).strip() if liga else 'Nincs adat'
        print(f"Liga: {liga_nev}")  # Naplózás
    except Exception as e:
        print(f"Hiba a liga kinyerésekor: {e}")
        liga_nev = 'Hiba a ligánál'

    # Időpont
    try:
        datum_match = re.search(r'📆 .*? (\d+)(?:st|nd|rd|th)? at (\d{2}):(\d{2})\s*\(GMT\)', szoveg)
        if datum_match:
            nap = int(datum_match.group(1))
            ora = int(datum_match.group(2))
            perc = int(datum_match.group(3))
            ma = datetime.now()

            # Hónap és év meghatározása
            if nap < ma.day:
                if ma.month == 12:
                    ev = ma.year + 1
                    honap = 1
                else:
                    ev = ma.year
                    honap = ma.month + 1
            else:
                ev = ma.year
                honap = ma.month

            try:
                meccs_ido = datetime(ev, honap, nap, ora, perc
