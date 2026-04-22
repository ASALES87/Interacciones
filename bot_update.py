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
        print(f'✅ Conectado como usuario: {self.user}')
        channel = self.get_channel(CHANNEL_ID)
        
        if not channel:
            # Si no lo encuentra por ID, intentamos buscarlo en todos los servidores
            channel = self.fetch_channel_fallback(CHANNEL_ID)
        
        if not channel:
            print(f"❌ Error: No tengo acceso al canal {CHANNEL_ID}")
            await self.close()
            return

        # Cargar historial existente
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                try:
                    historial = json.load(f)
                except:
                    historial = {"messages": []}
        else:
            historial = {"messages": []}

        ids_viejos = {str(m['id']) for m in historial.get('messages', [])}
        nuevos_mensajes = []

        print("📡 Leyendo historial del canal...")
        async for message in channel.history(limit=50):
            if str(message.id) not in ids_viejos:
                # Extraer timestamp (priorizar embed si existe)
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
            print(f"🚀 ¡Éxito! Añadidos {len(nuevos_mensajes)} puntos nuevos.")
        else:
            print("⌛ Todo al día. No hay kills nuevas.")

        await self.close()

    def fetch_channel_fallback(self, c_id):
        for guild in self.guilds:
            c = guild.get_channel(c_id)
            if c: return c
        return None

if TOKEN and CHANNEL_ID:
    # IMPORTANTE: En self-botting NO se usan intents
    client = MyClient()
    try:
        client.run(TOKEN)
    except discord.errors.LoginFailure:
        print("❌ Error: El Token de usuario no es válido.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
else:
    print("❌ Faltan variables TOKEN_ID o CHANNEL_ID")
