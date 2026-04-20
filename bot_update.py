import discord
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
JSON_FILE = 'datos.json'

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logueado como {self.user}')
        channel = self.get_channel(CHANNEL_ID)
        
        # 1. CARGAR DATOS EXISTENTES (El historial que subiste manualmente)
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, 'r', encoding='utf-8') as f:
                    historial = json.load(f)
            except:
                historial = {"messages": []}
        else:
            historial = {"messages": []}

        # Creamos un set de IDs para no repetir mensajes que ya tenemos
        ids_viejos = {m['id'] for m in historial.get('messages', [])}
        
        # 2. DESCARGAR MENSAJES RECIENTES DE DISCORD
        # He puesto un límite de 200, pero como filtramos IDs, no duplicará nada
        nuevos_mensajes = []
        async for message in channel.history(limit=200):
            if message.id not in ids_viejos:
                # Convertimos el mensaje a formato diccionario
                msg_data = {
                    "id": message.id,
                    "timestamp": message.created_at.isoformat(),
                    "content": message.content,
                    "embeds": [e.to_dict() for e in message.embeds]
                }
                nuevos_mensajes.append(msg_data)

        # 3. UNIR Y GUARDAR (Sin borrar lo antiguo)
        if nuevos_mensajes:
            # Añadimos los nuevos al principio o al final (aquí al final)
            historial['messages'].extend(nuevos_mensajes)
            
            # Ordenar por fecha para que el JSON esté limpio
            historial['messages'].sort(key=lambda x: x['timestamp'])

            with open(JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(historial, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Éxito: Se han añadido {len(nuevos_mensajes)} mensajes nuevos.")
        else:
            print("p No hay mensajes nuevos desde la última ejecución.")

        await self.close()

# Ejecutar el bot
if TOKEN and CHANNEL_ID:
    client = MyClient(intents=discord.Intents.default())
    client.run(TOKEN)
else:
    print("❌ Error: Faltan las variables de entorno TOKEN o CHANNEL_ID")
