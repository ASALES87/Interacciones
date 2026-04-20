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
        print(f'Conectado como {self.user}')
        channel = self.get_channel(CHANNEL_ID)
        
        # --- CARGA SEGURA ---
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                try:
                    historial = json.load(f)
                    print(f"✅ Historial cargado: {len(historial.get('messages', []))} registros previos.")
                except:
                    historial = {"messages": []}
        else:
            print("⚠️ No se encontró datos.json, creando uno nuevo.")
            historial = {"messages": []}

        ids_viejos = {str(m['id']) for m in historial.get('messages', [])}
        
        # --- EXTRACCIÓN ---
        nuevos_mensajes = []
        async for message in channel.history(limit=200):
            # Comparamos IDs como strings para evitar errores
            if str(message.id) not in ids_viejos:
                msg_data = {
                    "id": str(message.id),
                    "timestamp": message.created_at.isoformat(),
                    "content": message.content,
                    "embeds": [e.to_dict() for e in message.embeds]
                }
                nuevos_mensajes.append(msg_data)

        # --- FUSIÓN ---
        if nuevos_mensajes:
            historial['messages'].extend(nuevos_mensajes)
            # Ordenar por fecha (el más viejo arriba)
            historial['messages'].sort(key=lambda x: x['timestamp'])

            with open(JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(historial, f, indent=4, ensure_ascii=False)
            print(f"🚀 Éxito: {len(nuevos_mensajes)} mensajes nuevos añadidos.")
        else:
            print("⌛ No hay nada nuevo que añadir.")

        await self.close()

client = MyClient(intents=discord.Intents.default())
client.run(TOKEN)
