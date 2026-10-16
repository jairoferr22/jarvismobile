import os
import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Inicializa o servidor Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI(title="JARVIS Core Engine")

# Habilita CORS para permitir conexão da Vercel / Celular
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
async def status():
  return {'system': 'JARVIS Core', 'status': 'ONLINE', 'power': '100%'}


# Eventos Socket.IO
@sio.event
async def connect(sid, environ):
  print(f'⚡ [SISTEMA] Dispositivo conectado: {sid}')
  await sio.emit(
      'system_log',
      {'msg': 'Conexão segura estabelecida com o Jarvis Core.'},
      room=sid,
  )


@sio.event
async def disconnect(sid):
  print(f'🔻 [SISTEMA] Dispositivo desconectado: {sid}')


@sio.event
async def send_command(sid, data):
  comando = data.get('command', '')
  print(f'📥 [COMANDO MÓVEL RECEBIDO]: {comando}')

  # Log de processamento para o celular
  await sio.emit(
      'system_log',
      {'msg': f"Processando instrução: '{comando[:30]}...'"},
      room=sid,
  )

  # LÓGICA DO JARVIS (Aqui você pode conectar seus agentes, MT5, APIs, etc.)
  # Resposta simplificada de exemplo:
  resposta = (
      f"Comando '{comando}' recebido e processado com sucesso pelo Jarvis Core."
  )

  # Envia a resposta final para a interface web
  await sio.emit('jarvis_response', {'response': resposta}, room=sid)


# Junta o Socket.IO com o FastAPI
app_asgi = socketio.ASGIApp(sio, app)

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 8000))
  print(f'🚀 JARVIS Core rodando na porta {port}...')
  uvicorn.run(app_asgi, host='0.0.0.0', port=port)