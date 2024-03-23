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
    "20:00": {"message": "🟢 Open **Sydney** 21:00", "status": "Close New York 22:00"},
    "05:00": {"message": "🔴 Close **Sydney** 06:00", "status": "Open London 09:00"},
    "00:00": {"message": "🟢 Open **Tokyo** 01:00", "status": "Close Sydney 06:00"},
    "09:00": {"message": "🔴 Close **Tokyo** 10:00", "status": "Open New York 13:00"},
    "08:00": {"message": "🟢 Open **London** 09:00", "status": "Close Tokyo 10:00"},
    "17:00": {"message": "🔴 Close **London** 17:00", "status": "Open Sydney 21:00"},
    "12:00": {"message": "🟢 Open **New York** 13:00", "status": "Close London 18:00"},
    "21:00": {"message": "🔴 Close **New York** 22:00", "status": "Open Tokyo 01:00"},
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
  await client.change_presence(activity=discord.Activity(
      type=discord.ActivityType.watching, name=status))

# Funkcja sprawdzająca i wysyłająca wiadomość o konkretnej godzinie
async def check_and_send_message():
    await client.wait_until_ready()
    target_user = await client.fetch_user(TARGET_USER_ID)

    # Wysyłanie wiadomości startowej przez webhook
    await send_webhook_message("Bot został uruchomiony.")

    while not client.is_closed():
        now = datetime.now().strftime("%H:%M")
        if now in MESSAGE_SCHEDULE:
            schedule = MESSAGE_SCHEDULE[now]
            message_content = schedule["message"]
            status_content = schedule["status"]
            await send_private_message(target_user, message_content)
            await change_bot_status(status_content)  # Zmiana statusu bota
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
