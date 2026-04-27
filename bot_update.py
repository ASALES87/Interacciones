import discord
import json
import os
from datetime import datetime

TOKEN = os.getenv('TOKEN_ID')
raw_id = os.getenv('CHANNEL_ID')
CHANNEL_ID = int(raw_id) if raw_id else None
JSON_FILE = 'datos.json'

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'✅ Conectado como: {self.user}')
        channel = self.get_channel(CHANNEL_ID)
        
        if not channel:
            print(f"❌ Error: Canal {CHANNEL_ID} no encontrado")
            await self.close()
            return

        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                try: historial = json.load(f)
                except: historial = {"messages": []}
        else:
            historial = {"messages": []}

        ids_viejos = {str(m['id']) for m in historial.get('messages', [])}
        nuevos_mensajes = []

        print("📡 Escaneando mensajes...")
        async for message in channel.history(limit=100):
            if str(message.id) not in ids_viejos:
                fecha_iso = message.created_at.isoformat()
                if message.embeds and message.embeds[0].timestamp:
                    fecha_iso = message.embeds[0].timestamp.isoformat()

                nuevos_mensajes.append({
                    "id": str(message.id),
                    "timestamp": fecha_iso,
                    "content": message.content,
                    "embeds": [e.to_dict() for e in message.embeds]
                })

        if nuevos_mensajes:
            historial['messages'].extend(nuevos_mensajes)
            historial['messages'].sort(key=lambda x: x['timestamp'])
            with open(JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(historial, f, indent=4, ensure_ascii=False)
            print(f"🚀 {len(nuevos_mensajes)} kills nuevas guardadas.")
        else:
            print("⌛ No hay nada nuevo.")

        await self.close()

if TOKEN and CHANNEL_ID:
    client = MyClient()
    client.run(TOKEN)
