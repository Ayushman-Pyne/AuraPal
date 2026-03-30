import asyncio
import websockets
import json
import os
from flask import Flask, send_from_directory
from vosk import Model, KaldiRecognizer
from threading import Thread
  
# -----------------------------
# CONFIG
# -----------------------------
WS_PORT = 8888
HTTP_PORT = 8000
MODEL_PATH = "model"
  
# -----------------------------
# LOAD VOSK MODEL
# -----------------------------
recognizer = None
  
if os.path.exists(MODEL_PATH):
    print("Loading Vosk model...")
    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, 44100)
    print("✅ Vosk model loaded")
else:
    print("⚠️ Vosk model not found. Speech recognition disabled.")
  
# -----------------------------
# CLIENT STORAGE
# -----------------------------
connected_clients = set()
  
# -----------------------------
# SAFE SEND (NON-BLOCKING)
# -----------------------------
async def safe_send_all(data):
    dead = set()
  
    for ws in connected_clients:
        try:
            await ws.send(data)
        except:
            dead.add(ws)
  
    connected_clients.difference_update(dead)
  
# -----------------------------
# WEBSOCKET HANDLER
# -----------------------------
async def handler(websocket):
    print("Client connected")
    connected_clients.add(websocket)
  
    try:
        async for data in websocket:
  
            # 🔥 Non-blocking broadcast (fixes stopping issue)
            asyncio.create_task(safe_send_all(data))
  
            # 🔊 Speech recognition
            if recognizer:
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
  
                    if result.get("text"):
                        msg = json.dumps({
                            "type": "transcription",
                            "text": result["text"],
                            "isFinal": True
                        })
                        asyncio.create_task(safe_send_all(msg))
  
                else:
                    partial = json.loads(recognizer.PartialResult())
  
                    if partial.get("partial"):
                        msg = json.dumps({
                            "type": "transcription",
                            "text": partial["partial"],
                            "isFinal": False
                        })
                        asyncio.create_task(safe_send_all(msg))
  
            # 🧠 Prevent event loop blocking
            await asyncio.sleep(0)
  
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")
  
    finally:
        connected_clients.discard(websocket)
  
# -----------------------------
# FLASK SERVER
# -----------------------------
app = Flask(__name__, static_folder="static")
  
@app.route("/audio")
def audio():
    return app.send_static_file("audio_client.html")
  
@app.route("/js/<path:path>")
def js_files(path):
    return send_from_directory("static/js", path)
  
@app.route("/image/<path:path>")
def image_files(path):
    return send_from_directory("static/image", path)
  
# -----------------------------
# START SERVERS
# -----------------------------
async def start_ws():
    async with websockets.serve(handler, "0.0.0.0", WS_PORT):
        print(f"🌐 WebSocket running on ws://localhost:{WS_PORT}")
        await asyncio.Future()  # run forever
  
def start_http():
    print(f"🌐 HTTP server running on http://localhost:{HTTP_PORT}")
    app.run(host="0.0.0.0", port=HTTP_PORT)
  

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
   Thread(target=start_http, daemon=True).start()
asyncio.run(start_ws())