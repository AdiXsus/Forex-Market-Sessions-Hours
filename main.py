import discord
import os
import asyncio
import aiohttp
from datetime import datetime
from keep_alive import keep_alive

# Ustawienia bota
WEBHOOK_URL = os.getenv(
    'WEBHOOK_URL')  # Pobierz URL webhooka z zmiennych środowiskowych
TARGET_USER_ID = int(os.getenv(
    'TARGET_USER_ID'))  # Pobierz ID użytkownika z zmiennych środowiskowych
MESSAGE_SCHEDULE = {  # Harmonogram wysyłania wiadomości (godzina: treść wiadomości)
    "21:00": {"message": "🟢 Open **Sydney** 23:00", "status": "🔴 Close New York 23:00"},
    "06:00": {"message": "🔴 Close **Sydney** 08:00", "status": "🟢 Open London 09:00"},
    "00:00": {"message": "🟢 Open **Tokyo** 02:00", "status": "🔴 Close Sydney 08:00"},
    "09:00": {"message": "🔴 Close **Tokyo** 11:00", "status": "🟢 Open New York 14:00"},
    "07:00": {"message": "🟢 Open **London** 09:00", "status": "🔴 Close Tokyo 11:00"},
    "16:00": {"message": "🔴 Close **London** 18:00", "status": "🟢 Open Sydney 23:00"},
    "12:00": {"message": "🟢 Open **New York** 14:00", "status": "🔴 Close London 18:00"},
    "21:00": {"message": "🔴 Close **New York** 23:00", "status": "🟢 Open Tokyo 02:00"},
}

# Inicjalizacja klienta Discord z odpowiednimi intencjami
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

# Funkcja do wysyłania wiadomości przez webhook
async def send_webhook_message(message):
    async with aiohttp.ClientSession() as session:
        async with session.post(WEBHOOK_URL, json={"content":
                                                       message}) as response:
            pass

# Funkcja do wysyłania wiadomości prywatnej
async def send_private_message(user, message):
    try:
        await user.send(message)
        print(f"Wysłano wiadomość do {user.name}")
    except discord.errors.Forbidden:
        print(f"Nie można wysłać wiadomości prywatnej do {user.name}")

# Funkcja zmieniająca status bota
async def change_bot_status(status):
  await client.change_presence(activity=discord.CustomActivity(
      type=discord.ActivityType.custom, name=status))

# Funkcja sprawdzająca i wysyłająca wiadomość o konkretnej godzinie
async def check_and_send_message():
  await client.wait_until_ready()
  target_user = await client.fetch_user(TARGET_USER_ID)

  # Wysyłanie wiadomości startowej przez webhook
  await send_webhook_message("Bot został uruchomiony.")

  while not client.is_closed():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
      
    # Sprawdzenie czy jest piątek i godzina jest odpowiednia
    if now.weekday() == 4 and now.hour == 21 and now.minute == 30:
      await send_private_message(target_user, "🔴 Market closes in 30 minutes.")

    # Sprawdzenie czy jest niedziela i godzina jest odpowiednia
    if now.weekday() == 6:
      if now.hour == 20 and now.minute == 59:
        await change_bot_status("🟢 Open Sydney 23:00")  # Zmiana statusu o 21:00 w niedzielę

      elif now.hour == 20 and now.minute == 45:
        await send_private_message(target_user, "🟢 Market opens soon.")
        await change_bot_status("🟢 Market opens soon.")

    # Sprawdzenie, czy obecny czas mieści się w zakresie czasowym blokady
    if ((now.weekday() == 4 and now.hour >= 21 and now.minute >= 35)
        or (now.weekday() == 5) or (now.weekday() == 6 and now.hour < 21)
        or (now.weekday() == 6 and now.hour == 20 and now.minute < 40)):
      await change_bot_status("⌛️ Marked Closed")
      await asyncio.sleep(60)  # Czekaj 60 sekund i sprawdź ponownie
      continue

    # Jeśli obecny czas pasuje do jednego z zaplanowanych czasów, wyślij wiadomość
    if current_time in MESSAGE_SCHEDULE:
      schedule = MESSAGE_SCHEDULE[current_time]
      message_content = schedule["message"]
      status_content = schedule["status"]
      await send_private_message(target_user, message_content)
      await change_bot_status(status_content)  # Zmiana statusu bota

    await asyncio.sleep(60)  # Sprawdzanie co minutę

# Event połączenia z Discordem
@client.event
async def on_ready():
  print(f'Zalogowano jako {client.user.name}')
  await client.change_presence(activity=discord.CustomActivity(
      name="🔎 Checking Market..."))
  print("Zmieniono status bota.")
  client.loop.create_task(check_and_send_message())

@client.event
async def on_error(event, *args, **kwargs):
  print('Błąd:', args, kwargs)


@client.event
async def on_disconnect():
  print('Bot został rozłączony')


@client.event
async def on_reconnect():
  print('Bot próbuje ponownie połączyć się z Discord.')


@client.event
async def on_invalidated():
  print('Token bota został zinvalidowany.')

keep_alive()

# Uruchomienie bota
client.run(os.getenv('TOKEN'))  # Pobierz token bota z zmiennych środowiskowych
