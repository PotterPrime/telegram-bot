from telethon import TelegramClient, events
import re
from datetime import datetime, timedelta
import os

# SAJÁT ADATOK
api_id = int(os.getenv('TELEGRAM_API_ID', '26323340'))
api_hash = os.getenv('TELEGRAM_API_HASH', '342872321015c5140d34443fa08d712e')
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Ellenőrizzük, hogy a bot_token létezik-e
if not bot_token:
    raise ValueError("Hiba: A TELEGRAM_BOT_TOKEN környezeti változó nincs beállítva!")

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
    print(f"Feldolgozás alatt: {szoveg}")
    tipp = ''
    if tipp_tipus:
        print(f"Tipp típus: {tipp_tipus}")
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
                print("Nem ismert tipp típus.")

    try:
        meccs = re.search(r'🆚 (.*?)\n', szoveg)
        if meccs is None:
            raise ValueError("Nem található '🆚' az üzenetben")
        csapatok = meccs.group(1) if meccs else 'Nincs adat'
        print(f"Csapatok: {csapatok}")
    except Exception as e:
        print(f"Hiba a csapatok kinyerésekor: {e}")
        csapatok = 'Hiba a csapatoknál'

    try:
        liga = re.search(r'🏆 (.*?)\n', szoveg)
        if liga is None:
            raise ValueError("Nem található '🏆' az üzenetben")
        liga_nev = liga.group(1).strip() if liga else 'Nincs adat'
        print(f"Liga: {liga_nev}")
    except Exception as e:
        print(f"Hiba a liga kinyerésekor: {e}")
        liga_nev = 'Hiba a ligánál'

    try:
        datum_match = re.search(r'📆 .*? (\d+)(?:st|nd|rd|th)? at (\d{2}):(\d{2})\s*\(GMT\)', szoveg)
        if datum_match:
            nap = int(datum_match.group(1))
            ora = int(datum_match.group(2))
            perc = int(datum_match.group(3))
            ma = datetime.now()
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
                meccs_ido += timedelta(hours=1)
                honap_nev = meccs_ido.strftime("%B")
                honap_magyar = honapok.get(honap_nev, honap_nev)
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
        print(f"Dátum: {datum_str}")
    except Exception as e:
        print(f"Hiba a dátum kinyerésekor: {e}")
        datum_str = 'Hiba a dátumnál'

    try:
        prob = re.search(r'Probability[:\s]*([\d\.]+)%\s*\(([\d\.]+)\)', szoveg)
        if prob is None:
            raise ValueError("Nem található 'Probability' az üzenetben")
        valoszinuseg = prob.group(1) if prob else 'Nincs adat'
        fair_odds = prob.group(2) if prob else 'Nincs adat'
        print(f"Valószínűség: {valoszinuseg}, Fair odds: {fair_odds}")
    except Exception as e:
        print(f"Hiba a valószínűség kinyerésekor: {e}")
        valoszinuseg = 'Hiba'
        fair_odds = 'Hiba'

    try:
        odds = re.search(r'Odds[:\s]*([\d\.]+)', szoveg)
        if odds is None:
            raise ValueError("Nem található 'Odds' az üzenetben")
        odds_ertek = odds.group(1) if odds else 'Nincs adat'
        print(f"Odds: {odds_ertek}")
    except Exception as e:
        print(f"Hiba az odds kinyerésekor: {e}")
        odds_ertek = 'Hiba'

    try:
        value = re.search(r'Value[:\s]*([\d\.]+)%', szoveg)
        if value is None:
            raise ValueError("Nem található 'Value' az üzenetben")
        value_szazalek = '+' + value.group(1) if value else 'Nincs adat'
        print(f"Value: {value_szazalek}")
    except Exception as e:
        print(f"Hiba a value kinyerésekor: {e}")
        value_szazalek = 'Hiba'

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
        # Naplózzuk az összes beérkező üzenetet
        teljes_szoveg = event.message.message
        print(f"Új üzenet érkezett az OddAlertsBot-tól: {teljes_szoveg}")

        # Ellenőrizzük, hogy Value Bet-e az üzenet
        if "Value" not in teljes_szoveg:
            print("Nem Value Bet, kihagyom az üzenetet.")
            return

        print("Value Bet észlelve, folytatom a feldolgozást...")

        # Tipp típusának kinyerése
        try:
            tipp_tipus_match = re.search(r'⚙️ (.*?)\n', teljes_szoveg)
            if tipp_tipus_match is None:
                raise ValueError("Nem található '⚙️' az üzenetben")
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

        # Meccsek szétválasztása
        try:
            meccs_blokkok = re.split(r'(?=🆚 )', teljes_szoveg)
            print(f"Meccs blokkok száma: {len(meccs_blokkok)}")
        except Exception as e:
            print(f"Hiba a meccsek szétválasztásakor: {e}")
            await client.send_message(target_chat, f"⚠️ Hiba a meccsek szétválasztásakor: {e}")
            return

        # Blokk feldolgozása
        for blokk in meccs_blokkok:
            try:
                if '🆚' in blokk:
                    print(f"Blokk feldolgozása: {blokk}")
                    if 'Value' in blokk and 'Probability' in blokk:
                        print("Value és Probability megtalálva, formázás...")
                        formazott = format_tip(blokk, tipp_tipus)
                        print(f"Formázott üzenet: {formazott}")
                        print(f"Üzenet küldése a target_chat-be: {target_chat}")
                        await client.send_message(target_chat, formazott)
                        print("Üzenet sikeresen elküldve a cél csevegésbe.")
                    else:
                        print(f"Hiányos adatok a blokkban: {blokk}")
                        await client.send_message(target_chat, f"⚠️ Hiányos adatok a következő blokkban:\n{blokk}")
            except Exception as e:
                print(f"Hiba a blokk feldolgozása közben: {e}")
                await client.send_message(target_chat, f"⚠️ Hiba a blokk feldolgozása közben: {e}")

    except Exception as e:
        print(f"Hiba az üzenet teljes feldolgozása közben: {e}")
        try:
            await client.send_message(target_chat, f"⚠️ Hiba az üzenet feldolgozása közben: {e}")
        except Exception as send_error:
            print(f"Hiba az üzenet küldésekor a target_chat-be: {send_error}")

async def on_start():
    try:
        # Teszt üzenet küldése a bot indításakor
        print(f"Teszt üzenet küldése a target_chat-be: {target_chat}")
        await client.send_message(target_chat, "🔔 Bot elindult! Teszt üzenet a helyes működés ellenőrzéséhez.")
        print("Teszt üzenet sikeresen elküldve.")
    except Exception as e:
        print(f"Hiba a teszt üzenet küldésekor: {e}")

    # Ellenőrizzük, hogy a bot látja-e az OddAlertsBot csatornát
    try:
        print(f"Csatorna ellenőrzése: {source_channel}")
        channel = await client.get_entity(source_channel)
        print(f"Csatorna megtalálva: {channel.title} (ID: {channel.id})")
    except Exception as e:
        print(f"Hiba az OddAlertsBot csatorna elérésekor: {e}")

# Bot indítása újracsatlakozási logikával
async def main():
    try:
        print(f"Bot token: {bot_token}")
        await client.start(bot_token=bot_token)
        print("Sikeresen csatlakoztam a Telegramhoz!")
        await on_start()
        print("Bot fut, várakozás üzenetekre...")
        await client.run_until_disconnected()
    except Exception as e:
        print(f"Hiba történt, újracsatlakozás: {e}")
        await client.disconnect()
        await main()

# Futtassuk a ciklust
while True:
    try:
        client.loop.run_until_complete(main())
    except Exception as e:
        print(f"Végzetes hiba, újraindítás: {e}")
