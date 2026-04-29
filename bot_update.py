import discord
from discord.ext import commands
import json
import os

TOKEN = os.getenv("TOKEN_ID")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
FILE_PATH = 'datos.json'

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'✅ Conectado como {self.user}')
        channel = self.get_channel(CHANNEL_ID)
        
        if channel is None:
            print("❌ Error: No se encontró el canal. Revisa el CHANNEL_ID.")
            await self.close()
            return

        # 1. CARGAR DATOS EXISTENTES (EL HISTÓRICO)
        historial_mensajes = []
        if os.path.exists(FILE_PATH):
            try:
                with open(FILE_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    historial_mensajes = data.get('messages', [])
                print(f"📖 Historial cargado: {len(historial_mensajes)} mensajes previos.")
            except Exception as e:
                print(f"⚠️ No se pudo leer el historial (archivo corrupto o vacío): {e}")

        # Crear un set de IDs para evitar duplicados
        ids_existentes = {m.get('id') for m in historial_mensajes if 'id' in m}

        # 2. LEER MENSAJES NUEVOS DE DISCORD
        print(f"Reading messages from channel: {channel.name}")
        mensajes_nuevos_contador = 0
        
        # Quitamos el límite o lo subimos mucho para recuperar lo perdido
        # La primera vez leerá mucho, luego solo los nuevos
        async for message in channel.history(limit=None)
            if message.id not in ids_existentes:
                msg_dict = {
                    "id": message.id,  # IMPORTANTE guardar el ID para no duplicar
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
                historial_mensajes.append(msg_dict)
                ids_existentes.add(message.id)
                mensajes_nuevos_contador += 1

        # 3. ORDENAR POR FECHA (Antiguos primero, nuevos al final)
        historial_mensajes.sort(key=lambda x: x['timestamp'])

        # 4. GUARDAR TODO (ACUMULADO)
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump({"messages": historial_mensajes}, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Proceso completado.")
        print(f"✨ Mensajes nuevos añadidos: {mensajes_nuevos_contador}")
        print(f"📊 Total en el archivo histórico: {len(historial_mensajes)}")
        
        await self.close()

client = MyClient()
client.run(TOKEN)
