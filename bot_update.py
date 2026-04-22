import discord
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = os.getenv('TOKEN_ID')
raw_id = os.getenv('CHANNEL_ID')
CHANNEL_ID = int(raw_id) if raw_id else None
JSON_FILE = 'datos.json'

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'✅ Conectado como {self.user}')
        channel = self.get_channel(CHANNEL_ID)
        
        if not channel:
            print(f"❌ Error: No se encontró el canal {CHANNEL_ID}")
            await self.close()
            return

        # 1. CARGA SEGURA
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                try:
                    historial = json.load(f)
                except:
                    historial = {"messages": []}
        else:
            historial = {"messages": []}

        ids_viejos = {str(m['id']) for m in historial.get('messages', [])}
        
        # 2. EXTRACCIÓN DE NUEVOS MENSAJES
        nuevos_mensajes = []
        async for message in channel.history(limit=100):
            if str(message.id) not in ids_viejos:
                # Priorizar fecha del embed
                fecha_iso = message.created_at.isoformat()
                if message.embeds and message.embeds[0].timestamp:
                    fecha_iso = message.embeds[0].timestamp.isoformat()

                msg_data = {
                    "id": str(message.id),
                    "timestamp": fecha_iso,
                    "content": message.content,
                    "embeds": [e.to_dict() for e in message.embeds]
                }
                nuevos_mensajes.append(msg_data)

        # 3. FUSIÓN
        if nuevos_mensajes:
            historial['messages'].extend(nuevos_mensajes)
            historial['messages'].sort(key=lambda x: x['timestamp'])
            with open(JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(historial, f, indent=4, ensure_ascii=False)
            print(f"🚀 Añadidos {len(nuevos_mensajes)} mensajes nuevos.")
        else:
            print("⌛ No hay mensajes nuevos.")

        await self.close()

if TOKEN and CHANNEL_ID:
    client = MyClient(intents=discord.Intents.default())
    client.run(TOKEN)
else:
    print("❌ Faltan variables de entorno TOKEN_ID o CHANNEL_ID")
