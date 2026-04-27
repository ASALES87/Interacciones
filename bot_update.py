import discord
from discord.ext import commands
import json
import os

TOKEN = os.getenv("TOKEN_ID")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'✅ Conectado como {self.user}')
        channel = self.get_channel(CHANNEL_ID)
        
        if channel is None:
            print("❌ Error: No se encontró el canal. Revisa el CHANNEL_ID.")
            await self.close()
            return

        messages_data = []
        print(f"Reading messages from channel: {channel.name}")

        async for message in channel.history(limit=100):
            # Guardamos el mensaje completo para que el app.py lo procese
            msg_dict = {
                "content": message.content,
                "timestamp": message.created_at.isoformat(),
                "embeds": [
                    {
                        "description": e.description,
                        "title": e.title,
                        "timestamp": e.timestamp.isoformat() if e.timestamp else None
                    } for e in message.embeds
                ]
            }
            messages_data.append(msg_dict)

        with open('datos.json', 'w', encoding='utf-8') as f:
            json.dump({"messages": messages_data}, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Archivo datos.json generado con {len(messages_data)} mensajes.")
        await self.close()

client = MyClient()
client.run(TOKEN)
