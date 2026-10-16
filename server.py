import os
import socketio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai

# Inicializa o cliente do Gemini (ele lê automaticamente a variável de ambiente GEMINI_API_KEY)
# Para configurar sua chave no Render: acesse o painel do seu Web Service > Environment > Add Environment Variable (GEMINI_API_KEY)
client = genai.Client()

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = FastAPI(title="JARVIS Core Engine")

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


@sio.event
async def connect(sid, environ):
  print(f'⚡ [SISTEMA] Dispositivo conectado: {sid}')
  await sio.emit(
      'system_log',
      {'msg': 'Conexão segura estabelecida com o Jarvis Core.'},
      room=sid,
  )


@sio.event
async def send_command(sid, data):
  comando = data.get('command', '')
  print(f'📥 [COMANDO MÓVEL]: {comando}')

  await sio.emit(
      'system_log',
      {'msg': f"Processando instrução via IA: '{comando[:30]}...'"},
      room=sid,
  )

  try:
    # Chamada real usando o Gemini SDK
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=(
            'Você é o JARVIS, assistente pessoal avançado do Jairo. Seja'
            f' direto, técnico e prestativo. Instrução: {comando}'
        ),
    )
    resposta_jarvis = response.text
  except Exception as e:
    resposta_jarvis = f'Erro ao processar com o Gemini: {str(e)}'

  await sio.emit('jarvis_response', {'response': resposta_jarvis}, room=sid)


app_asgi = socketio.ASGIApp(sio, app)

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 8000))
  uvicorn.run(app_asgi, host='0.0.0.0', port=port)