from telethon import TelegramClient, events
import re
from datetime import datetime, timedelta
import os

# SAJÁT ADATOK
api_id = int(os.getenv('TELEGRAM_API_ID', '26323340'))
api_hash = os.getenv('TELEGRAM_API_HASH', '342872321015c5140d34443fa08d712e')
# Bot token környezeti változóként
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')  # Adj hozzá egy bot token-t a Render környezeti változókhoz
source_channel = 'OddAlertsBot'
target_chat = -1002160063925

# A TelegramClient inicializálása bot token-nel
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
            except ValueError as e:
                print(f"Hiba a dátum formázásakor: {e}")
                datum_str = 'Érvénytelen dátum'
        else:
            datum_str = 'Nincs dátum'
        print(f"Dátum: {datum_str}")  # Naplózás
    except Exception as e:
        print(f"Hiba a dátum kinyerésekor: {e}")
        datum_str = 'Hiba a dátumnál'

    # Valószínűség és fair odds
    try:
        prob = re.search(r'Probability[:\s]*([\d\.]+)%\s*\(([\d\.]+)\)', szoveg)
        valoszinuseg = prob.group(1) if prob else 'Nincs adat'
        fair_odds = prob.group(2) if prob else 'Nincs adat'
        print(f"Valószínűség: {valoszinuseg}, Fair odds: {fair_odds}")  # Naplózás
    except Exception as e:
        print(f"Hiba a valószínűség kinyerésekor: {e}")
        valoszinuseg = 'Hiba'
        fair_odds = 'Hiba'

    # Odds
    try:
        odds = re.search(r'Odds[:\s]*([\d\.]+)', szoveg)
        odds_ertek = odds.group(1) if odds else 'Nincs adat'
        print(f"Odds: {odds_ertek}")  # Naplózás
    except Exception as e:
        print(f"Hiba az odds kinyerésekor: {e}")
        odds_ertek = 'Hiba'

    # Value
    try:
        value = re.search(r'Value[:\s]*([\d\.]+)%', szoveg)
        value_szazalek = '+' + value.group(1) if value else 'Nincs adat'
        print(f"Value: {value_szazalek}")  # Naplózás
    except Exception as e:
        print(f"Hiba a value kinyerésekor: {e}")
        value_szazalek = 'Hiba'

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
    try:
        # 1. Üzenet kinyerése és naplózása
        teljes_szoveg = event.message.message
        print(f"Új üzenet érkezett az OddAlertsBot-tól: {teljes_szoveg}")

        # 2. Ellenőrizzük, hogy Value Bet-e az üzenet
        if "Value" not in teljes_szoveg:
            print("Nem Value Bet, kihagyom az üzenetet.")
            return  # Ha nem Value Bet, csendben kilépünk

        print("Value Bet észlelve, folytatom a feldolgozást...")

        # 3. Tipp típusának kinyerése
        try:
            tipp_tipus_match = re.search(r'⚙️ (.*?)\n', teljes_szoveg)
            tipp_tipus = tipp_tipus_match.group(1).strip() if tipp_tipus_match else None
            if not tipp_tipus:
                print("Nem található tipp típus az üzenetben!")
                await client.send_message(target_chat, "⚠️ Nem található tipp típus az üzenetben!")
                return
            print(f"Tipp típus kinyerve: {tipp_tipus}")
        except Exception as e:
            print(f"Hiba a tipp típus kinyerésekor: {e}")
            await client.send_message(target_chat, f"⚠️ Hiba a tipp típus kinyerésekor: {e}")
            return

        # 4. Meccsek szétválasztása
        try:
            meccs_blokkok = re.split(r'(?=🆚 )', teljes_szoveg)
            print(f"Meccs blokkok száma: {len(meccs_blokkok)}")
        except Exception as e:
            print(f"Hiba a meccsek szétválasztásakor: {e}")
            await client.send_message(target_chat, f"⚠️ Hiba a meccsek szétválasztásakor: {e}")
            return

        # 5. Blokk feldolgozása
        for blokk in meccs_blokkok:
            try:
                if '🆚' in blokk:
                    print(f"Blokk feldolgozása: {blokk}")
                    # Ellenőrizzük, hogy a blokk tartalmaz-e Value és Probability adatokat
                    if 'Value' in blokk and 'Probability' in blokk:
                        print("Value és Probability megtalálva, formázás...")
                        formazott = format_tip(blokk, tipp_tipus)
                        print(f"Formázott üzenet: {formazott}")
                        await client.send_message(target_chat, formazott)
                        print("Üzenet elküldve a cél csevegésbe.")
                    else:
                        print(f"Hiányos adatok a blokkban: {blokk}")
                        await client.send_message(target_chat, f"⚠️ Hiányos adatok a következő blokkban:\n{blokk}")
            except Exception as e:
                print(f"Hiba a blokk feldolgozása közben: {e}")
                await client.send_message(target_chat, f"⚠️ Hiba a blokk feldolgozása közben: {e}")

    except Exception as e:
        print(f"Hiba az üzenet teljes feldolgozása közben: {e}")
        await client.send_message(target_chat, f"⚠️ Hiba az üzenet feldolgozása közben: {e}")

async def on_start():
    try:
        await client.send_message(target_chat, "✅ Új botverzió aktív, csak Value Bet-eket figyelek!")
        print("Kezdeti üzenet elküldve.")
    except Exception as e:
        print(f"Hiba a kezdeti üzenet küldésekor: {e}")

# Bot indítása bot token-nel
with client:
    # A bot token-t használjuk a bejelentkezéshez
    client.start(bot_token=bot_token)
    client.loop.run_until_complete(on_start())
    client.run_until_disconnected()
