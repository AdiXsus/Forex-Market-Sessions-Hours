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
    "20:00": "🟢 Open **Sydney** 21:00",
    "05:00": "🔴 Close **Sydney** 05:00",
    "00:00": "🟢 Open **Tokyo** 01:00",
    "09:00": "🔴 Close **Tokyo** 10:00",
    "08:00": "🟢 Open **London** 09:00",
    "17:00": "🔴 Close **London** 17:00",
    "12:00": "🟢 Open **New York** 12:00",
    "21:00": "🔴 Close **New York** 22:00",
    "00:58": "Test 1",
    "23:58": "Test 2",
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


# Funkcja sprawdzająca i wysyłająca wiadomość o konkretnej godzinie
async def check_and_send_message():
  await client.wait_until_ready()
  target_user = await client.fetch_user(TARGET_USER_ID)

  # Wysyłanie wiadomości startowej przez webhook
  await send_webhook_message("Bot został uruchomiony.")

  while not client.is_closed():
    now = datetime.now().strftime("%H:%M")
    if now in MESSAGE_SCHEDULE:
      message_content = MESSAGE_SCHEDULE[now]
      await send_private_message(target_user, message_content)
      await asyncio.sleep(
          60
      )  # Zabezpieczenie przed wielokrotnym wysłaniem w tej samej minucie
    await asyncio.sleep(30)  # Sprawdzanie co 30 sekund


# Event połączenia z Discordem
@client.event
async def on_ready():
  print(f'Zalogowano jako {client.user.name}')
  client.loop.create_task(check_and_send_message())


# Uruchomienie bota
client.run(os.getenv('TOKEN'))  # Pobierz token bota z zmiennych środowiskowych
