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
        self.active_connections: dict[int, list[WebSocket]] = {}  # workspace_id -> list of connections

    async def connect(self, websocket: WebSocket, workspace_id: int):
        await websocket.accept()
        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = []
        self.active_connections[workspace_id].append(websocket)

    def disconnect(self, websocket: WebSocket, workspace_id: int):
        if workspace_id in self.active_connections:
            self.active_connections[workspace_id].remove(websocket)
            if not self.active_connections[workspace_id]:
                del self.active_connections[workspace_id]

    async def broadcast_to_workspace(self, workspace_id: int, message: dict):
        if workspace_id in self.active_connections:
            for connection in self.active_connections[workspace_id]:
                await connection.send_json(message)

manager = ConnectionManager()

async def update_workspace_occupancy(workspace_id: int, available_spots: int):
    """Update workspace occupancy in database"""
    if not engine:
        return {"error": "Database connection not configured"}

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    UPDATE workspaces
                    SET available_spots = :spots
                    WHERE id = :id
                    RETURNING available_spots, total_spots
                """),
                {"id": workspace_id, "spots": available_spots}
            ).first()

            if result:
                return {
                    "workspace_id": workspace_id,
                    "availableSpots": result[0],
                    "totalSpots": result[1]
                }
            return {"error": "Workspace not found"}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

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

@app.websocket("/ws/{workspace_id}")
async def workspace_updates(websocket: WebSocket, workspace_id: int):
    await manager.connect(websocket, workspace_id)
    try:
        while True:
            data = await websocket.receive_json()

            # Validate workspace_id matches
            if data.get("workspace_id") != workspace_id:
                await websocket.send_json({"error": "Invalid workspace_id"})
                continue

            # Validate available_spots
            available_spots = data.get("available_spots")
            if not isinstance(available_spots, int):
                await websocket.send_json({"error": "Invalid available_spots value"})
                continue

            # Update database and get current state
            result = await update_workspace_occupancy(workspace_id, available_spots)

            if "error" in result:
                await websocket.send_json(result)
                continue

            # Broadcast to all connected clients for this workspace
            await manager.broadcast_to_workspace(workspace_id, result)

    except WebSocketDisconnect:
        manager.disconnect(websocket, workspace_id)
    except Exception as e:
        await websocket.send_json({"error": f"Unexpected error: {str(e)}"})
        manager.disconnect(websocket, workspace_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
