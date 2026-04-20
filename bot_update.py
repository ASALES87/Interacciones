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
        
        # 1. Definir el límite de tiempo (últimas 3 horas)
        # Usamos timezone.utc para evitar errores de desfase horario
        limite_tiempo = datetime.now(timezone.utc) - timedelta(hours=3)
        
        # 2. Cargar o crear datos.json
        if os.path.exists('datos.json'):
            with open('datos.json', 'r', encoding='utf-8') as f:
                try: 
                    data = json.load(f)
                except: 
                    data = {"messages": []}
        else:
            data = {"messages": []}

        # 3. Leer mensajes y filtrar por tiempo
        # Ponemos un límite alto (ej. 200) por seguridad, pero el filtro de tiempo manda
        async for message in channel.history(limit=200, after=limite_tiempo):
            if message.embeds:
                for embed in message.embeds:
                    nueva = {
                        "description": embed.description or "", 
                        "timestamp": str(embed.timestamp or "")
                    }
                    
                    # Evitar duplicados antes de añadir
                    if not any(m['embeds'][0]['description'] == nueva['description'] for m in data['messages'] if m.get('embeds')):
                        data["messages"].append({"embeds": [nueva]})

        # 4. Guardar los resultados
        with open('datos.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        print(f"Sincronización completada. Se han revisado mensajes desde: {limite_tiempo}")
        await self.close()

client = MyClient()
client.run(TOKEN)
