import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('.env.production')

app = FastAPI()
application = app

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL) if DATABASE_URL else None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}

@app.get("/workspaces")
async def get_workspaces():
    if not engine:
        return {"error": "Database connection not configured"}
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT id, name, address, latitude, longitude, available_spots, total_spots 
                FROM workspaces
            """))
            workspaces = [
                {
                    "id": row[0],
                    "name": row[1],
                    "address": row[2],
                    "latitude": float(row[3]),
                    "longitude": float(row[4]),
                    "availableSpots": row[5],
                    "totalSpots": row[6]
                }
                for row in result
            ]
            return {"workspaces": workspaces}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

@app.get("/workspace/{workspace_id}/occupancy")
async def get_workspace_occupancy(workspace_id: int):
    if not engine:
        return {"error": "Database connection not configured"}
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT available_spots, total_spots FROM workspaces WHERE id = :id"),
                {"id": workspace_id}
            ).first()
            
            if result:
                return {
                    "availableSpots": result[0],
                    "totalSpots": result[1]
                }
            return {"error": "Workspace not found"}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
