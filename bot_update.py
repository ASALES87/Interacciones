import discord
import json
import os
from datetime import datetime, timedelta, timezone

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Conectado como {self.user}')
        channel = self.get_channel(CHANNEL_ID)
        ahora = datetime.now(timezone.utc)
        limite_3h = ahora - timedelta(hours=3)
        
        # --- 1. GESTIÓN DEL HISTORIAL (datos.json) ---
        if os.path.exists('datos.json'):
            with open('datos.json', 'r', encoding='utf-8') as f:
                try: historial = json.load(f)
                except: historial = {"messages": []}
        else:
            historial = {"messages": []}

        # --- 2. GESTIÓN DE LO RECIENTE (reciente.json) ---
        reciente = {"messages": []}

        # Leer mensajes (traemos suficientes para cubrir las 3h)
        async for message in channel.history(limit=200):
            if message.embeds:
                for embed in message.embeds:
                    msg_time = embed.timestamp.replace(tzinfo=timezone.utc) if embed.timestamp else ahora
                    nueva = {
                        "description": embed.description or "", 
                        "timestamp": str(msg_time)
                    }
                    
                    # Añadir al HISTORIAL si no existe (acumulativo)
                    if not any(m['embeds'][0]['description'] == nueva['description'] for m in historial['messages'] if m.get('embeds')):
                        historial["messages"].append({"embeds": [nueva]})
                    
                    # Añadir a RECIENTE si está dentro de las 3 horas
                    if msg_time >= limite_3h:
                        reciente["messages"].append({"embeds": [nueva]})

        # --- 3. GUARDAR AMBOS ARCHIVOS ---
        with open('datos.json', 'w', encoding='utf-8') as f:
            json.dump(historial, f, indent=4)
            
        with open('reciente.json', 'w', encoding='utf-8') as f:
            json.dump(reciente, f, indent=4)
            
        print("Archivos datos.json y reciente.json actualizados.")
        await self.close()

client = MyClient()
client.run(TOKEN)
