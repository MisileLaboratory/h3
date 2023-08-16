from fastapi import FastAPI, WebSocket, HTTPException, status, Header
from starlette.endpoints import WebSocketEndpoint
from pymongo import MongoClient
from dotenv import load_dotenv

from os import environ, getenv
from typing import Annotated
from urllib.parse import quote_plus

envs = environ
load_dotenv()

def get_env(a: str):
    return getenv(a) if envs[a] is None else envs[a]

app = FastAPI()
db = MongoClient(quote_plus(get_env("MONGO_URI")))["minecrafter"]
websocketlist = {
    "reactor": [],
    "turbine": [],
    "matrix": [],
    "fuelgen": []
}

@app.websocket_route("/data/{st_type}")
class DataWebsocket(WebSocketEndpoint):
    async def on_connect(self, ws: WebSocket, st_type: str):
        self.st_type = st_type
        await ws.accept()
        websocketlist[st_type].append(ws)

    async def on_receive(self, _: WebSocket, data: str):
        print(data)
        db[self.st_type].insert_one(data)

    async def on_disconnect(self, ws: WebSocket, close_code: int):
        print(f"{ws.client.host} disconnected with {close_code}")
        websocketlist[self.st_type].remove(ws)

@app.post("/reacting-react/status/{r_status}")
def status_end(r_status: int):
    if r_status not in [0, 1]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    for ws in websocketlist["reactor"]:
        ws.send_text(f"set status {r_status}")

@app.post("/reacting-react/set-amount")
def amount_end(
    am_type: Annotated[str | None, Header()] = None,
    st_type: Annotated[str | None, Header()] = None,
    amount: Annotated[int | None, Header()] = None
):
    for ws in websocketlist[st_type]:
        ws.send_text(f"set {am_type} {amount}")