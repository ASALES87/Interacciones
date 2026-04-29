import discord
import json
import os

# --- CONFIGURACIÓN ---
TOKEN = os.getenv("TOKEN_ID")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
FILE_PATH = 'datos.json'

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'✅ Conectado como {self.user}')
        channel = self.get_channel(CHANNEL_ID)
        
        if channel is None:
            print(f"❌ Error: No se encontró el canal {CHANNEL_ID}. Revisa permisos.")
            await self.close()
            return

        # 1. CARGAR DATOS EXISTENTES
        historial_mensajes = []
        if os.path.exists(FILE_PATH):
            try:
                with open(FILE_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    historial_mensajes = data.get('messages', [])
                print(f"📖 Historial cargado: {len(historial_mensajes)} mensajes previos.")
            except Exception as e:
                print(f"⚠️ No se pudo leer el historial: {e}")

        # Crear un set de IDs para evitar duplicados
        ids_existentes = {m.get('id') for m in historial_mensajes if 'id' in m}

        # 2. LEER MENSAJES DE DISCORD
        print(f"🔎 Escaneando canal: {channel.name}")
        mensajes_nuevos_contador = 0
        
        try:
            # limit=None para capturar TODO el historial del nuevo server
            async for message in channel.history(limit=None):
                # Solo guardamos si tiene embeds y no lo tenemos ya
                if message.embeds and message.id not in ids_existentes:
                    msg_dict = {
                        "id": message.id,
                        "content": message.content,
                        "timestamp": message.created_at.isoformat(),
                        "embeds": [
                            {
                                "description": e.description,
                                "title": e.title,
                                "timestamp": e.timestamp.isoformat() if e.timestamp else None
                            } for e in message.embeds if e.description
                        ]
                    }
                    historial_mensajes.append(msg_dict)
                    ids_existentes.add(message.id)
                    mensajes_nuevos_contador += 1
                    
                    if mensajes_nuevos_contador % 100 == 0:
                        print(f"📥 Descargando... {mensajes_nuevos_contador} mensajes nuevos.")
        
        except Exception as e:
            print(f"❌ Error durante la lectura: {e}")

        # 3. ORDENAR POR FECHA
        historial_mensajes.sort(key=lambda x: x['timestamp'])

        # 4. GUARDAR TODO
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump({"messages": historial_mensajes}, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Proceso completado.")
        print(f"✨ Mensajes nuevos añadidos: {mensajes_nuevos_contador}")
        print(f"📊 Total en el archivo histórico: {len(historial_mensajes)}")
        
        await self.close()

# Ejecutar el cliente (Self-bot debe usar su propio token)
client = MyClient()
client.run(TOKEN)
