from telethon import TelegramClient, events
import re
from datetime import datetime, timedelta
import os

# SAJÁT ADATOK
api_id = int(os.getenv('TELEGRAM_API_ID', '26323340'))
api_hash = os.getenv('TELEGRAM_API_HASH', '342872321015c5140d34443fa08d712e')  # Felesleges ) eltávolítva

source_channel = 'OddAlertsBot'
target_chat = -1002160063925

client = TelegramClient('bot', api_id, api_hash).start(bot_token='7951953035:AAHvvswK0L4H1SwQn071eo6_pG13C4HYY50')

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
    # Tipp típusa
    tipp = ''
    if tipp_tipus:
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

    # Csapatok
    meccs = re.search(r'🆚 (.*?)\n', szoveg)
    csapatok = meccs.group(1) if meccs else 'Nincs adat'

    # Liga
    liga = re.search(r'🏆 (.*?)\n', szoveg)
    liga_nev = liga.group(1).strip() if liga else 'Nincs adat'

    # Időpont
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
            meccs_ido = datetime(ev, honap, nap, ora, perc)
            meccs_ido += timedelta(hours=1)  # Időzóna korrekció (GMT -> CET)

            # Hónap nevének kinyerése és fordítása
            honap_nev = meccs_ido.strftime("%B")
            honap_magyar = honapok.get(honap_nev, honap_nev)

            # Dátum formázása
            datum_str = f"{honap_magyar}. %-d. (%A) – %H:%M"
            datum_str = meccs_ido.strftime(datum_str).replace('Monday', 'Hétfő')\
                .replace('Tuesday', 'Kedd').replace('Wednesday', 'Szerda')\
                .replace('Thursday', 'Csütörtök').replace('Friday', 'Péntek')\
                .replace('Saturday', 'Szombat').replace('Sunday', 'Vasárnap')
        except ValueError:
            datum_str = 'Érvénytelen dátum'
    else:
        datum_str = 'Nincs dátum'

    # Valószínűség és fair odds
    prob = re.search(r'Probability[:\s]*([\d\.]+)%\s*\(([\d\.]+)\)', szoveg)
    valoszinuseg = prob.group(1) if prob else 'Nincs adat'
    fair_odds = prob.group(2) if prob else 'Nincs adat'

    # Odds
    odds = re.search(r'Odds[:\s]*([\d\.]+)', szoveg)
    odds_ertek = odds.group(1) if odds else 'Nincs adat'

    # Value
    value = re.search(r'Value[:\s]*([\d\.]+)%', szoveg)
    value_szazalek = '+' + value.group(1) if value else 'Nincs adat'

    # Kimenet
    return (
        f"⚽ Tipp: {tipp}\n\n"
        f"🏆 Liga: {liga_nev}\n"
        f"🆚 {csapatok}\n"
        f"📅 Dátum: {datum_str}\n"
        f"📊 Valószínűség: {valoszinuseg}% ({fair_odds})\n"
        f"💰 Odds: {odds_ertek}\n"
        f"📈 Value: {value_szazalek}%"
    )

@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    teljes_szoveg = event.message.message

    # Ellenőrizzük, hogy Value Bet-e az üzenet
    if "Value" not in teljes_szoveg:
        return  # Ha nem Value Bet, csendben kilépünk, nem küldünk semmit

    # Tipp típusának kinyerése
    tipp_tipus_match = re.search(r'⚙️ (.*?)\n', teljes_szoveg)
    tipp_tipus = tipp_tipus_match.group(1).strip() if tipp_tipus_match else None

    if not tipp_tipus:
        await client.send_message(target_chat, "⚠️ Nem található tipp típus az üzenetben!")
        return

    # Meccsek szétválasztása
    meccs_blokkok = re.split(r'(?=🆚 )', teljes_szoveg)

    # Blokk feldolgozása
    for blokk in meccs_blokkok:
        if '🆚' in blokk:
            if 'Value' in blokk and 'Probability' in blokk:
                formazott = format_tip(blokk, tipp_tipus)
                await client.send_message(target_chat, formazott)
            else:
                await client.send_message(target_chat, "⚠️ Hiányos adatok a következő blokkban:\n" + blokk)

async def on_start():
    await client.send_message(target_chat, "✅ Új botverzió aktív, csak Value Bet-eket figyelek!")

with client:
    client.loop.run_until_complete(on_start())
    client.run_until_disconnected()
